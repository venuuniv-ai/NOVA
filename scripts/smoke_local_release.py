"""Fresh authenticated local release smoke, using FIXTURE generation only."""

import json
import subprocess
import time
from uuid import uuid4

from qualify_phase11 import ROOT


def smoke(release):
    if release.status()["status"] != "READY":
        raise RuntimeError("RELEASE_NOT_READY")
    call = release.api
    call("/tasks", expected=401, credential=False)
    identity = call("/auth/me")
    assert identity["mode"] == "local"
    devices = {d["type"]: d["id"] for d in call("/devices")}
    task = call(
        "/tasks",
        {"title": "NOVA v1 local release smoke", "origin_device_id": devices["DESKTOP"]},
        201,
    )
    subject = "release_" + uuid4().hex[:10]
    memory = call(
        "/memory",
        {
            "idempotency_key": str(uuid4()),
            "subject": subject,
            "predicate": "preferred_cuisine",
            "value": "noodles",
        },
        201,
    )
    result = call(
        "/inference/generate",
        {
            "task_id": task["id"],
            "request_id": str(uuid4()),
            "mode": "FIXTURE",
            "operation": "RAG",
            "query": memory["normalized_text"],
            "retrieval": "LEXICAL",
            "max_output_tokens": 96,
        },
    )
    assert result["state"] == "DONE" and result["simulation"]
    assert any(
        c["evidence_id"] == memory["id"] and c["quote"] == memory["normalized_text"]
        for c in result["output"]["claims"]
    )
    payload = {
        "task_id": task["id"],
        "query": f"Which cuisine does {subject} prefer?",
        "memory_ids": [memory["id"]],
        "idempotency_key": str(uuid4()),
    }
    draft = call("/proactive/drafts", payload, 202)
    assert call("/proactive/drafts", payload, 202)["id"] == draft["id"]
    until = time.monotonic() + 45
    while time.monotonic() < until:
        release.gate()
        ready = call("/proactive/drafts/" + draft["id"])
        if ready["state"] not in {"QUEUED", "RUNNING"}:
            break
        time.sleep(0.2)
    assert ready["state"] == "PENDING_APPROVAL" and ready["simulation"]
    assert ready["evidence"][0]["id"] == memory["id"]
    assert ready["content"] == memory["normalized_text"] and not ready["execution_enabled"]
    path = "/proposals/" + ready["proposal_id"]
    detail = call(path)
    assert detail["approval"] is None and detail["execution"] is None
    for operation in ["approve", "execute"]:
        refused = call(path + "/" + operation, {"idempotency_key": str(uuid4())}, 409)
        assert refused["error"]["code"] == "DRAFT_ONLY"
    assert (
        call(path + "/reject", {"idempotency_key": str(uuid4())})["approval"]["decision"]
        == "REJECTED"
    )
    assert call("/proactive/drafts/" + draft["id"])["content"] is None
    for source, target in [("DESKTOP", "WEARABLE"), ("WEARABLE", "MOBILE")]:
        assert (
            call(
                "/tasks/" + task["id"] + "/handoff",
                {
                    "source_device_id": devices[source],
                    "target_device_id": devices[target],
                    "idempotency_key": str(uuid4()),
                },
            )["task"]["id"]
            == task["id"]
        )
    assert len(call("/tasks/" + task["id"] + "/events")) == 3
    token = (release.private / "operator.token").read_text().strip()
    # Existing strict real-service browser journeys: login/cookie/logout, actual
    # operations subscription/pending fixture proposal, and cross-origin refusal.
    with (release.state / "browser-smoke.log").open("w") as log:
        tested = subprocess.run(
            [
                "npm",
                "run",
                "test:e2e",
                "--",
                "tests/security.spec.ts",
                "--grep",
                "authenticated local stack",
                "--trace",
                "off",
            ],
            cwd=ROOT / "frontend",
            env={**release.env, "NOVA_TEST_BEARER": token},
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=150,
        )
    assert tested.returncode == 0, "BROWSER_SMOKE_FAILED"
    outcome = {
        "status": "PASS",
        "task_id": task["id"],
        "memory_id": memory["id"],
        "draft_id": draft["id"],
        "proposal_id": ready["proposal_id"],
        "rag_run_id": result["id"],
        "mode": "FIXTURE",
        "real_generations": 0,
        "external_actions": 0,
        "draft_result": "PENDING_APPROVAL then explicitly REJECTED; approval/execution denied",
        "citation": "ORIGINAL_UUID_AND_EXACT_QUOTE",
        "browser_cases": 3,
        "http_no_bearer": 401,
        "task_device": "MOBILE",
        "at": time.time(),
    }
    (release.state / "smoke.json").write_text(json.dumps(outcome, indent=2) + "\n")
    return outcome
