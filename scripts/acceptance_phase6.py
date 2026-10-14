"""Phase 6 local persistence/personalization acceptance with fixture vector retrieval."""

import argparse
import json
import urllib.request
from uuid import uuid4


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--verify-task")
    args = parser.parse_args()

    def call(path, payload=None, method=None):
        req = urllib.request.Request(
            args.base_url + "/api/v1" + path,
            data=json.dumps(payload).encode() if payload is not None else None,
            method=method,
            headers={"Content-Type": "application/json", "X-Correlation-ID": str(uuid4())},
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)

    def search(task_id):
        return call(
            "/memory/search",
            {
                "task_id": task_id,
                "subject": "demo_user",
                "predicate": "dining_preference",
                "query": "quiet restaurants",
                "limit": 20,
            },
        )

    if args.verify_task:
        task_id = args.verify_task
    else:
        original = call(
            "/memory",
            {
                "idempotency_key": str(uuid4()),
                "value": "quiet Italian restaurants",
                "subject": "demo_user",
                "predicate": "dining_preference",
            },
        )
        assert original["status"] == "ACTIVE" and original["origin"] == "USER_EXPLICIT"
        devices = {d["type"]: d["id"] for d in call("/devices")}
        task = call(
            "/tasks",
            {
                "title": "Plan dinner tomorrow.",
                "description": "PHASE6|" + original["id"],
                "origin_device_id": devices["DESKTOP"],
            },
        )
        task_id = task["id"]
        result = call(f"/tasks/{task_id}/run-agents", {"idempotency_key": "phase6-dinner"})
        assert result["execution"]["status"] == "DONE"
        first = search(task_id)
        assert any(h["memory_id"] == original["id"] for h in first["hits"])
        call(
            f"/tasks/{task_id}/handoff",
            {
                "source_device_id": devices["DESKTOP"],
                "target_device_id": devices["WEARABLE"],
                "idempotency_key": "phase6-wearable",
            },
        )
        media = call(f"/tasks/{task_id}/media/fixture", {"idempotency_key": "phase6-frame"})
        perception = call(
            f"/tasks/{task_id}/perception",
            {"media_id": media["id"], "idempotency_key": "phase6-perception"},
        )
        observation = next(
            o for o in perception["observations"] if o["label"] == "coffee_cup_present"
        )
        candidate = call(
            "/memory/candidates/visual",
            {
                "task_id": task_id,
                "observation_id": observation["id"],
                "idempotency_key": "phase6-visual-" + task_id,
            },
        )
        assert (
            candidate["status"] == "PENDING_CONFIRMATION"
            and candidate["origin"] == "VISUAL_OBSERVATION"
        )
        assert not any(
            h["memory_id"] == candidate["id"]
            for h in call(
                "/memory/search", {"task_id": task_id, "subject": "demo_user", "query": "coffee"}
            )["hits"]
        )
        corrected = call(
            f"/memory/{original['id']}/correct",
            {"idempotency_key": "phase6-correct-" + task_id, "value": "quiet Japanese restaurants"},
        )
        assert corrected["supersedes_id"] == original["id"] and corrected["status"] == "ACTIVE"
        another = call(
            "/tasks",
            {
                "title": "Plan dinner tomorrow.",
                "description": "Phase 6 corrected preference task",
                "origin_device_id": devices["DESKTOP"],
            },
        )
        assert any(h["memory_id"] == corrected["id"] for h in search(another["id"])["hits"])
        second_plan = call(
            f"/tasks/{another['id']}/run-agents", {"idempotency_key": "phase6-corrected-dinner"}
        )
        assert second_plan["execution"]["status"] == "DONE"
        call(
            f"/memory/{corrected['id']}", {"idempotency_key": "phase6-delete-" + task_id}, "DELETE"
        )
        assert not any(
            h["memory_id"] in [original["id"], corrected["id"]] for h in search(task_id)["hits"]
        )
        # A separate benign fact proves active memory survives restart, independently of deletion.
        active = call(
            "/memory",
            {
                "idempotency_key": "phase6-active-" + task_id,
                "memory_type": "FACT",
                "subject": "phase6_" + task_id,
                "predicate": "project_deadline",
                "value": "Friday",
            },
        )
        draft = call(
            "/proactive/evaluate", {"task_id": task_id, "idempotency_key": "phase6-proposal"}
        )
        assert draft["proposal"]["status"] == "PENDING_APPROVAL"
        call(
            f"/tasks/{task_id}/handoff",
            {
                "source_device_id": devices["WEARABLE"],
                "target_device_id": devices["MOBILE"],
                "idempotency_key": "phase6-mobile",
            },
        )
    task = call(f"/tasks/{task_id}")
    original_id = task["description"].split("|")[1]
    records = call("/memory")
    original = next(m for m in records if m["id"] == original_id)
    corrected = next(m for m in records if m["supersedes_id"] == original_id)
    active = next(m for m in records if m["subject"] == "phase6_" + task_id)
    assert (
        original["status"] == "SUPERSEDED"
        and corrected["status"] == "DELETED"
        and active["status"] == "ACTIVE"
    )
    assert not any(
        h["memory_id"] in [original_id, corrected["id"]] for h in search(task_id)["hits"]
    )
    plan = call(f"/tasks/{task_id}/plan")
    hit = next(h for h in plan["context"]["memory_hits"] if h["memory_id"] == original_id)
    assert (
        hit["memory"]["origin"] == "USER_EXPLICIT"
        and hit["memory"]["scope"] == "USER"
        and plan["critic"]["verdict"] == "PASS"
    )
    assert any(
        c["provenance"]["reference"] == "memory:" + original_id for c in plan["plan"]["constraints"]
    )
    perception = call(f"/tasks/{task_id}/perception")[0]
    observation_ids = {o["id"] for o in perception["observations"]}
    candidate = next(
        m
        for m in records
        if m["origin"] == "VISUAL_OBSERVATION"
        and any(o in m["source_reference"] for o in observation_ids)
    )
    assert candidate["status"] == "PENDING_CONFIRMATION"
    proposal = call(f"/tasks/{task_id}/proposals")[0]
    detail = call("/proposals/" + proposal["id"])
    assert (
        proposal["status"] == "PENDING_APPROVAL"
        and detail["approval"] is None
        and detail["execution"] is None
    )
    assert task["current_device_id"] == "00000000-0000-4000-8000-000000000030"
    assert call("/memory/" + original_id + "/history")[-1]["event_type"] == "MEMORY_SUPERSEDED"
    assert call("/memory/" + corrected["id"] + "/history")[-1]["event_type"] == "MEMORY_DELETED"
    assert any(
        h["memory_id"] == active["id"]
        for h in call("/memory/search", {"subject": active["subject"], "query": "Friday"})["hits"]
    )
    print(
        json.dumps(
            {
                "result": "PASS",
                "task_id": task_id,
                "original_memory": original_id,
                "corrected_memory": corrected["id"],
                "active_memory": active["id"],
                "candidate": candidate["id"],
                "perception_id": perception["id"],
                "media_id": perception["media_id"],
                "proposal_id": proposal["id"],
                "device": "MOBILE",
                "embedding": "FIXTURE / NOT REAL SEMANTIC QUALITY",
                "real_embedding": "NOT CONFIGURED",
                "required_external_spend_usd": 0,
                "restart_verification": bool(args.verify_task),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
