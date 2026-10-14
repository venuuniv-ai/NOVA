"""Real local Phase 2 acceptance: no paid API, fixture provider, persisted intelligence."""
import argparse
import json
import urllib.request
from uuid import uuid4

TITLE = "Find somewhere for dinner with Sarah tomorrow after my meeting."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--verify-task", help="Verify completed Phase 2 state after service restart.")
    args = parser.parse_args()

    def call(path, payload=None):
        request = urllib.request.Request(args.base_url + path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Content-Type": "application/json", "X-Correlation-ID": str(uuid4())})
        with urllib.request.urlopen(request, timeout=20) as response:
            assert response.headers["X-Correlation-ID"]
            return json.load(response)

    devices = {device["type"]: device["id"] for device in call("/api/v1/devices")}
    if args.verify_task:
        task_id = args.verify_task
    else:
        task = call("/api/v1/tasks", {"title": TITLE, "origin_device_id": devices["DESKTOP"]})
        task_id = task["id"]
        assert task["current_device_id"] == devices["DESKTOP"]
        key = str(uuid4())
        execution = call(f"/api/v1/tasks/{task_id}/run-agents", {"idempotency_key": key})
        assert execution["execution"]["status"] == "DONE"
        replay = call(f"/api/v1/tasks/{task_id}/run-agents", {"idempotency_key": key})
        assert replay["replayed"] and replay["execution"]["id"] == execution["execution"]["id"]
    intelligence = call(f"/api/v1/tasks/{task_id}/plan")
    assert intelligence["execution"]["provider"] == "FixtureModelProvider"
    assert intelligence["critic"]["verdict"] == "PASS"
    assert [run["stage"] for run in intelligence["agent_runs"]] == [
        "context", "planner", "calendar", "memory", "planner_revision", "critic"]
    assert all(run["status"] == "DONE" for run in intelligence["agent_runs"])
    trace = intelligence["execution"]["trace_id"]
    assert all(run["trace_id"] == trace for run in intelligence["agent_runs"])
    tools = [tool for run in intelligence["agent_runs"] for tool in run["tool_calls"]]
    assert len(tools) == 5 and all(tool["trace_id"] == trace for tool in tools)
    assert all(entry["provenance"]["source"] == "DEMO_FIXTURE"
               for entry in intelligence["context"]["preferences"])
    facts = [fact["fact"] for fact in intelligence["plan"]["constraints"]]
    assert all(any(expected in fact for fact in facts) for expected in ["5:00 PM", "Downtown", "Italian", "6:00 PM"])
    assert any("restaurant" in missing.casefold() for missing in intelligence["plan"]["missing_information"])
    if not args.verify_task:
        original_handoff = None
        for source, target in [("DESKTOP", "WEARABLE"), ("WEARABLE", "MOBILE")]:
            payload = {"source_device_id": devices[source], "target_device_id": devices[target], "idempotency_key": str(uuid4())}
            if original_handoff is None:
                original_handoff = payload
            moved = call(f"/api/v1/tasks/{task_id}/handoff", payload)
            assert moved["task"]["id"] == task_id and moved["task"]["current_device_id"] == devices[target]
            assert call(f"/api/v1/tasks/{task_id}/plan") == intelligence
        retried = call(f"/api/v1/tasks/{task_id}/handoff", original_handoff)
        assert retried["replayed"] and retried["task"]["current_device_id"] == devices["MOBILE"]
    assert call(f"/api/v1/tasks/{task_id}")["current_device_id"] == devices["MOBILE"]
    assert len(call(f"/api/v1/tasks/{task_id}/events")) == 3
    print(json.dumps({"result": "PASS", "task_id": task_id, "trace_id": trace,
        "provider": "FIXTURE / DETERMINISTIC", "critic": "PASS", "agent_runs": 6,
        "tool_calls": 5, "current_device": "MOBILE", "restart_verification": bool(args.verify_task)}, indent=2))


if __name__ == "__main__":
    main()
