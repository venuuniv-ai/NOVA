"""Real local REST acceptance for the deterministic Phase 5 wearable scene."""
import argparse
import hashlib
import json
import urllib.request
from uuid import uuid4


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--verify-task")
    args = parser.parse_args()

    def call(path, payload=None, binary=False):
        request = urllib.request.Request(args.base_url + "/api/v1" + path, data=json.dumps(payload).encode() if payload is not None else None, headers={"Content-Type": "application/json", "X-Correlation-ID": str(uuid4())})
        with urllib.request.urlopen(request, timeout=30) as response:
            assert response.headers["X-Correlation-ID"]
            return response.read() if binary else json.load(response)

    devices = {d["type"]: d["id"] for d in call("/devices")}
    if args.verify_task:
        task_id = args.verify_task
    else:
        task_id = call("/tasks", {"title": "Find somewhere for dinner with Sarah tomorrow after my meeting.", "origin_device_id": devices["DESKTOP"]})["id"]
        call(f"/tasks/{task_id}/handoff", {"source_device_id": devices["DESKTOP"], "target_device_id": devices["WEARABLE"], "idempotency_key": "phase5-wearable"})
        media = call(f"/tasks/{task_id}/media/fixture", {"idempotency_key": "phase5-frame"})
        run = call(f"/tasks/{task_id}/perception", {"media_id": media["id"], "idempotency_key": "phase5-perception", "privacy_class": "SENSITIVE_LOCAL_ONLY"})
        repeated = call(f"/tasks/{task_id}/perception", {"media_id": media["id"], "idempotency_key": "phase5-perception", "privacy_class": "SENSITIVE_LOCAL_ONLY"})
        assert repeated["id"] == run["id"] and repeated["replayed"]
        reason = call(f"/tasks/{task_id}/perception/{run['id']}/reason", {"idempotency_key": "phase5-reason", "propose_action": True})
        assert reason["execution"]["execution"]["status"] == "DONE" and not reason["memory_written"]
        assert reason["proposal"]["proposal"]["status"] == "PENDING_APPROVAL"
        call(f"/tasks/{task_id}/handoff", {"source_device_id": devices["WEARABLE"], "target_device_id": devices["MOBILE"], "idempotency_key": "phase5-mobile"})
    task = call(f"/tasks/{task_id}")
    media = call(f"/tasks/{task_id}/media")[0]
    runs = call(f"/tasks/{task_id}/perception")
    assert len(runs) == 1
    run = runs[0]
    assert task["current_device_id"] == devices["MOBILE"] and run["status"] == "DONE"
    objects = [o for o in run["observations"] if o["processor"] == "FIXTURE_VISION"]
    assert len(objects) == 4 and len(run["observations"]) == 5 and len(run["context"]) == 5
    assert all(o["simulation"] and o["source"] == "FIXTURE_IMAGE" and o["score"] is None and o["region"] is None for o in objects)
    assert any("consistent with" in c["interpretation"] for c in run["context"])
    content = call(f"/tasks/{task_id}/media/{media['id']}/content", binary=True)
    assert hashlib.sha256(content).hexdigest() == media["sha256"]
    calls = call(f"/tasks/{task_id}/model-calls")
    assert len(calls) == 1 and calls[0]["trace_id"] == run["trace_id"] and "VISION_REQUIRED" in calls[0]["decision"]["reason_codes"]
    proposal = call(f"/tasks/{task_id}/proposals")[0]
    assert proposal["status"] == "PENDING_APPROVAL"
    detail = call(f"/proposals/{proposal['id']}")
    assert detail["approval"] is None and detail["execution"] is None
    plan = call(f"/tasks/{task_id}/plan")
    assert plan["critic"]["verdict"] == "PASS" and len(plan["context"]["visual_evidence"]) == 5
    print(json.dumps({"result": "PASS", "task_id": task_id, "media_id": media["id"], "media_sha256": media["sha256"], "perception_id": run["id"], "trace_id": run["trace_id"], "observation_ids": [o["id"] for o in run["observations"]], "proposal_id": proposal["id"], "device": "MOBILE", "required_api_spend": 0, "real_inference": "NOT CONFIGURED", "restart_verification": bool(args.verify_task)}, indent=2))


if __name__ == "__main__":
    main()
