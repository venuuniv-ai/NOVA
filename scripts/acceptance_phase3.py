"""Exercise persisted local proactive approval and simulated execution with the fixture clock."""
import argparse
import json
import urllib.request
from uuid import uuid4


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--verify-task")
    args = parser.parse_args()

    def call(path, payload=None):
        request = urllib.request.Request(args.base_url + path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Content-Type": "application/json", "X-Correlation-ID": str(uuid4())})
        with urllib.request.urlopen(request, timeout=20) as response:
            assert response.headers["X-Correlation-ID"]
            return json.load(response)

    devices = {d["type"]: d["id"] for d in call("/api/v1/devices")}
    if args.verify_task:
        task_id = args.verify_task
        proposals = call(f"/api/v1/tasks/{task_id}/proposals")
        assert len(proposals) == 1
        proposal = proposals[0]
    else:
        task = call("/api/v1/tasks", {"title": "Architecture Review — Phase 3 acceptance", "origin_device_id": devices["DESKTOP"]})
        task_id = task["id"]
        event = {"task_id": task_id, "idempotency_key": str(uuid4()), "event_type": "TIME_TICK"}
        evaluation = call("/api/v1/proactive/evaluate", event)
        assert evaluation["status"] == "SURFACED"
        proposal = evaluation["proposal"]
        assert call("/api/v1/proactive/evaluate", event)["proposal"]["id"] == proposal["id"]
        assert proposal["status"] == "PENDING_APPROVAL"
        assert proposal["policy_decision"] == "REQUIRE_APPROVAL"
    situation = proposal["situation"]
    assert situation["current_time"].startswith("2026-10-14T13:31")
    assert (situation["minutes_available"], situation["travel_minutes"], situation["lateness_minutes"]) == (29, 35, 6)
    assert "2:06 PM" in proposal["content"]
    proposal_id, trace_id = proposal["id"], proposal["trace_id"]
    if not args.verify_task:
        approve = {"idempotency_key": str(uuid4())}
        approved = call(f"/api/v1/proposals/{proposal_id}/approve", approve)
        assert approved["approval"]["payload_hash"] == proposal["payload_hash"]
        assert call(f"/api/v1/proposals/{proposal_id}/approve", approve)["approval"]["id"] == approved["approval"]["id"]
        execution = call(f"/api/v1/proposals/{proposal_id}/execute", {"idempotency_key": str(uuid4())})
        replay = call(f"/api/v1/proposals/{proposal_id}/execute", {"idempotency_key": str(uuid4())})
        assert execution["execution"]["id"] == replay["execution"]["id"]
        first_handoff = None
        for source, target in [("DESKTOP", "WEARABLE"), ("WEARABLE", "MOBILE")]:
            payload = {"source_device_id": devices[source], "target_device_id": devices[target], "idempotency_key": str(uuid4())}
            first_handoff = first_handoff or payload
            moved = call(f"/api/v1/tasks/{task_id}/handoff", payload)
            assert moved["task"]["id"] == task_id and moved["task"]["current_device_id"] == devices[target]
            current = call(f"/api/v1/proposals/{proposal_id}")["proposal"]
            assert current["trace_id"] == trace_id and current["task_id"] == task_id
        assert call(f"/api/v1/tasks/{task_id}/handoff", first_handoff)["replayed"]
    result = call(f"/api/v1/proposals/{proposal_id}")
    assert result["proposal"]["status"] == "EXECUTED"
    assert result["approval"]["payload_hash"] == result["proposal"]["payload_hash"]
    assert result["execution"]["status"] == "DONE"
    assert result["execution"]["receipt"]["external_message_sent"] is False
    assert result["execution"]["receipt"]["disclosure"] == "SIMULATED / NOT SENT"
    audit = call(f"/api/v1/tasks/{task_id}/audit-events")
    assert len(audit) == 4 and all(a["trace_id"] == trace_id for a in audit)
    assert call(f"/api/v1/tasks/{task_id}")["current_device_id"] == devices["MOBILE"]
    print(json.dumps({"result": "PASS", "task_id": task_id, "proposal_id": proposal_id,
        "trace_id": trace_id, "execution_id": result["execution"]["id"], "arithmetic": "29 / 35 / +6",
        "disclosure": "SIMULATED / NOT SENT", "current_device": "MOBILE", "audit_events": len(audit),
        "restart_verification": bool(args.verify_task)}, indent=2))


if __name__ == "__main__":
    main()
