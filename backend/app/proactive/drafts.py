"""Owned, bounded preference drafts. Fixture default; no action capability.

Uses existing context events, event jobs, triggers, proposals and audit records.
The support contract is Phase 9's named cuisine/beverage subset, not entailment.
"""

import asyncio
import os
import time
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import HTTPException
from pydantic import Field
from sqlalchemy import and_, or_, select

from app.database import SessionLocal
from app.events.models import Job, Outbox
from app.inference.grounding import preference_keys, select_context
from app.inference.providers import GroundedFixture, selected
from app.inference.service import (
    eligible,
    memory_binding,
    revalidate_evidence,
    verified_output,
    verified_selection,
)
from app.intelligence.contracts import Contract
from app.memory.models import MemoryRecord
from app.memory.service import digest
from app.model_routing.contracts import ModelRequest
from app.model_routing.providers import ProviderFailure, validate_result
from app.models import Device, User
from app.proactive.clock import SystemClock
from app.proactive.models import ActionProposal, ApprovalDecision, ContextEvent, ProactiveTrigger
from app.proactive.policy import payload_hash
from app.proactive.service import ProactiveService
from app.schemas import IdempotencyKey
from app.security.identity import current_user_id, principal
from app.security.models import DeviceRegistration, Identity
from app.service import fail, find_task

SOURCE = "OWNED_CONTEXT_V1"
PURPOSE = "PREFERENCE_RECOMMENDATION"
TERMINAL = {"CANCELLED", "EXPIRED", "FAILED", "REJECTED"}


def permission_binding(session):
    identity = principal.get()
    if identity.mode == "demo":
        return {"mode": "demo"}  # Explicit replay identity; never claimed as live auth.
    row = session.get(Identity, identity.identity_id) if identity.identity_id else None
    if row is None:
        fail(403, "CONTEXT_AUTH_REVOKED", "A current owner identity is required.")
    registration = session.get(DeviceRegistration, identity.device_id)
    binding = {
        "mode": identity.mode,
        "identity_id": str(row.id),
        "version": row.version,
        "device_id": str(identity.device_id),
        "device_version": registration.version if registration else 0,
    }
    check_permission(session, binding)
    return binding


def check_permission(session, binding):
    if binding["mode"] == "demo":
        return
    identity = session.scalar(
        select(Identity).where(Identity.id == UUID(binding["identity_id"])).with_for_update()
    )
    device = session.scalar(
        select(Device).where(Device.id == UUID(binding["device_id"])).with_for_update()
    )
    registration = session.scalar(
        select(DeviceRegistration)
        .where(DeviceRegistration.device_id == UUID(binding["device_id"]))
        .with_for_update()
    )
    if (
        not identity
        or not identity.enabled
        or "owner" not in identity.roles
        or identity.user_id != current_user_id()
        or identity.version != binding["version"]
        or not device
        or device.user_id != current_user_id()
        or (
            registration and (not registration.enabled or registration.user_id != current_user_id())
        )
        or (registration.version if registration else 0) != binding["device_version"]
    ):
        fail(403, "CONTEXT_AUTH_REVOKED", "Owner or device authorization changed.")


class DraftInput(Contract):
    task_id: UUID
    query: str = Field(min_length=1, max_length=200)
    memory_ids: list[UUID] = Field(default_factory=list, max_length=2)
    idempotency_key: IdempotencyKey
    expires_in_seconds: int = Field(default=600, ge=30, le=600)


def owner(session, task_id):
    identity = principal.get()
    if identity is None or "owner" not in identity.roles:
        fail(403, "FORBIDDEN", "An authenticated owner is required.")
    session.scalar(select(User.id).where(User.id == current_user_id()).with_for_update())
    return find_task(session, task_id)


def sources(session, payload):
    ids = payload.memory_ids
    keys = preference_keys(payload.query)
    if len(set(ids)) != len(ids) or not keys:
        fail(409, "UNSUPPORTED_CONTEXT", "Use a named cuisine or beverage preference question.")
    query = eligible(current_user_id(), payload.task_id)
    query = (
        query.where(MemoryRecord.id.in_(ids))
        if ids
        else query.where(
            or_(
                *(
                    and_(MemoryRecord.subject == subject, MemoryRecord.predicate == predicate)
                    for subject, predicate in keys
                )
            )
        )
    )
    rows = session.scalars(query.order_by(MemoryRecord.id).limit(32).with_for_update()).all()
    if (ids and len(rows) != len(ids)) or not rows:
        fail(409, "CONTEXT_UNAVAILABLE", "An owned eligible source is required.")
    if not ids:
        # One source per requested fact; final conflict validation still scans
        # every eligible value for these keys, including beyond this bounded read.
        unique = {}
        for memory in rows:
            unique.setdefault((memory.subject, memory.predicate), memory)
        rows = list(unique.values())
    evidence = [
        {
            "id": str(m.id),
            "kind": "MEMORY",
            "text": m.normalized_text,
            "subject": m.subject,
            "predicate": m.predicate,
            "value": m.value,
            "origin": m.origin,
            "binding": memory_binding(m),
        }
        for m in rows
    ]
    chosen, _ = select_context(payload.query, evidence, output_tokens=96, selection=True)
    if len(chosen) != len(evidence) or revalidate_evidence(
        evidence, payload.task_id, session=session
    ):
        fail(409, "UNSUPPORTED_CONTEXT", "Sources must be supported, bounded and conflict-free.")
    return evidence


def event_for(session, event_id):
    row = session.scalar(
        select(ContextEvent).where(
            ContextEvent.id == event_id,
            ContextEvent.user_id == current_user_id(),
            ContextEvent.source == SOURCE,
        )
    )
    if row is None:
        fail(404, "DRAFT_NOT_FOUND", "Draft request not found.")
    owner(session, row.task_id)
    # Reload after the owner lock: cancellation and finalization serialize here.
    session.refresh(row)
    return row


def audit(session, row, state):
    ProactiveService(clock=SystemClock()).audit(
        session, "OWNED_DRAFT_" + state, row, str(row.trace_id), purpose=PURPOSE
    )


def transition(session, row, state, error=None):
    row.payload = {**row.payload, "state": state, "error": error}
    audit(session, row, state)


def validate(session, row):
    check_permission(session, row.payload["authorization"])
    if datetime.now(UTC) >= datetime.fromisoformat(row.payload["expires_at"]):
        fail(409, "DRAFT_EXPIRED", "Draft context expired.")
    if revalidate_evidence(row.payload["evidence"], row.task_id, session=session):
        fail(409, "CONFLICTING_EVIDENCE", "Conflicting sources require refusal.")


def invalidate(session, row):
    """Expire stale drafts on every read/mutation as well as before final commit."""
    if row.payload["state"] in TERMINAL:
        return
    try:
        validate(session, row)
    except HTTPException as error:
        transition(session, row, "EXPIRED", error.detail["code"])
        proposal = session.scalar(
            select(ActionProposal).where(ActionProposal.trace_id == row.trace_id)
        )
        if proposal:
            proposal.status = "EXPIRED"


def view(session, row):
    invalidate(session, row)
    state = row.payload["state"]
    visible = state == "PENDING_APPROVAL"
    proposal = session.scalar(select(ActionProposal).where(ActionProposal.trace_id == row.trace_id))
    return {
        "id": str(row.id),
        "task_id": str(row.task_id),
        "trace_id": str(row.trace_id),
        "purpose": PURPOSE,
        "state": state,
        "error": row.payload.get("error"),
        "expires_at": row.payload["expires_at"],
        "proposal_id": str(proposal.id) if proposal else None,
        "content": proposal.content if proposal and visible else None,
        "evidence": [
            {k: x[k] for k in ("id", "text", "origin", "binding")} for x in row.payload["evidence"]
        ]
        if visible
        else [],
        "verification": "EXACT_SUPPORTED_QUOTES" if visible else "NOT_CURRENTLY_VERIFIED",
        "approval_required": True,
        "execution_enabled": False,
        "simulation": row.payload["mode"] == "FIXTURE",
        "provider": row.payload.get("provider", row.payload["mode"]),
        "latency_ms": row.payload.get("latency_ms"),
        "input_tokens": row.payload.get("input_tokens"),
        "output_tokens": row.payload.get("output_tokens"),
        "usage_source": row.payload.get("usage_source", "UNKNOWN"),
    }


class OwnedDraftService:
    def __init__(self, provider=None):
        # Reads/cancellation never activate or require a provider. Real selection
        # is a private operator setting, never an API input, and defaults off.
        self.mode = os.environ.get("OWNED_DRAFT_MODE", "FIXTURE")
        self.provider = provider

    def generator(self):
        if self.mode not in {"FIXTURE", "LOCAL_REAL"}:
            fail(409, "DRAFT_PROVIDER_DISABLED", "Draft generation is disabled.")
        provider = self.provider or (
            GroundedFixture() if self.mode == "FIXTURE" else selected("LOCAL_REAL", "STRUCTURED")
        )
        if self.mode == "FIXTURE" and provider.spec.kind != "FIXTURE":
            fail(409, "DRAFT_PROVIDER_DISABLED", "Fixture mode requires fixture generation.")
        if self.mode == "LOCAL_REAL" and (
            provider.spec.kind != "LOCAL"
            or not provider.config.managed_residency
            or provider.config.grounded_generation_contract != "SELECTION_V1"
        ):
            fail(
                409, "DRAFT_PROVIDER_DISABLED", "Real drafts require managed selection generation."
            )
        return provider

    def create(self, payload):
        signature = digest(payload.model_dump(mode="json", exclude={"idempotency_key"}))
        with SessionLocal.begin() as session:
            task = owner(session, payload.task_id)
            prior = session.scalar(
                select(ContextEvent).where(
                    ContextEvent.task_id == task.id,
                    ContextEvent.idempotency_key == payload.idempotency_key,
                )
            )
            if prior:
                if prior.source != SOURCE or prior.request_hash != signature:
                    fail(409, "IDEMPOTENCY_CONFLICT", "Request key has different intent.")
                return view(session, prior)
            evidence = sources(session, payload)
            self.generator()  # Validate mode/config without acquiring a runtime.
            authorization = permission_binding(session)
            now = datetime.now(UTC)
            row = ContextEvent(
                id=uuid4(),
                user_id=task.user_id,
                task_id=task.id,
                event_type="TASK_UPDATED",
                timestamp=now,
                source=SOURCE,
                trace_id=uuid4(),
                idempotency_key=payload.idempotency_key,
                request_hash=signature,
                payload={
                    "mode": self.mode,
                    "authorization": authorization,
                    "query": payload.query,
                    "evidence": evidence,
                    "state": "QUEUED",
                    "expires_at": (now + timedelta(seconds=payload.expires_in_seconds)).isoformat(),
                },
            )
            session.add(row)
            session.flush()  # Existing outbox mapper writes the trigger in this transaction.
            audit(session, row, "REQUESTED")
            audit(session, row, "QUEUED")
            return view(session, row)

    def read(self, event_id):
        with SessionLocal.begin() as session:
            return view(session, event_for(session, event_id))

    def list(self, task_id):
        with SessionLocal.begin() as session:
            owner(session, task_id)
            return [
                view(session, row)
                for row in session.scalars(
                    select(ContextEvent)
                    .where(
                        ContextEvent.task_id == task_id,
                        ContextEvent.user_id == current_user_id(),
                        ContextEvent.source == SOURCE,
                    )
                    .order_by(ContextEvent.timestamp.desc())
                    .limit(50)
                ).all()
            ]

    def cancel(self, event_id):
        with SessionLocal.begin() as session:
            row = event_for(session, event_id)
            invalidate(session, row)
            if row.payload["state"] not in TERMINAL:
                transition(session, row, "CANCELLED")
                proposal = session.scalar(
                    select(ActionProposal).where(ActionProposal.trace_id == row.trace_id)
                )
                if proposal:
                    proposal.status = "REJECTED"
            return view(session, row)

    def reject(self, proposal_id, payload):
        with SessionLocal.begin() as session:
            proposal = session.scalar(
                select(ActionProposal).where(
                    ActionProposal.id == proposal_id, ActionProposal.user_id == current_user_id()
                )
            )
            if proposal is None:
                fail(404, "PROPOSAL_NOT_FOUND", "Proposal not found.")
            row = event_for(session, proposal.situation["context_event_id"])
            invalidate(session, row)
            if row.payload["state"] == "REJECTED":
                return ProactiveService().detail(session, proposal)
            if row.payload["state"] != "PENDING_APPROVAL":
                fail(409, "DRAFT_NOT_REJECTABLE", "Draft is no longer pending.")
            now = datetime.now(UTC)
            session.add(
                ApprovalDecision(
                    proposal_id=proposal.id,
                    user_id=row.user_id,
                    decision="REJECTED",
                    payload_hash=proposal.payload_hash,
                    created_at=now,
                    expires_at=proposal.expires_at,
                )
            )
            proposal.status = "REJECTED"
            transition(session, row, "REJECTED")
            session.flush()
            return ProactiveService().detail(session, proposal)

    def process(self, job_id):
        with SessionLocal.begin() as session:
            job = session.get(Job, job_id)
            row = event_for(session, UUID(session.get(Outbox, job.event_id).payload["resource_id"]))
            session.refresh(job)  # It may have completed while this caller waited for the owner.
            if row.user_id != job.user_id or row.task_id != job.task_id:
                fail(409, "JOB_BINDING_INVALID", "Job context binding mismatch.")
            invalidate(session, row)
            if job.state == "DONE" or row.payload["state"] in TERMINAL:
                job.state = "DONE" if job.result_id else "DEAD"
                return
            if row.payload["mode"] != self.mode or (
                self.mode == "LOCAL_REAL" and row.payload["state"] == "RUNNING"
            ):
                transition(session, row, "FAILED", "DRAFT_MODE_CHANGED_OR_INTERRUPTED")
                job.state = "DEAD"
                return  # A real generation is never retried after ambiguous interruption.
            transition(session, row, "RUNNING")
            device = session.get(Device, find_task(session, row.task_id).current_device_id).type
            evidence, query, task_id, trace_id = (
                row.payload["evidence"],
                row.payload["query"],
                row.task_id,
                row.trace_id,
            )
        try:
            provider = self.generator()
            selection = self.mode == "LOCAL_REAL"
            context = {
                "query": query,
                "evidence": [{"id": x["id"], "text": x["text"]} for x in evidence],
            }
            if selection:
                chosen, context = select_context(query, evidence, 96, selection=True)
                if len(chosen) != len(evidence):
                    fail(409, "DRAFT_CONTEXT_LIMIT", "Exact sources must fit the verified budget.")
            request = ModelRequest(
                task_id=task_id,
                user_id=current_user_id(),
                trace_id=trace_id,
                purpose="GROUNDED_SELECTION" if selection else "GROUNDED",
                structured_input=context,
                max_output_tokens=96,
                required_capabilities=["STRUCTURED"],
                privacy_class="PERSONAL",
                current_device=device,
            )

            async def generate():
                # Managed LocalProvider already separates 30s acquisition from
                # the 8s inference deadline and releases leases in finally.
                if selection:
                    return await provider.generate(request)
                return await asyncio.wait_for(provider.generate(request), timeout=8)

            started = time.perf_counter()
            result = validate_result(request, asyncio.run(generate()), provider.spec)
            if result.finish_reason != ("stop" if selection else "fixture"):
                fail(409, "DRAFT_INCOMPLETE", "Draft generation did not finish normally.")
            latency = round((time.perf_counter() - started) * 1000, 3)
            answer = (
                verified_selection(result.output, evidence, query)[0]
                if selection
                else verified_output(result.output, evidence, query=query)
            )
            if answer.abstain:
                fail(409, "DRAFT_ABSTAINED", "No supported recommendation was produced.")
            content = " ".join(x.quote for x in answer.claims)
            if len(content) > 1000:
                fail(409, "DRAFT_TOO_LARGE", "Draft exceeds its bound.")
            with SessionLocal.begin() as session:
                row = event_for(session, row.id)
                job = session.get(Job, job_id)
                invalidate(session, row)
                if row.payload["state"] in TERMINAL:
                    job.state = "DEAD"
                    return
                if job.state == "DONE":
                    return
                validate(session, row)
                # Verification and pending persistence share this transaction;
                # do not expose an intermediate durable state or enqueue work.
                audit(session, row, "EVIDENCE_VERIFIED")
                row.payload = {
                    **row.payload,
                    "latency_ms": latency,
                    "provider": provider.spec.provider,
                    "model": provider.spec.model,
                    "input_tokens": result.input_tokens,
                    "output_tokens": result.output_tokens,
                    "usage_source": result.usage_source,
                }
                trigger = ProactiveTrigger(
                    event_id=row.id,
                    user_id=row.user_id,
                    task_id=row.task_id,
                    trace_id=row.trace_id,
                    fingerprint=row.request_hash,
                    status="SURFACED",
                    reason="OWNED_SUPPORTED_DRAFT",
                    situation={"draft_contract": SOURCE},
                    created_at=datetime.now(UTC),
                    agent_record={
                        "agent": "BOUNDED_PREFERENCE_DRAFT",
                        "simulation": self.mode == "FIXTURE",
                        "status": "DONE",
                        "purpose": PURPOSE,
                    },
                )
                session.add(trigger)
                session.flush()
                proposal = ActionProposal(
                    user_id=row.user_id,
                    task_id=row.task_id,
                    trigger_id=trigger.id,
                    trace_id=row.trace_id,
                    action_type="LOCAL_RECOMMENDATION",
                    recipient="owner",
                    channel="LOCAL",
                    content=content,
                    reason="Verified owned preference evidence.",
                    status="PENDING_APPROVAL",
                    policy_version=SOURCE,
                    policy_decision="REQUIRE_APPROVAL",
                    policy_reason="Draft only; execution disabled.",
                    situation={"draft_contract": SOURCE, "context_event_id": str(row.id)},
                    created_at=datetime.now(UTC),
                    expires_at=datetime.fromisoformat(row.payload["expires_at"]),
                )
                proposal.payload_hash = payload_hash(proposal)
                session.add(proposal)
                session.flush()
                job.state, job.result_id, job.updated_at = "DONE", proposal.id, datetime.now(UTC)
                transition(session, row, "PENDING_APPROVAL")
        except (
            HTTPException,
            ValueError,
            TypeError,
            KeyError,
            TimeoutError,
            ProviderFailure,
        ) as error:
            with SessionLocal.begin() as session:
                row = event_for(session, row.id)
                job = session.get(Job, job_id)
                if row.payload["state"] not in TERMINAL:
                    code = (
                        error.detail["code"]
                        if isinstance(error, HTTPException)
                        else "DRAFT_TIMEOUT"
                        if isinstance(error, TimeoutError)
                        else "DRAFT_INVALID"
                    )
                    transition(session, row, "FAILED", code)
                job.state = "DEAD"
