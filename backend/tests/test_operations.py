"""Phase 11 metadata pagination and real authentication; no model calls."""

import json
from uuid import uuid4

import pytest
from sqlalchemy import select
from test_phase8 import identities as identities

from app.database import SessionLocal
from app.events.models import Inbox, Job, Outbox
from app.seed import DEMO_USER_ID


def history(task_id, count=7):
    with SessionLocal.begin() as session:
        for _ in range(count):
            e = Outbox(
                user_id=DEMO_USER_ID,
                task_id=task_id,
                event_type="ContextEvent.changed",
                payload={"private": "DO_NOT_EXPOSE_SOURCE_OR_PROVIDER_BODY"},
            )
            session.add(e)
            session.flush()
            session.add(
                Job(event_id=e.id, task_id=task_id, user_id=DEMO_USER_ID, state="DEAD", attempts=1)
            )
            session.add(Inbox(event_id=e.id, consumer="proactive"))


def test_independent_pages_and_snapshot_exclude_appended_events(client, task):
    history(task["id"])
    url = f"/api/v1/operations/tasks/{task['id']}"
    first = client.get(url, params={"limit": 2}).json()
    ceiling = first["page"]["through"]
    history(task["id"], 1)
    for key, cursor in [("events", "next_after"), ("jobs", "next_jobs_after")]:
        page, rows = first, list(first[key])
        while page["page"][cursor] is not None:
            params = {
                "limit": 2,
                "through": ceiling,
                "after" if key == "events" else "jobs_after": page["page"][cursor],
            }
            response = client.get(url, params=params)
            assert response.status_code == 200
            page = response.json()
            rows.extend(page[key])
        sequences = [x["sequence"] for x in rows]
        assert sequences == sorted(set(sequences))
        assert max(sequences) <= ceiling
        assert len(rows) == (9 if key == "events" else 7)
    assert client.get(url).json()["page"]["through"] > ceiling
    assert "DO_NOT_EXPOSE" not in json.dumps(first)
    assert first["jobs"][0]["diagnostic"] == "TERMINAL_JOB_FAILURE"


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"after": -1},
        {"jobs_after": -1},
        {"through": -1},
        {"after": 9223372036854775808},
        {"jobs_after": 9223372036854775808},
        {"through": 9223372036854775808},
    ],
)
def test_invalid_page_bounds(client, task, params):
    assert client.get(f"/api/v1/operations/tasks/{task['id']}", params=params).status_code == 422


def test_empty_and_bounded_query_count(client, task):
    from sqlalchemy import event

    from app.database import engine

    history(task["id"], 110)
    statements = []

    def capture(*args):
        statements.append(args[2])

    event.listen(engine, "before_cursor_execute", capture)
    try:
        response = client.get(f"/api/v1/operations/tasks/{task['id']}", params={"limit": 100})
    finally:
        event.remove(engine, "before_cursor_execute", capture)
    assert response.status_code == 200
    assert len(response.json()["events"]) == 100
    assert len(response.json()["jobs"]) == 100
    assert len(statements) <= 10  # Batch inbox read; never one query per event.
    empty = client.get(f"/api/v1/operations/tasks/{task['id']}", params={"through": 0}).json()
    assert empty["events"] == empty["jobs"] == []
    assert empty["page"]["next_after"] is None
    assert empty["page"]["next_jobs_after"] is None


def test_authenticated_owner_foreign_owner_role_and_revocation(client, identities):
    from app.security.models import Identity

    a, b, viewer = identities
    created = client.post(
        "/api/v1/tasks",
        headers=a["headers"],
        json={
            "title": "Private operations",
            "origin_device_id": str(a["device_id"]),
        },
    ).json()
    url = f"/api/v1/operations/tasks/{created['id']}"
    assert client.get(url, headers=a["headers"]).status_code == 200
    assert client.get(url).status_code == 401
    assert client.get(url, headers=b["headers"]).status_code == 403
    assert client.get(url, headers=viewer["headers"]).status_code == 403
    with SessionLocal.begin() as session:
        foreign = session.scalar(select(Identity).where(Identity.user_id == b["user_id"]))
        foreign.roles = ["owner", "operator"]
    assert client.get(url, headers=b["headers"]).status_code == 404
    with SessionLocal.begin() as session:
        owner = session.scalar(select(Identity).where(Identity.user_id == a["user_id"]))
        owner.enabled = False
    assert client.get(url, headers=a["headers"]).status_code == 401
    assert (
        client.get(f"/api/v1/operations/tasks/{uuid4()}", headers=b["headers"]).status_code == 404
    )
