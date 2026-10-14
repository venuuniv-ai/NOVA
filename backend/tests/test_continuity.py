from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.database import SessionLocal, engine
from app.main import app
from app.models import Task, TaskEvent
from app.seed import seed_demo


def handoff(client, task_id, devices, source="DESKTOP", target="WEARABLE", key="first-handoff"):
    return client.post(
        f"/api/v1/tasks/{task_id}/handoff",
        json={
            "source_device_id": devices[source],
            "target_device_id": devices[target],
            "idempotency_key": key,
        },
    )


def history(client, task_id):
    response = client.get(f"/api/v1/tasks/{task_id}/events")
    assert response.status_code == 200
    return response.json()


def test_creation_persisted_and_created_event(client, devices, task):
    assert task["current_device_id"] == devices["DESKTOP"]
    assert task["origin_device_id"] == devices["DESKTOP"]
    assert task["status"] == "ACTIVE"
    assert task["created_at"] and task["updated_at"]
    with SessionLocal() as session:
        persisted = session.get(Task, task["id"])
        assert persisted.title == task["title"]
        assert session.scalar(select(func.count()).select_from(Task)) == 1
    events = history(client, task["id"])
    assert len(events) == 1
    assert events[0]["event_type"] == "TASK_CREATED"
    assert events[0]["target_device_id"] == devices["DESKTOP"]
    assert events[0]["source_device_id"] is None
    assert events[0]["sequence"] == 1
    assert events[0]["metadata"]["correlation_id"]
    assert client.get("/api/v1/tasks").json()[0]["id"] == task["id"]


def test_full_acceptance_refresh_and_old_retry(client, devices, task):
    task_id = task["id"]
    first = handoff(client, task_id, devices)
    assert first.status_code == 200
    assert first.json()["task"]["id"] == task_id
    assert first.json()["task"]["current_device_id"] == devices["WEARABLE"]
    assert not first.json()["replayed"]
    assert client.get(f"/api/v1/tasks/{task_id}").json()["current_device_id"] == devices["WEARABLE"]

    second = handoff(client, task_id, devices, "WEARABLE", "MOBILE", "second-handoff")
    assert second.status_code == 200
    assert second.json()["task"]["id"] == task_id
    assert second.json()["task"]["current_device_id"] == devices["MOBILE"]
    assert client.get(f"/api/v1/tasks/{task_id}").json()["current_device_id"] == devices["MOBILE"]
    retry = handoff(client, task_id, devices)
    assert retry.status_code == 200
    assert retry.json()["replayed"]
    assert retry.json()["event"]["id"] == first.json()["event"]["id"]
    assert retry.json()["task"]["current_device_id"] == devices["MOBILE"]
    assert [e["event_type"] for e in history(client, task_id)] == [
        "TASK_CREATED",
        "HANDOFF_DESKTOP_TO_WEARABLE",
        "HANDOFF_WEARABLE_TO_MOBILE",
    ]
    with SessionLocal() as session:
        assert session.scalar(select(func.count()).select_from(Task)) == 1
        assert session.scalar(select(func.count()).select_from(TaskEvent)) == 3


def test_same_key_exact_retry_is_idempotent(client, devices, task):
    first = handoff(client, task["id"], devices).json()
    retry = handoff(client, task["id"], devices).json()
    assert first["event"]["id"] == retry["event"]["id"]
    assert first["task"]["updated_at"] == retry["task"]["updated_at"]
    assert retry["replayed"]
    assert len(history(client, task["id"])) == 2


def test_same_key_different_payload_conflicts(client, devices, task):
    assert handoff(client, task["id"], devices).status_code == 200
    response = handoff(client, task["id"], devices, "WEARABLE", "MOBILE")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"
    assert len(history(client, task["id"])) == 2
    assert (
        client.get(f"/api/v1/tasks/{task['id']}").json()["current_device_id"] == devices["WEARABLE"]
    )


def test_key_is_scoped_to_task(client, devices, task):
    other = client.post(
        "/api/v1/tasks",
        json={
            "title": "Another task",
            "origin_device_id": devices["DESKTOP"],
        },
    ).json()
    assert handoff(client, task["id"], devices).status_code == 200
    assert handoff(client, other["id"], devices).status_code == 200


def test_invalid_device_does_not_mutate(client, devices, task):
    response = client.post(
        f"/api/v1/tasks/{task['id']}/handoff",
        json={
            "source_device_id": devices["DESKTOP"],
            "target_device_id": str(uuid4()),
            "idempotency_key": "invalid-device",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_DEVICE"
    assert len(history(client, task["id"])) == 1
    assert (
        client.get(f"/api/v1/tasks/{task['id']}").json()["current_device_id"] == devices["DESKTOP"]
    )


@pytest.mark.parametrize("target", ["DESKTOP", "MOBILE"])
def test_invalid_transition(client, devices, task, target):
    response = handoff(client, task["id"], devices, target=target)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_TRANSITION"
    assert len(history(client, task["id"])) == 1


def test_stale_source(client, devices, task):
    assert handoff(client, task["id"], devices).status_code == 200
    response = handoff(client, task["id"], devices, key="new-key")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "STALE_SOURCE"
    assert len(history(client, task["id"])) == 2


def test_mobile_has_no_next_transition(client, devices, task):
    handoff(client, task["id"], devices)
    handoff(client, task["id"], devices, "WEARABLE", "MOBILE", "second")
    assert handoff(client, task["id"], devices, "MOBILE", "DESKTOP", "third").status_code == 409
    assert len(history(client, task["id"])) == 3


def test_persistence_across_app_lifecycle(client, devices, task):
    handoff(client, task["id"], devices)
    engine.dispose()  # Discard existing pool, as an application restart would.
    with TestClient(app) as fresh_client:
        response = fresh_client.get(f"/api/v1/tasks/{task['id']}")
        assert response.status_code == 200
        assert response.json()["current_device_id"] == devices["WEARABLE"]
        assert len(history(fresh_client, task["id"])) == 2


def test_concurrent_same_key_one_event(client, devices, task):
    def send(_):
        return handoff(client, task["id"], devices, key="concurrent")

    with ThreadPoolExecutor(max_workers=4) as executor:
        responses = list(executor.map(send, range(4)))
    assert all(response.status_code == 200 for response in responses)
    assert sum(not response.json()["replayed"] for response in responses) == 1
    assert len({response.json()["event"]["id"] for response in responses}) == 1
    assert len(history(client, task["id"])) == 2


def test_concurrent_different_keys_only_one_transition(client, devices, task):
    def send(index):
        return handoff(client, task["id"], devices, key=f"race-{index}")

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(send, range(2)))
    assert sorted(response.status_code for response in responses) == [200, 409]
    assert len(history(client, task["id"])) == 2


@pytest.mark.parametrize("key", ["", "contains space", "x" * 129])
def test_invalid_idempotency_key(client, devices, task, key):
    assert handoff(client, task["id"], devices, key=key).status_code == 422
    assert len(history(client, task["id"])) == 1


def test_missing_key(client, devices, task):
    response = client.post(
        f"/api/v1/tasks/{task['id']}/handoff",
        json={
            "source_device_id": devices["DESKTOP"],
            "target_device_id": devices["WEARABLE"],
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize("title", ["", "   ", "x" * 241])
def test_invalid_title(client, devices, title):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": title,
            "origin_device_id": devices["DESKTOP"],
        },
    )
    assert response.status_code == 422


def test_invalid_creation_origin(client, devices):
    for device in (devices["MOBILE"], str(uuid4())):
        response = client.post("/api/v1/tasks", json={"title": "Task", "origin_device_id": device})
        assert response.status_code == 422


def test_invalid_uuid_and_missing_task(client):
    assert client.get("/api/v1/tasks/not-a-uuid").status_code == 422
    assert client.get(f"/api/v1/tasks/{uuid4()}").status_code == 404
    assert client.get(f"/api/v1/tasks/{uuid4()}/events").status_code == 404


def test_devices_seed_idempotently_and_health(client):
    seed_demo()
    seed_demo()
    response = client.get("/api/v1/devices")
    assert [device["type"] for device in response.json()] == ["DESKTOP", "WEARABLE", "MOBILE"]
    assert client.get("/health/live").json()["status"] == "alive"
    assert client.get("/health/ready").json()["status"] == "ready"


def test_correlation_ids_success_error_and_validation(client, devices):
    for path in ("/api/v1/devices", f"/api/v1/tasks/{uuid4()}", "/api/v1/tasks/invalid"):
        response = client.get(path, headers={"X-Correlation-ID": "test-correlation"})
        assert response.headers["X-Correlation-ID"] == "test-correlation"
        if response.status_code >= 400:
            assert response.json()["correlation_id"] == "test-correlation"
    response = client.get("/api/v1/devices", headers={"X-Correlation-ID": " " * 70})
    assert len(response.headers["X-Correlation-ID"]) == 36


def test_pagination_validation(client, task):
    assert client.get("/api/v1/tasks?limit=1").json()[0]["id"] == task["id"]
    assert client.get("/api/v1/tasks?offset=1").json() == []
    assert client.get("/api/v1/tasks?limit=1000").status_code == 422
