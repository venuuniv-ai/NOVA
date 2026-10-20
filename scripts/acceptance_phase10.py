"""Operator-run local fixture draft/Kafka acceptance. No model or action execution.

Use an isolated Compose project, existing images and private short-lived tokens.
Optional recovery stops/restarts only its proactive worker, preserving overlays.
"""

import argparse
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit
from uuid import uuid4


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8080")
    parser.add_argument("--recovery", action="store_true")
    parser.add_argument("--inject-duplicates", action="store_true")
    args = parser.parse_args()
    endpoint = urlsplit(args.base_url)
    if (
        endpoint.scheme != "http"
        or endpoint.hostname not in {"localhost", "127.0.0.1"}
        or endpoint.username
        or endpoint.password
        or endpoint.path not in {"", "/"}
        or endpoint.query
        or endpoint.fragment
    ):
        raise ValueError("Only an explicit local loopback application is permitted")
    token, other = os.environ["NOVA_TOKEN_A"], os.environ["NOVA_TOKEN_B"]
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    project = os.environ.get("COMPOSE_PROJECT_NAME", "")
    if args.recovery or args.inject_duplicates:
        if not project.startswith("nova-phase10-") or not os.environ.get("COMPOSE_FILE"):
            raise ValueError("Explicit isolated nova-phase10- Compose project/files required")

    def call(path, body=None, credential=token, expected=200):
        request = urllib.request.Request(
            args.base_url + "/api/v1" + path,
            data=json.dumps(body).encode() if body is not None else None,
            headers={
                "Content-Type": "application/json",
                **({"Authorization": "Bearer " + credential} if credential else {}),
            },
        )
        try:
            with opener.open(request, timeout=15) as response:
                assert response.status == expected, (path, response.status)
                return json.load(response)
        except urllib.error.HTTPError as error:
            assert error.code == expected, (path, error.code)
            raw = error.read()
            return json.loads(raw) if raw else {}

    def wait(path, states):
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            result = call(path)
            if result["state"] in states:
                return result
            time.sleep(0.2)
        raise AssertionError("Draft did not reach the declared state")

    call("/tasks", credential="", expected=401)
    assert call("/auth/me")["mode"] == "local"
    devices = {d["type"]: d["id"] for d in call("/devices")}
    task = call(
        "/tasks",
        {
            "title": "Phase 10 owned fixture draft acceptance",
            "origin_device_id": devices["DESKTOP"],
        },
        expected=201,
    )
    subject = "phase10_" + uuid4().hex[:8]
    memory = call(
        "/memory",
        {
            "idempotency_key": str(uuid4()),
            "subject": subject,
            "predicate": "preferred_cuisine",
            "value": "noodles",
        },
        expected=201,
    )
    payload = {
        "task_id": task["id"],
        "query": f"Which cuisine does {subject} prefer?",
        "memory_ids": [memory["id"]],
        "idempotency_key": str(uuid4()),
    }
    row = call("/proactive/drafts", payload, expected=202)
    assert call("/proactive/drafts", payload, expected=202)["id"] == row["id"]
    path = "/proactive/drafts/" + row["id"]
    call(path, credential=other, expected=404)
    ready = wait(path, {"PENDING_APPROVAL", "FAILED", "EXPIRED"})
    assert ready["state"] == "PENDING_APPROVAL", ready["error"]
    assert ready["simulation"] and not ready["execution_enabled"]
    assert ready["content"] == memory["normalized_text"]
    assert ready["evidence"][0]["id"] == memory["id"]
    assert ready["verification"] == "EXACT_SUPPORTED_QUOTES"
    proposal_path = "/proposals/" + ready["proposal_id"]
    detail = call(proposal_path)
    assert detail["approval"] is None and detail["execution"] is None
    for operation in ("approve", "execute"):
        denied = call(
            proposal_path + "/" + operation, {"idempotency_key": str(uuid4())}, expected=409
        )
        assert denied["error"]["code"] == "DRAFT_ONLY"

    duplicate = "NOT_EXECUTED"
    if args.inject_duplicates:
        code = """
import json,sys,time,hashlib
from uuid import UUID
from kafka import KafkaProducer
from sqlalchemy import select,func
from app.database import SessionLocal
from app.events.models import Outbox,DeadLetter
from app.events.pipeline import TOPIC,envelope
with SessionLocal() as session:
 row=session.scalar(select(Outbox).where(Outbox.event_type=='ContextEvent.changed',
     Outbox.payload['resource_id'].astext==sys.argv[1]))
 message=envelope(row)
producer=KafkaProducer(bootstrap_servers='kafka:9092',acks='all')
for _ in range(3):
 producer.send(TOPIC,key=message['task_id'].encode(),value=json.dumps(message).encode()).get(timeout=10)
message['payload']['approval']=True
raw=json.dumps(message).encode();fingerprint=hashlib.sha256(raw).hexdigest()
producer.send(TOPIC,key=message['task_id'].encode(),value=raw).get(timeout=10)
producer.close()
deadline=time.monotonic()+30
while time.monotonic()<deadline:
 with SessionLocal() as session:
  count=session.scalar(select(func.count()).select_from(DeadLetter).where(DeadLetter.fingerprint==fingerprint))
 if count==3:break
 time.sleep(.2)
assert count==3
"""
        subprocess.run(
            ["docker", "compose", "exec", "-T", "backend", "python", "-c", code, row["id"]],
            check=True,
        )
        assert call(path)["proposal_id"] == ready["proposal_id"]
        duplicate = "PASS / THREE DUPLICATES AND THREE FORGED-EVENT DEAD LETTERS"

    rejected = call(proposal_path + "/reject", {"idempotency_key": str(uuid4())})
    assert rejected["approval"]["decision"] == "REJECTED" and rejected["execution"] is None
    assert call(path)["state"] == "REJECTED"

    recovery = "NOT_EXECUTED"
    if args.recovery:
        subprocess.run(["docker", "compose", "stop", "proactive-worker"], check=True)
        try:
            payload["idempotency_key"] = str(uuid4())
            queued = call("/proactive/drafts", payload, expected=202)
            # Stop/restart proves queued durability. In-flight crash/rollback has
            # separate PostgreSQL tests; this is not claimed as a mid-call crash.
            assert call("/proactive/drafts/" + queued["id"])["state"] == "QUEUED"
        finally:
            subprocess.run(
                [
                    "docker",
                    "compose",
                    "up",
                    "-d",
                    "--no-build",
                    "--pull",
                    "never",
                    "proactive-worker",
                ],
                check=True,
            )
        recovered = wait(
            "/proactive/drafts/" + queued["id"], {"PENDING_APPROVAL", "FAILED", "EXPIRED"}
        )
        assert recovered["state"] == "PENDING_APPROVAL"
        assert recovered["proposal_id"] != ready["proposal_id"]
        cancelled = call("/proactive/drafts/" + queued["id"] + "/cancel", {})
        assert cancelled["state"] == "CANCELLED" and cancelled["content"] is None
        recovery = "PASS / QUEUED WORK SURVIVED WORKER STOP/RESTART"

    print(
        json.dumps(
            {
                "result": "PASS",
                "task_id": task["id"],
                "draft_id": row["id"],
                "proposal_id": ready["proposal_id"],
                "mode": "FIXTURE",
                "execution": "DISABLED",
                "ownership": "LOCAL JWT / FOREIGN OWNER 404 / NO BEARER 401",
                "citation_verification": ready["verification"],
                "final_state": "REJECTED",
                "duplicate_delivery": duplicate,
                "worker_recovery": recovery,
                "real_model_calls": 0,
                "external_actions": 0,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
