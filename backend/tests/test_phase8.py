import json
import secrets
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from uuid import uuid4

import jwt
import pytest
from sqlalchemy import func, select

from app.config import settings
from app.database import SessionLocal
from app.events.models import DeadLetter, Inbox, Job, Outbox, Projection
from app.events.pipeline import consume, envelope, publish_one, work_one
from app.models import Device, Task, User
from app.security.identity import Principal, principal
from app.security.models import Identity
from app.seed import DEMO_USER_ID


@pytest.fixture
def identities(tmp_path, monkeypatch):
    key = secrets.token_hex(64)
    path = tmp_path / "auth.key"
    path.write_text(key)
    monkeypatch.setattr(settings, "auth_key_file", str(path))
    monkeypatch.setattr(settings, "auth_mode", "local")
    result = []
    with SessionLocal.begin() as s:
        for roles in [["owner", "approver", "operator"], ["owner"], ["viewer"]]:
            user_id, device_id, subject = uuid4(), uuid4(), str(uuid4())
            s.add(User(id=user_id, name="Controlled identity fixture"))
            s.flush()
            s.add(Device(id=device_id, user_id=user_id, name="Desktop", type="DESKTOP"))
            s.add(
                Identity(
                    user_id=user_id,
                    issuer="nova-local",
                    subject=subject,
                    roles=roles,
                    created_at=datetime.now(UTC),
                    version=1,
                    enabled=True,
                )
            )
            now = int(datetime.now(UTC).timestamp())
            claims = {
                "sub": subject,
                "iss": "nova-local",
                "aud": "nova-api",
                "iat": now,
                "nbf": now,
                "exp": now + 300,
                "device_id": str(device_id),
                "version": 1,
            }
            token = jwt.encode(claims, key, algorithm="HS256")
            result.append(
                {
                    "user_id": user_id,
                    "device_id": device_id,
                    "claims": claims,
                    "headers": {"Authorization": "Bearer " + token},
                    "key": key,
                }
            )
    return result


def test_authentication_required_even_with_spoofed_headers(client, identities):
    r = client.get("/api/v1/tasks", headers={"X-User-ID": str(DEMO_USER_ID), "X-Roles": "operator"})
    assert r.status_code == 401
    assert client.get("/health/live").status_code == 200
    assert client.get("/api/v1/auth/me", headers=identities[0]["headers"]).json()["mode"] == "local"


@pytest.mark.parametrize(
    "change",
    [
        "expired",
        "issuer",
        "audience",
        "device",
        "signature",
        "version",
        "missing_exp",
        "missing_nbf",
        "future",
    ],
)
def test_bad_credentials_refused(client, identities, change):
    a = identities[0]
    claims = dict(a["claims"])
    key = a["key"]
    if change == "expired":
        claims["exp"] = claims["iat"] - 1
    if change == "issuer":
        claims["iss"] = "forged"
    if change == "audience":
        claims["aud"] = "other"
    if change == "device":
        claims["device_id"] = str(identities[1]["device_id"])
    if change == "signature":
        key = secrets.token_hex(64)
    if change == "version":
        claims["version"] = 2
    if change == "missing_exp":
        del claims["exp"]
    if change == "missing_nbf":
        del claims["nbf"]
    if change == "future":
        claims["nbf"] = claims["exp"] + 30
    token = jwt.encode(claims, key, algorithm="HS256")
    assert (
        client.get("/api/v1/tasks", headers={"Authorization": "Bearer " + token}).status_code == 401
    )


def test_rbac_and_resource_ownership(client, identities):
    a, b, viewer = identities
    task = client.post(
        "/api/v1/tasks",
        headers=a["headers"],
        json={"title": "Controlled owner task", "origin_device_id": str(a["device_id"])},
    ).json()
    assert task["user_id"] == str(a["user_id"])
    assert client.get("/api/v1/tasks", headers=b["headers"]).json() == []
    for suffix in [
        "",
        "/events",
        "/plan",
        "/agent-runs",
        "/memory",
        "/media",
        "/model-calls",
        "/proposals",
    ]:
        assert (
            client.get("/api/v1/tasks/" + task["id"] + suffix, headers=b["headers"]).status_code
            == 404
        )
    assert client.get("/api/v1/devices", headers=a["headers"]).json()[0]["id"] == str(
        a["device_id"]
    )
    assert client.post("/api/v1/tasks", headers=viewer["headers"], json={}).status_code == 403
    assert client.get("/api/v1/evaluation/runs", headers=b["headers"]).status_code == 403
    assert (
        client.post(
            "/api/v1/proposals/" + str(uuid4()) + "/approve", headers=b["headers"], json={}
        ).status_code
        == 403
    )


def test_identity_revocation(client, identities):
    a = identities[0]
    with SessionLocal.begin() as s:
        row = s.scalar(select(Identity).where(Identity.user_id == a["user_id"]))
        row.enabled = False
    assert client.get("/api/v1/tasks", headers=a["headers"]).status_code == 401


def test_memory_owned_by_authenticated_user(client, identities):
    a, b, _ = identities
    body = {
        "idempotency_key": "memory",
        "memory_type": "FACT",
        "subject": "evaluation",
        "predicate": "deadline",
        "value": "Friday",
        "statement": "My evaluation deadline is Friday.",
    }
    # Reuse the exact public contract rather than bypassing request ownership.
    from app.memory.contracts import MemoryInput

    body = MemoryInput(
        idempotency_key="memory",
        memory_type="FACT",
        subject="evaluation",
        predicate="project_deadline",
        value="Friday",
    ).model_dump(mode="json")
    r = client.post("/api/v1/memory", json=body, headers=a["headers"])
    assert r.status_code == 201, r.text
    mid = r.json()["id"]
    assert client.get("/api/v1/memory/" + mid, headers=b["headers"]).status_code == 404
    assert client.get("/api/v1/memory", headers=b["headers"]).json() == []


def test_outbox_atomic_rollback_and_commit(task):
    with SessionLocal() as s:
        before = s.scalar(select(func.count()).select_from(Outbox))
        row = s.get(Task, task["id"])
        row.description = "Rolled back fixture mutation"
        s.flush()
        assert s.scalar(select(func.count()).select_from(Outbox)) == before + 1
        s.rollback()
        assert s.scalar(select(func.count()).select_from(Outbox)) == before
    with SessionLocal.begin() as s:
        s.get(Task, task["id"]).description = "Committed fixture mutation"
    with SessionLocal() as s:
        assert s.scalar(select(func.count()).select_from(Outbox)) == before + 1


def test_publish_ack_failure_retry_and_no_uncommitted_delivery(task):
    def failure(key, value):
        raise TimeoutError()

    assert publish_one(failure)
    with SessionLocal.begin() as s:
        row = s.scalar(select(Outbox).order_by(Outbox.sequence))
        assert row.state == "PENDING" and row.attempts == 1 and row.published_at is None
        expected = envelope(row)
        row.next_attempt_at = datetime.now(UTC)
    delivered = []
    assert publish_one(lambda key, value: delivered.append((key, value)))
    assert len(delivered) == 1
    assert json.loads(delivered[0][1]) == expected


def test_duplicate_delivery_concurrency_and_projection_order(task):
    with SessionLocal() as s:
        rows = list(
            s.scalars(select(Outbox).where(Outbox.task_id == task["id"]).order_by(Outbox.sequence))
        )
        raw = json.dumps(envelope(rows[-1])).encode()
        older = json.dumps(envelope(rows[0])).encode()
    with ThreadPoolExecutor(2) as pool:
        statuses = list(pool.map(consume, [raw, raw]))
    assert sorted(statuses) == ["DUPLICATE", "PROCESSED"]
    consume(older)
    with SessionLocal() as s:
        assert s.get(Projection, task["id"]).last_sequence == rows[-1].sequence
        assert (
            s.scalar(select(func.count()).select_from(Inbox).where(Inbox.event_id == rows[-1].id))
            == 1
        )


def test_forged_poison_event_never_effects(task):
    with SessionLocal() as s:
        raw = envelope(s.scalar(select(Outbox).where(Outbox.task_id == task["id"])))
    raw["payload"]["approval"] = True
    data = json.dumps(raw).encode()
    assert consume(data) == consume(data) == "DEAD_LETTER"
    assert consume(b"not json") == "DEAD_LETTER"
    with SessionLocal() as s:
        assert s.scalar(select(func.count()).select_from(DeadLetter)) == 2
        assert s.scalar(select(func.count()).select_from(Job)) == 0


def test_proactive_event_duplicate_only_creates_one_pending_draft(client, task, devices):
    assert client.post("/api/v1/operations/tasks/" + task["id"] + "/subscribe").status_code == 200
    client.post(
        "/api/v1/tasks/" + task["id"] + "/handoff",
        json={
            "source_device_id": devices["DESKTOP"],
            "target_device_id": devices["WEARABLE"],
            "idempotency_key": "handoff",
        },
    )
    with SessionLocal() as s:
        row = next(
            o
            for o in s.scalars(select(Outbox).where(Outbox.task_id == task["id"]))
            if o.payload.get("transition") == "HANDOFF_DESKTOP_TO_WEARABLE"
        )
        data = json.dumps(envelope(row)).encode()
    assert consume(data, "proactive") == "PROCESSED"
    assert consume(data, "proactive") == "DUPLICATE"
    assert work_one()
    proposals = client.get("/api/v1/tasks/" + task["id"] + "/proposals").json()
    assert len(proposals) == 1 and proposals[0]["status"] == "PENDING_APPROVAL"
    assert not work_one()
    with SessionLocal() as s:
        assert s.scalar(select(func.count()).select_from(Job)) == 1


def test_worker_identity_cannot_approve_or_execute():
    from app.proactive.service import ProactiveService

    token = principal.set(Principal(DEMO_USER_ID, frozenset({"owner"}), mode="worker"))
    try:
        with pytest.raises(Exception) as error:
            ProactiveService().mutate(uuid4(), "approve", None, "test")
        assert getattr(error.value, "status_code", None) == 403
    finally:
        principal.reset(token)


def test_oidc_public_jwks_validation_and_server_roles(client, identities, tmp_path, monkeypatch):
    from cryptography.hazmat.primitives.asymmetric import rsa
    from jwt.algorithms import RSAAlgorithm

    a = identities[0]
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = json.loads(RSAAlgorithm.to_jwk(private.public_key()))
    public.update(kid="fixture-key", alg="RS256", use="sig")
    path = tmp_path / "jwks.json"
    path.write_text(json.dumps({"keys": [public]}))
    monkeypatch.setattr(settings, "auth_mode", "oidc")
    monkeypatch.setattr(settings, "oidc_issuer", "http://local-issuer")
    monkeypatch.setattr(settings, "oidc_jwks_file", str(path))
    with SessionLocal.begin() as s:
        identity = s.scalar(select(Identity).where(Identity.user_id == a["user_id"]))
        identity.issuer, identity.roles = "http://local-issuer", ["viewer"]
    claims = {**a["claims"], "iss": "http://local-issuer", "roles": ["operator", "approver"]}
    claims.pop("nbf", None)  # OIDC nbf is optional; verify it when present.
    encoded = jwt.encode(claims, private, algorithm="RS256", headers={"kid": "fixture-key"})
    headers = {"Authorization": "Bearer " + encoded}
    assert client.get("/api/v1/auth/me", headers=headers).json()["roles"] == ["viewer"]
    assert client.get("/api/v1/evaluation/runs", headers=headers).status_code == 403
    assert client.post("/api/v1/tasks", headers=headers, json={}).status_code == 403
    from datetime import timedelta

    from app.security.models import DeviceRegistration

    with SessionLocal.begin() as session:
        session.add(
            DeviceRegistration(
                device_id=a["device_id"],
                user_id=a["user_id"],
                enabled=True,
                version=1,
                updated_at=datetime.now(UTC) - timedelta(seconds=1),
            )
        )
    claims["iat"] = int(datetime.now(UTC).timestamp()) - 2
    encoded = jwt.encode(claims, private, algorithm="RS256", headers={"kid": "fixture-key"})
    assert (
        client.get("/api/v1/auth/me", headers={"Authorization": "Bearer " + encoded}).status_code
        == 401
    )
    claims["iat"] = int(datetime.now(UTC).timestamp())
    encoded = jwt.encode(claims, private, algorithm="RS256", headers={"kid": "fixture-key"})
    assert (
        client.get("/api/v1/auth/me", headers={"Authorization": "Bearer " + encoded}).status_code
        == 200
    )
    claims["iss"] = "http://forged-issuer"
    encoded = jwt.encode(claims, private, algorithm="RS256", headers={"kid": "fixture-key"})
    assert (
        client.get("/api/v1/auth/me", headers={"Authorization": "Bearer " + encoded}).status_code
        == 401
    )


def test_consumer_effect_rollback_allows_redelivery(task, monkeypatch):
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.orm import Session

    with SessionLocal() as s:
        row = s.scalar(select(Outbox).where(Outbox.task_id == task["id"]))
        data, event_id = json.dumps(envelope(row)).encode(), row.id
    # Context-manager transaction commit uses transaction hooks; inject before commit.
    from sqlalchemy import event

    def fail_commit(session):
        raise OperationalError("fixture", {}, Exception("controlled failure"))

    event.listen(Session, "before_commit", fail_commit)
    try:
        with pytest.raises(OperationalError):
            consume(data)
    finally:
        event.remove(Session, "before_commit", fail_commit)
    with SessionLocal() as s:
        assert s.get(Inbox, ("projection", event_id)) is None
    assert consume(data) == "PROCESSED"


def test_publisher_ack_then_crash_redelivery_deduplicates(task):
    from sqlalchemy import event
    from sqlalchemy.orm import Session

    delivered = []

    def crash(session):
        raise RuntimeError("Controlled crash after broker ack before DB commit")

    event.listen(Session, "before_commit", crash)
    try:
        with pytest.raises(RuntimeError):
            publish_one(lambda key, raw: delivered.append(raw))
    finally:
        event.remove(Session, "before_commit", crash)
    assert publish_one(lambda key, raw: delivered.append(raw))
    assert len(delivered) == 2 and delivered[0] == delivered[1]
    assert consume(delivered[0]) == "PROCESSED"
    assert consume(delivered[1]) == "DUPLICATE"


def test_job_recovery_replays_original_service_key(client, task, devices):
    client.post("/api/v1/operations/tasks/" + task["id"] + "/subscribe")
    client.post(
        "/api/v1/tasks/" + task["id"] + "/handoff",
        json={
            "source_device_id": devices["DESKTOP"],
            "target_device_id": devices["WEARABLE"],
            "idempotency_key": "move",
        },
    )
    with SessionLocal() as s:
        row = next(
            o
            for o in s.scalars(select(Outbox).where(Outbox.task_id == task["id"]))
            if o.payload.get("transition") == "HANDOFF_DESKTOP_TO_WEARABLE"
        )
        consume(json.dumps(envelope(row)).encode(), "proactive")
    assert work_one()
    with SessionLocal.begin() as s:
        job = s.scalar(select(Job).where(Job.task_id == task["id"]))
        result_id = job.result_id
        job.state = "RUNNING"  # Crash after domain commit, before job acknowledgment.
    assert work_one()
    with SessionLocal() as s:
        assert s.scalar(select(Job).where(Job.task_id == task["id"])).result_id == result_id
    assert len(client.get("/api/v1/tasks/" + task["id"] + "/proposals").json()) == 1


def test_device_registration_and_revocation_enforced(client, identities):
    a, b, _ = identities
    own = str(a["device_id"])
    assert (
        client.post(
            "/api/v1/auth/devices/" + str(b["device_id"]) + "/revoke", headers=a["headers"]
        ).status_code
        == 404
    )
    registered = client.post(
        "/api/v1/auth/devices/register", json={"device_id": own}, headers=a["headers"]
    )
    assert registered.status_code == 200 and registered.json()["version"] == 1
    # A new registration epoch invalidates earlier local device credentials.
    assert client.get("/api/v1/tasks", headers=a["headers"]).status_code == 401
    claims = {**a["claims"], "device_version": 1}
    headers = {"Authorization": "Bearer " + jwt.encode(claims, a["key"], algorithm="HS256")}
    assert client.get("/api/v1/tasks", headers=headers).status_code == 200
    assert (
        client.post("/api/v1/auth/devices/" + own + "/revoke", headers=headers).status_code == 200
    )
    assert client.get("/api/v1/tasks", headers=headers).status_code == 401


def test_standalone_evaluation_process_registers_complete_schema():
    import subprocess
    import sys

    code = (
        "from app.evaluation.runner import EvaluationRunner; "
        "from app.evaluation.contracts import RunInput; from uuid import uuid4; "
        "r=EvaluationRunner().run(RunInput(idempotency_key=str(uuid4()))); "
        "assert r['status']=='DONE' and r['summary']['gate_status']=='PASS', r.get('safe_error')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr[-2000:]
