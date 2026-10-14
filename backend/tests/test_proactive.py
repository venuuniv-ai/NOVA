import asyncio
import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import func, select

from app.config import settings
from app.database import SessionLocal
from app.intelligence.contracts import ProviderResponse
from app.intelligence.plugins import EmptyQuery, KernelRuntime
from app.intelligence.provider import FixtureModelProvider
from app.proactive.api import get_service
from app.proactive.clock import DEMO_TIME, FixtureClock, SystemClock
from app.proactive.communication import (
    ActionExecutor,
    CommunicationAgent,
    SimulatedCommunicationAdapter,
    register_communication,
)
from app.proactive.contracts import (
    ActionIntent,
    Attendee,
    CommunicationInput,
    ContextEventInput,
    EditRequest,
    Mutation,
)
from app.proactive.models import ActionExecution, ActionProposal, ApprovalDecision, AuditEvent
from app.proactive.policy import evaluate_policy, payload_hash
from app.proactive.service import ProactiveService
from app.proactive.trigger import ProactiveTriggerEngine, RedisCooldown, demo_meeting
from app.seed import DEMO_USER_ID


@pytest.fixture
def service():
    return ProactiveService(
        cooldown=RedisCooldown(settings.redis_url, prefix=f"nova:test:{uuid4()}")
    )


def evaluate(service, task, key=None):
    return service.evaluate(
        ContextEventInput(task_id=task["id"], idempotency_key=key or str(uuid4())),
        "test-correlation",
    )


def proposal(service, task):
    result = evaluate(service, task)
    assert result.status == "SURFACED", result
    return result.proposal


def mutate(service, item, operation, key=None, **changes):
    payload = (
        EditRequest(idempotency_key=key or str(uuid4()), **changes)
        if operation == "edit"
        else Mutation(idempotency_key=key or str(uuid4()))
    )
    return service.mutate(item.id, operation, payload, "test-correlation")


def count(model):
    with SessionLocal() as session:
        return session.scalar(select(func.count()).select_from(model))


def test_trigger_arithmetic_and_fixture_clock():
    clock = FixtureClock()
    situation, reason = ProactiveTriggerEngine(clock).analyze(demo_meeting(clock))
    assert (situation.minutes_available, situation.travel_minutes, situation.lateness_minutes) == (
        29,
        35,
        6,
    )
    assert situation.arrival_at.hour == 14 and situation.arrival_at.minute == 6
    assert reason == "SURFACE" and clock.now() == DEMO_TIME
    assert SystemClock().now().tzinfo


@pytest.mark.parametrize(
    "changes,reason",
    [
        ({"travel_minutes": 30}, "BELOW_THRESHOLD"),
        ({"travel_minutes": 31}, "BELOW_THRESHOLD"),
        ({"confidence": 0.5}, "LOW_CONFIDENCE"),
        ({"proactive_enabled": False}, "PREFERENCE_DISABLED"),
        ({"starts_at": DEMO_TIME - timedelta(minutes=1)}, "OUTSIDE_RELEVANT_WINDOW"),
        ({"starts_at": DEMO_TIME + timedelta(hours=2)}, "OUTSIDE_RELEVANT_WINDOW"),
    ],
)
def test_trigger_suppression(changes, reason):
    clock = FixtureClock()
    meeting = demo_meeting(clock).model_copy(update=changes)
    assert ProactiveTriggerEngine(clock).analyze(meeting)[1] == reason


def test_fingerprint_stable_private_and_window_sensitive():
    clock = FixtureClock()
    engine = ProactiveTriggerEngine(clock)
    situation, _ = engine.analyze(demo_meeting(clock))
    key = engine.fingerprint(DEMO_USER_ID, situation)
    assert len(key) == 64 and key == engine.fingerprint(DEMO_USER_ID, situation)
    assert "Architecture" not in key
    assert key != engine.fingerprint(uuid4(), situation)
    situation.meeting.starts_at += timedelta(days=1)
    assert key != engine.fingerprint(DEMO_USER_ID, situation)


def test_real_redis_atomic_dedup_and_ttl():
    gate = RedisCooldown(settings.redis_url, prefix=f"nova:test:{uuid4()}", ttl=1)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: gate.claim(DEMO_USER_ID, "stable"), range(8)))
    assert results.count("CLAIMED") == 1 and results.count("COOLDOWN") == 7
    key = f"{gate.prefix}:{DEMO_USER_ID}:stable"
    assert 0 <= gate.client.ttl(key) <= 1
    gate.client.pexpire(key, 1)
    import time

    time.sleep(0.02)
    assert gate.claim(DEMO_USER_ID, "stable") == "CLAIMED"


def test_redis_unavailable_persists_suppression_no_proposal(task):
    service = ProactiveService(cooldown=RedisCooldown("redis://127.0.0.1:1/0"))
    result = evaluate(service, task)
    assert result.status == "SUPPRESSED" and result.reason == "REDIS_UNAVAILABLE"
    assert result.proposal is None and count(ActionProposal) == 0
    with SessionLocal() as session:
        audit = session.scalar(select(AuditEvent))
        assert audit.event_type == "PROACTIVE_TRIGGER_SUPPRESSED"
        assert audit.safe_metadata["reason"] == "REDIS_UNAVAILABLE"


def test_duplicate_events_and_redis_expiration_do_not_resurface(service, task):
    first = evaluate(service, task, "event-key")
    replay = evaluate(service, task, "event-key")
    assert first.trigger_id == replay.trigger_id and first.proposal.id == replay.proposal.id
    duplicate = evaluate(service, task)
    assert duplicate.reason == "COOLDOWN" and duplicate.proposal is None
    service.cooldown.client.delete(*service.cooldown.client.keys(f"{service.cooldown.prefix}:*"))
    assert evaluate(service, task).reason == "DURABLE_DUPLICATE"
    assert count(ActionProposal) == 1


def test_evaluation_idempotency_conflict(service, task):
    evaluate(service, task, "same-key")
    with pytest.raises(HTTPException) as caught:
        service.evaluate(
            ContextEventInput(
                task_id=task["id"], event_type="TASK_UPDATED", idempotency_key="same-key"
            ),
            "test",
        )
    assert caught.value.status_code == 409


def test_communication_agent_and_kernel_capabilities(task):
    clock = FixtureClock()
    situation, _ = ProactiveTriggerEngine(clock).analyze(demo_meeting(clock))
    payload = CommunicationInput(task_id=task["id"], trace_id=uuid4(), situation=situation)
    records = []
    runtime = KernelRuntime(FixtureModelProvider(), records.append)
    register_communication(runtime)
    result = asyncio.run(CommunicationAgent().execute(payload, runtime, uuid4()))
    assert "2:06 PM" in result.intent.content
    assert records[0].plugin == "CommunicationPlugin" and records[0].trace_id == payload.trace_id
    assert runtime.discover("COMMUNICATION") == ["CommunicationPlugin.resolve_demo_attendee"]
    for agent, plugin, function in [
        ("COMMUNICATION", "CalendarPlugin", "get_events_for_date"),
        ("COMMUNICATION", "CommunicationPlugin", "execute"),
        ("PLANNER", "CommunicationPlugin", "resolve_demo_attendee"),
    ]:
        with pytest.raises(PermissionError):
            asyncio.run(
                runtime.invoke(
                    agent, uuid4(), payload.trace_id, plugin, function, EmptyQuery(), Attendee
                )
            )
    assert not hasattr(CommunicationAgent(), "executor") and not hasattr(runtime, "executor")
    assert not hasattr(runtime.kernel.plugins["CommunicationPlugin"], "execute")


@pytest.mark.parametrize(
    "changes",
    [
        {"approval": True},
        {"status": "APPROVED"},
        {"content": "x" * 1001},
        {"content": " "},
        {"recipient": "x" * 121},
        {"channel": "EMAIL"},
        {"action_type": "SEND_SMS"},
    ],
)
def test_action_intent_rejects_untrusted_fields(changes):
    clock = FixtureClock()
    situation, _ = ProactiveTriggerEngine(clock).analyze(demo_meeting(clock))
    fields = dict(
        recipient="Meeting attendee",
        content="Draft",
        reason="Risk",
        task_id=uuid4(),
        trace_id=uuid4(),
        context_evidence=situation,
    )
    fields.update(changes)
    with pytest.raises(ValidationError):
        ActionIntent(**fields)


def test_provider_cannot_self_authorize(service, task):
    class Forged(FixtureModelProvider):
        async def generate_communication(self, payload, attendee):
            response = await super().generate_communication(payload, attendee)
            import json

            data = json.loads(response.payload_json)
            data["intent"]["approval"] = True
            return ProviderResponse(payload_json=json.dumps(data))

    service.provider = Forged()
    result = evaluate(service, task)
    assert result.status == "FAILED" and result.reason == "COMMUNICATION_FAILED"
    assert count(ActionProposal) == count(ActionExecution) == 0


def test_proposal_hash_policy_approval_and_audit(service, task):
    item = proposal(service, task)
    assert item.status == "PENDING_APPROVAL" and item.policy_decision == "REQUIRE_APPROVAL"
    assert evaluate_policy(item)[0] == "REQUIRE_APPROVAL"
    assert item.payload_hash == payload_hash(item)
    with pytest.raises(HTTPException):
        mutate(service, item, "execute")
    approved = mutate(service, item, "approve")
    assert approved.approval.payload_hash == approved.proposal.payload_hash
    assert approved.approval.user_id == DEMO_USER_ID
    result = mutate(service, item, "execute")
    assert (
        result.execution.status == "DONE"
        and result.execution.receipt["external_message_sent"] is False
    )
    with SessionLocal() as session:
        events = session.scalars(select(AuditEvent)).all()
        assert {
            "PROACTIVE_TRIGGER_CREATED",
            "ACTION_PROPOSED",
            "APPROVAL_GRANTED",
            "ACTION_EXECUTED",
        } <= {e.event_type for e in events}
        assert all(e.trace_id == item.trace_id for e in events)
        assert all(e.safe_metadata["correlation_id"] == "test-correlation" for e in events)


def test_reject_cannot_execute(service, task):
    item = proposal(service, task)
    assert mutate(service, item, "reject").proposal.status == "REJECTED"
    with pytest.raises(HTTPException):
        mutate(service, item, "execute")
    assert count(ActionExecution) == 0


def test_edit_supersedes_approved_payload_and_requires_reapproval(service, task):
    item = proposal(service, task)
    mutate(service, item, "approve")
    edited = mutate(
        service,
        item,
        "edit",
        "edit-key",
        content="Running 15 minutes late.",
        recipient="New demo attendee",
    )
    assert edited.proposal.id != item.id and edited.proposal.supersedes_id == item.id
    assert edited.proposal.payload_hash != item.payload_hash
    assert edited.proposal.status == "PENDING_APPROVAL" and edited.approval is None
    assert service.get(item.id, "test").proposal.status == "SUPERSEDED"
    retry = mutate(
        service,
        item,
        "edit",
        "edit-key",
        content="Running 15 minutes late.",
        recipient="New demo attendee",
    )
    assert retry.proposal.id == edited.proposal.id and count(ActionProposal) == 2
    for target in (item, edited.proposal):
        with pytest.raises(HTTPException):
            mutate(service, target, "execute")
    mutate(service, edited.proposal, "approve")
    assert mutate(service, edited.proposal, "execute").execution.status == "DONE"


@pytest.mark.parametrize("target", ["proposal", "approval"])
def test_expiration_enforced_and_audited(service, task, target):
    item = proposal(service, task)
    if target == "approval":
        mutate(service, item, "approve")
    service.clock.time += timedelta(minutes=10 if target == "proposal" else 5)
    with pytest.raises(HTTPException):
        mutate(service, item, "execute")
    assert service.get(item.id, "test").proposal.status == "EXPIRED"
    assert count(ActionExecution) == 0
    with SessionLocal() as session:
        assert session.scalar(select(AuditEvent).where(AuditEvent.event_type == "ACTION_EXPIRED"))


@pytest.mark.parametrize(
    "field,value",
    [
        ("content", "Tampered"),
        ("recipient", "Tampered recipient"),
        ("channel", "SMS"),
        ("policy_version", "forged"),
    ],
)
def test_tampering_after_approval_cannot_execute(service, task, field, value):
    item = proposal(service, task)
    mutate(service, item, "approve")
    with SessionLocal.begin() as session:
        setattr(session.get(ActionProposal, item.id), field, value)
    with pytest.raises(HTTPException):
        mutate(service, item, "execute")
    assert count(ActionExecution) == 0


@pytest.mark.parametrize("field", ["user_id", "payload_hash", "proposal_id"])
def test_wrong_approval_binding_rejected(service, task, devices, client, field):
    item = proposal(service, task)
    mutate(service, item, "approve")
    other_task = client.post(
        "/api/v1/tasks", json={"title": "Other", "origin_device_id": devices["DESKTOP"]}
    ).json()
    other = proposal(service, other_task)
    with SessionLocal.begin() as session:
        approval = session.scalar(
            select(ApprovalDecision).where(ApprovalDecision.proposal_id == item.id)
        )
        if field == "payload_hash":
            approval.payload_hash = "0" * 64
        elif field == "proposal_id":
            approval.proposal_id = other.id
        else:
            from app.models import User

            user = User(name="Other")
            session.add(user)
            session.flush()
            approval.user_id = user.id
    with pytest.raises(HTTPException):
        mutate(service, item, "execute")
    assert count(ActionExecution) == 0


def test_idempotent_execution_different_keys_and_concurrency(service, task):
    item = proposal(service, task)
    mutate(service, item, "approve")
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: mutate(service, item, "execute"), range(8)))
    assert len({r.execution.id for r in results}) == 1 and count(ActionExecution) == 1
    assert count(ApprovalDecision) == 1
    first = results[0].execution
    service.clock.time += timedelta(days=1)
    assert mutate(service, item, "execute", first.idempotency_key).execution.id == first.id


@pytest.mark.parametrize("operations", [("approve", "reject"), ("edit", "approve")])
def test_decision_races_remain_authorized(service, task, operations):
    item = proposal(service, task)

    def invoke(op):
        try:
            return mutate(
                service,
                item,
                op,
                **(
                    {"content": "Edited draft", "recipient": item.recipient} if op == "edit" else {}
                ),
            )
        except HTTPException as error:
            return error.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(invoke, operations))
    if operations[0] == "approve":
        assert sum(result == 409 for result in results) == 1 and count(ApprovalDecision) == 1
    else:
        proposals = service.list_proposals(UUID(task["id"]), "test")
        assert len(proposals) == 2
        assert any(p.status == "SUPERSEDED" for p in proposals)
        new = next(p for p in proposals if p.supersedes_id)
        assert new.status == "PENDING_APPROVAL"
        with pytest.raises(HTTPException):
            mutate(service, new, "execute")
    assert count(ActionExecution) == 0


def test_duplicate_evaluation_race(service, task):
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(lambda _: evaluate(service, task), range(5)))
    assert sum(r.status == "SURFACED" for r in results) == 1 and count(ActionProposal) == 1


def test_simulated_path_no_external_http_or_socket(monkeypatch, task):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network attempted by simulation")

    clock = FixtureClock()
    situation, _ = ProactiveTriggerEngine(clock).analyze(demo_meeting(clock))
    payload = CommunicationInput(task_id=task["id"], trace_id=uuid4(), situation=situation)
    runtime = KernelRuntime(FixtureModelProvider())
    register_communication(runtime)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket.socket, "connect_ex", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(httpx.Client, "request", forbidden)
    monkeypatch.setattr(httpx.AsyncClient, "request", forbidden)
    import urllib.request

    import requests

    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    monkeypatch.setattr(requests.sessions.Session, "request", forbidden)
    result = asyncio.run(CommunicationAgent().execute(payload, runtime, uuid4()))
    receipt = ActionExecutor().execute_authorized(result.intent.model_dump(mode="json"), "a" * 64)
    assert receipt["external_message_sent"] is False
    assert SimulatedCommunicationAdapter().execute(
        {}, "abc"
    ) == SimulatedCommunicationAdapter().execute({}, "abc")


def test_api_validation_trace_and_cross_device_persistence(client, task, service, devices):
    from app.main import app

    app.dependency_overrides[get_service] = lambda: service
    try:
        response = client.post(
            "/api/v1/proactive/evaluate",
            json={"task_id": task["id"], "idempotency_key": "api-evaluate"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert response.headers["X-Trace-ID"] == data["trace_id"]
        proposal_id = data["proposal"]["id"]
        for operation in ("approve", "execute"):
            forged = client.post(
                f"/api/v1/proposals/{proposal_id}/{operation}",
                json={"idempotency_key": "bad", "status": "APPROVED"},
            )
            assert forged.status_code == 422
        for source, target in [("DESKTOP", "WEARABLE"), ("WEARABLE", "MOBILE")]:
            assert (
                client.post(
                    f"/api/v1/tasks/{task['id']}/handoff",
                    json={
                        "source_device_id": devices[source],
                        "target_device_id": devices[target],
                        "idempotency_key": str(uuid4()),
                    },
                ).status_code
                == 200
            )
            details = client.get(f"/api/v1/proposals/{proposal_id}").json()
            assert (
                details["proposal"]["task_id"] == task["id"]
                and details["proposal"]["trace_id"] == data["trace_id"]
            )
        approved = client.post(
            f"/api/v1/proposals/{proposal_id}/approve", json={"idempotency_key": "approve"}
        )
        assert approved.status_code == 200
        assert (
            client.post(
                f"/api/v1/proposals/{proposal_id}/execute", json={"idempotency_key": "execute"}
            ).json()["execution"]["status"]
            == "DONE"
        )
        assert len(client.get(f"/api/v1/tasks/{task['id']}/audit-events").json()) == 4
        assert client.get(f"/api/v1/proposals/{uuid4()}").status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_mutation_keys_bind_operation_and_edited_payload(service, task):
    item = proposal(service, task)
    mutate(service, item, "approve", "decision-key")
    with pytest.raises(HTTPException) as conflict:
        mutate(service, item, "reject", "decision-key")
    assert conflict.value.detail["code"] == "IDEMPOTENCY_CONFLICT"
    edited = mutate(
        service, item, "edit", "edit-binding", content="Original edit", recipient=item.recipient
    )
    with pytest.raises(HTTPException) as conflict:
        mutate(
            service,
            item,
            "edit",
            "edit-binding",
            content="Different edit",
            recipient=item.recipient,
        )
    assert conflict.value.detail["code"] == "IDEMPOTENCY_CONFLICT"
    assert count(ActionProposal) == 2 and edited.proposal.status == "PENDING_APPROVAL"


def test_execute_expiration_race_never_executes_at_boundary(service, task):
    item = proposal(service, task)
    mutate(service, item, "approve")
    service.clock.time += timedelta(minutes=5)
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = []

        def attempt(_):
            try:
                mutate(service, item, "execute")
            except HTTPException as error:
                return error.status_code

        outcomes = list(pool.map(attempt, range(2)))
    assert outcomes == [409, 409] and count(ActionExecution) == 0


def test_failed_simulation_records_safe_failure_and_cannot_repeat(service, task):
    item = proposal(service, task)
    mutate(service, item, "approve")

    class BrokenExecutor:
        calls = 0

        def execute_authorized(self, payload, digest):
            self.calls += 1
            raise RuntimeError("private transport detail must not be persisted")

    executor = BrokenExecutor()
    service.executor = executor
    first = mutate(service, item, "execute")
    second = mutate(service, item, "execute")
    assert executor.calls == 1 and first.execution.id == second.execution.id
    assert first.execution.safe_error == "SIMULATION_FAILED" and first.execution.receipt == {}
    assert first.proposal.status == "FAILED"


def test_replay_with_new_key_still_binds_that_key(service, task):
    item = proposal(service, task)
    mutate(service, item, "approve", "first-approve")
    mutate(service, item, "approve", "replay-approve")
    with pytest.raises(HTTPException) as conflict:
        mutate(service, item, "edit", "replay-approve", recipient=item.recipient, content="New")
    assert conflict.value.detail["code"] == "IDEMPOTENCY_CONFLICT"
    mutate(service, item, "execute", "first-execute")
    mutate(service, item, "execute", "replay-execute")
    with pytest.raises(HTTPException) as conflict:
        mutate(service, item, "reject", "replay-execute")
    assert conflict.value.detail["code"] == "IDEMPOTENCY_CONFLICT"
    assert count(ActionExecution) == 1
