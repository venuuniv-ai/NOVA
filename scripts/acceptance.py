"""Exercise the real local REST API; never calls a model or paid service."""
import argparse
import json
import urllib.request
from uuid import uuid4

TITLE = "Find somewhere for dinner with Sarah tomorrow after my meeting."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--verify-task", help="Verify an existing completed acceptance task after restart.")
    args = parser.parse_args()

    def call(path, payload=None):
        request = urllib.request.Request(
            args.base_url + path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Content-Type": "application/json", "X-Correlation-ID": str(uuid4())},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            assert response.headers["X-Correlation-ID"]
            return json.load(response)

    devices = {device["type"]: device["id"] for device in call("/api/v1/devices")}
    assert len(devices) == 3
    if args.verify_task:
        task_id = args.verify_task
    else:
        task = call("/api/v1/tasks", {
            "title": TITLE,
            "description": "Phase 1 API acceptance test. Real PostgreSQL state.",
            "origin_device_id": devices["DESKTOP"],
        })
        task_id = task["id"]
        assert task["current_device_id"] == devices["DESKTOP"]
        first_payload = {
            "source_device_id": devices["DESKTOP"],
            "target_device_id": devices["WEARABLE"],
            "idempotency_key": str(uuid4()),
        }
        first = call(f"/api/v1/tasks/{task_id}/handoff", first_payload)
        assert first["task"]["id"] == task_id and not first["replayed"]
        assert first["task"]["current_device_id"] == devices["WEARABLE"]
        assert call(f"/api/v1/tasks/{task_id}")["current_device_id"] == devices["WEARABLE"]
        second = call(f"/api/v1/tasks/{task_id}/handoff", {
            "source_device_id": devices["WEARABLE"],
            "target_device_id": devices["MOBILE"],
            "idempotency_key": str(uuid4()),
        })
        assert second["task"]["id"] == task_id and not second["replayed"]
        retry = call(f"/api/v1/tasks/{task_id}/handoff", first_payload)
        assert retry["replayed"] and retry["event"]["id"] == first["event"]["id"]
        assert retry["task"]["current_device_id"] == devices["MOBILE"]

    task = call(f"/api/v1/tasks/{task_id}")
    events = call(f"/api/v1/tasks/{task_id}/events")
    assert task["id"] == task_id
    assert task["current_device_id"] == devices["MOBILE"]
    assert [event["event_type"] for event in events] == [
        "TASK_CREATED", "HANDOFF_DESKTOP_TO_WEARABLE", "HANDOFF_WEARABLE_TO_MOBILE",
    ]
    print(json.dumps({"result": "PASS", "task_id": task_id, "current_device": "MOBILE",
                      "event_count": len(events), "restart_verification": bool(args.verify_task)}, indent=2))


if __name__ == "__main__":
    main()
