import asyncio
import hashlib
import json
import logging
from datetime import timedelta
from uuid import uuid4

from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.intelligence.plugins import KernelRuntime
from app.intelligence.provider import FixtureModelProvider
from app.models import User
from app.proactive.clock import FixtureClock
from app.proactive.communication import ActionExecutor, CommunicationAgent, register_communication
from app.proactive.contracts import (
    ApprovalRead,
    CommunicationInput,
    EvaluationRead,
    ExecutionRead,
    ProposalDetail,
    ProposalRead,
)
from app.proactive.models import (
    ActionExecution,
    ActionMutation,
    ActionProposal,
    ApprovalDecision,
    AuditEvent,
    ContextEvent,
    ProactiveTrigger,
)
from app.proactive.policy import POLICY_VERSION, canonical_payload, evaluate_policy, payload_hash
from app.proactive.trigger import ProactiveTriggerEngine, RedisCooldown, demo_meeting
from app.security.identity import current_user_id
from app.service import fail, find_task

logger = logging.getLogger("nova.proactive")


def request_hash(operation: str, payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(
            {"operation": operation, "payload": payload}, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()


class ProactiveService:
    def __init__(
        self, clock=None, cooldown=None, provider=None, executor=None, trace_id=None, threshold=2
    ):
        # The public Phase 3 demo explicitly uses a frozen clock, never wall-clock acceptance.
        self.clock = clock or FixtureClock()
        self.cooldown = cooldown or RedisCooldown(settings.redis_url)
        self.provider = provider or FixtureModelProvider()
        self.executor = executor or ActionExecutor()
        self.trace_id = trace_id
        self.threshold = threshold

    def audit(self, session, event_type, owner, correlation_id, **metadata):
        proposal_id = owner.id if isinstance(owner, ActionProposal) else None
        session.add(
            AuditEvent(
                event_type=event_type,
                user_id=owner.user_id,
                task_id=owner.task_id,
                proposal_id=proposal_id,
                trace_id=owner.trace_id,
                created_at=self.clock.now(),
                safe_metadata={"correlation_id": correlation_id, **metadata},
            )
        )
        logger.info(
            event_type,
            extra={
                "trace_id": str(owner.trace_id),
                "task_id": str(owner.task_id),
                "correlation_id": correlation_id,
            },
        )

    def _evaluation(self, session, trigger):
        proposal = session.scalar(
            select(ActionProposal).where(
                ActionProposal.trigger_id == trigger.id, ActionProposal.supersedes_id.is_(None)
            )
        )
        return EvaluationRead(
            trigger_id=trigger.id,
            trace_id=trigger.trace_id,
            status=trigger.status,
            reason=trigger.reason,
            situation=trigger.situation,
            proposal=ProposalRead.model_validate(proposal) if proposal else None,
        )

    def evaluate(self, payload, correlation_id):
        digest = request_hash(
            "evaluate", payload.model_dump(mode="json", exclude={"idempotency_key"})
        )
        with SessionLocal.begin() as session:
            # User-level serialization covers the same meeting across different tasks.
            session.scalar(select(User).where(User.id == current_user_id()).with_for_update())
            task = find_task(session, payload.task_id, lock=True)
            prior = session.scalar(
                select(ContextEvent).where(
                    ContextEvent.task_id == task.id,
                    ContextEvent.idempotency_key == payload.idempotency_key,
                )
            )
            if prior:
                if prior.request_hash != digest:
                    fail(409, "IDEMPOTENCY_CONFLICT", "Evaluation key belongs to another input.")
                return self._evaluation(
                    session,
                    session.scalar(
                        select(ProactiveTrigger).where(ProactiveTrigger.event_id == prior.id)
                    ),
                )
            engine = ProactiveTriggerEngine(self.clock, self.threshold)
            situation, reason = engine.analyze(demo_meeting(self.clock, str(task.id)))
            fingerprint = engine.fingerprint(task.user_id, situation)
            event = ContextEvent(
                user_id=task.user_id,
                task_id=task.id,
                event_type=payload.event_type,
                timestamp=self.clock.now(),
                source="DEMO_FIXTURE",
                payload=situation.model_dump(mode="json"),
                trace_id=self.trace_id or uuid4(),
                idempotency_key=payload.idempotency_key,
                request_hash=digest,
            )
            session.add(event)
            session.flush()
            if reason == "SURFACE":
                claim = self.cooldown.claim(task.user_id, fingerprint)
                if claim != "CLAIMED":
                    reason = claim
                elif session.scalar(
                    select(ProactiveTrigger.id).where(
                        ProactiveTrigger.user_id == task.user_id,
                        ProactiveTrigger.fingerprint == fingerprint,
                        ProactiveTrigger.status == "SURFACED",
                    )
                ):
                    reason = "DURABLE_DUPLICATE"
            trigger = ProactiveTrigger(
                event_id=event.id,
                user_id=task.user_id,
                task_id=task.id,
                trace_id=event.trace_id,
                fingerprint=fingerprint,
                status="SURFACED" if reason == "SURFACE" else "SUPPRESSED",
                reason=reason,
                situation=situation.model_dump(mode="json"),
                created_at=self.clock.now(),
            )
            session.add(trigger)
            session.flush()
            if reason != "SURFACE":
                self.audit(
                    session, "PROACTIVE_TRIGGER_SUPPRESSED", trigger, correlation_id, reason=reason
                )
                return self._evaluation(session, trigger)
            records = []
            runtime = KernelRuntime(
                self.provider, lambda record: records.append(record.model_dump(mode="json"))
            )
            register_communication(runtime)
            run_id = uuid4()
            try:
                output = asyncio.run(
                    CommunicationAgent().execute(
                        CommunicationInput(
                            task_id=task.id, trace_id=trigger.trace_id, situation=situation
                        ),
                        runtime,
                        run_id,
                    )
                )
            except Exception:
                trigger.status, trigger.reason = "FAILED", "COMMUNICATION_FAILED"
                trigger.agent_record = {
                    "id": str(run_id),
                    "agent": "COMMUNICATION",
                    "status": "FAILED",
                    "trace_id": str(trigger.trace_id),
                    "tool_calls": records,
                    "safe_error": "COMMUNICATION_FAILED",
                }
                self.audit(
                    session,
                    "PROACTIVE_TRIGGER_SUPPRESSED",
                    trigger,
                    correlation_id,
                    reason=trigger.reason,
                )
                return self._evaluation(session, trigger)
            trigger.agent_record = {
                "id": str(run_id),
                "agent": "COMMUNICATION",
                "status": "DONE",
                "trace_id": str(trigger.trace_id),
                "provider": self.provider.provider_name,
                "tool_calls": records,
                "output": output.model_dump(mode="json"),
            }
            intent = output.intent
            proposal = ActionProposal(
                user_id=task.user_id,
                task_id=task.id,
                trigger_id=trigger.id,
                trace_id=trigger.trace_id,
                action_type=intent.action_type,
                recipient=intent.recipient,
                channel=intent.channel,
                content=intent.content,
                reason=intent.reason,
                status="PROPOSED",
                situation=situation.model_dump(mode="json"),
                created_at=self.clock.now(),
                expires_at=self.clock.now() + timedelta(minutes=10),
                policy_version=POLICY_VERSION,
            )
            self._policy(proposal)
            session.add(proposal)
            session.flush()
            self.audit(session, "PROACTIVE_TRIGGER_CREATED", trigger, correlation_id)
            self.audit(
                session,
                "ACTION_PROPOSED",
                proposal,
                correlation_id,
                policy=proposal.policy_decision,
                payload_hash=proposal.payload_hash,
            )
            return self._evaluation(session, trigger)

    def _policy(self, proposal):
        proposal.payload_hash = payload_hash(proposal)
        proposal.policy_decision, proposal.policy_reason = evaluate_policy(proposal)
        proposal.policy_version = POLICY_VERSION
        proposal.status = (
            "PENDING_APPROVAL" if proposal.policy_decision == "REQUIRE_APPROVAL" else "REJECTED"
        )

    def find_proposal(self, session, proposal_id, lock=False):
        query = select(ActionProposal).where(
            ActionProposal.id == proposal_id, ActionProposal.user_id == current_user_id()
        )
        proposal = session.scalar(query.with_for_update() if lock else query)
        if proposal is None:
            fail(404, "PROPOSAL_NOT_FOUND", "Proposal was not found.")
        return proposal

    def expire(self, session, proposal, correlation_id):
        if proposal.policy_version == "OWNED_CONTEXT_V1":
            from app.proactive.drafts import event_for, invalidate

            row = event_for(session, proposal.situation["context_event_id"])
            invalidate(session, row)
            return
        approval = session.scalar(
            select(ApprovalDecision).where(ApprovalDecision.proposal_id == proposal.id)
        )
        if proposal.status in {"PENDING_APPROVAL", "APPROVED"} and (
            self.clock.now() >= proposal.expires_at
            or (
                approval
                and approval.decision == "APPROVED"
                and self.clock.now() >= approval.expires_at
            )
        ):
            proposal.status = "EXPIRED"
            self.audit(session, "ACTION_EXPIRED", proposal, correlation_id)

    def detail(self, session, proposal):
        approval = session.scalar(
            select(ApprovalDecision).where(ApprovalDecision.proposal_id == proposal.id)
        )
        execution = session.scalar(
            select(ActionExecution).where(ActionExecution.proposal_id == proposal.id)
        )
        return ProposalDetail(
            proposal=self.proposal_read(proposal),
            approval=ApprovalRead.model_validate(approval) if approval else None,
            execution=ExecutionRead.model_validate(execution) if execution else None,
        )

    def proposal_read(self, proposal):
        result = ProposalRead.model_validate(proposal)
        if proposal.policy_version == "OWNED_CONTEXT_V1":
            result.clock_mode = "SYSTEM"
            if proposal.status != "PENDING_APPROVAL":
                result.content = "Draft unavailable; context is no longer active."
        return result

    def get(self, proposal_id, correlation_id):
        with SessionLocal.begin() as session:
            session.scalar(select(User.id).where(User.id == current_user_id()).with_for_update())
            proposal = self.find_proposal(session, proposal_id, True)
            self.expire(session, proposal, correlation_id)
            return self.detail(session, proposal)

    def list_proposals(self, task_id, correlation_id):
        with SessionLocal.begin() as session:
            session.scalar(select(User.id).where(User.id == current_user_id()).with_for_update())
            find_task(session, task_id)
            proposals = session.scalars(
                select(ActionProposal)
                .where(
                    ActionProposal.task_id == task_id, ActionProposal.user_id == current_user_id()
                )
                .order_by(ActionProposal.created_at, ActionProposal.id)
                .with_for_update()
            ).all()
            for proposal in proposals:
                self.expire(session, proposal, correlation_id)
            return [self.proposal_read(proposal) for proposal in proposals]

    def _deny(self, session, proposal, correlation_id, code):
        self.audit(session, "ACTION_EXECUTION_FAILED", proposal, correlation_id, reason=code)
        # Preserve refusal/expiration audit even though the HTTP operation fails.
        session.commit()
        fail(409, code, "Action refused. Reload and review its approval and validity.")

    def _remember_mutation(self, session, proposal, key, digest, result):
        session.add(
            ActionMutation(
                proposal_id=proposal.id,
                idempotency_key=key,
                request_hash=digest,
                result_proposal_id=result.id,
            )
        )
        session.flush()

    def mutate(self, proposal_id, operation, payload, correlation_id):
        from app.security.identity import principal

        identity = principal.get()
        if identity and operation in {"approve", "execute"} and "approver" not in identity.roles:
            fail(403, "FORBIDDEN", "Human approver permission required.")
        from app.database import _evaluation_schema, _evaluation_shadow

        if (
            _evaluation_schema.get()
            and _evaluation_shadow.get()
            and operation in {"approve", "execute"}
        ):
            fail(409, "SHADOW_ACTION_BLOCKED", "Shadow simulations cannot approve or execute.")
        with SessionLocal() as session:
            draft = self.find_proposal(session, proposal_id)
            if draft.policy_version == "OWNED_CONTEXT_V1":
                if operation != "reject":
                    fail(
                        409,
                        "DRAFT_ONLY",
                        "This workflow stops at pending approval; execution is disabled.",
                    )
                from app.proactive.drafts import OwnedDraftService

                return OwnedDraftService().reject(proposal_id, payload)
        digest = request_hash(
            operation, payload.model_dump(mode="json", exclude={"idempotency_key"})
        )
        with SessionLocal.begin() as session:
            proposal = self.find_proposal(session, proposal_id, True)
            previous = session.scalar(
                select(ActionMutation).where(
                    ActionMutation.proposal_id == proposal.id,
                    ActionMutation.idempotency_key == payload.idempotency_key,
                )
            )
            if previous:
                if previous.request_hash != digest:
                    fail(
                        409,
                        "IDEMPOTENCY_CONFLICT",
                        "Key was used for another operation or payload.",
                    )
                # Historical replay is a read of the original result; never executes again.
                result = self.find_proposal(session, previous.result_proposal_id, True)
                self.expire(session, result, correlation_id)
                return self.detail(session, result)
            self.expire(session, proposal, correlation_id)
            result = proposal
            if operation == "execute":
                existing = session.scalar(
                    select(ActionExecution).where(ActionExecution.proposal_id == proposal.id)
                )
                if existing:
                    self._remember_mutation(
                        session, proposal, payload.idempotency_key, digest, proposal
                    )
                    return self.detail(session, proposal)
                approval = session.scalar(
                    select(ApprovalDecision).where(ApprovalDecision.proposal_id == proposal.id)
                )
                valid = (
                    proposal.status == "APPROVED"
                    and approval
                    and approval.decision == "APPROVED"
                    and approval.proposal_id == proposal.id
                    and approval.user_id == proposal.user_id
                    and self.clock.now() < proposal.expires_at
                    and self.clock.now() < approval.expires_at
                    and proposal.payload_hash == payload_hash(proposal) == approval.payload_hash
                    and proposal.policy_version == POLICY_VERSION
                    and evaluate_policy(proposal)[0] == "REQUIRE_APPROVAL"
                )
                if not valid:
                    self._deny(session, proposal, correlation_id, "AUTHORIZATION_INVALID")
                now = self.clock.now()
                try:
                    receipt = self.executor.execute_authorized(
                        canonical_payload(proposal), proposal.payload_hash
                    )
                    status, error = "DONE", None
                except Exception:
                    receipt, status, error = {}, "FAILED", "SIMULATION_FAILED"
                execution = ActionExecution(
                    proposal_id=proposal.id,
                    approval_id=approval.id,
                    idempotency_key=payload.idempotency_key,
                    adapter="SIMULATED_COMMUNICATION",
                    status=status,
                    receipt=receipt,
                    started_at=now,
                    completed_at=self.clock.now(),
                    safe_error=error,
                )
                session.add(execution)
                proposal.status = "EXECUTED" if status == "DONE" else "FAILED"
                self.audit(
                    session,
                    "ACTION_EXECUTED" if status == "DONE" else "ACTION_EXECUTION_FAILED",
                    proposal,
                    correlation_id,
                    adapter="SIMULATED_COMMUNICATION",
                    external_message_sent=False,
                )
            elif operation == "edit":
                if proposal.status not in {"PENDING_APPROVAL", "APPROVED"}:
                    self._deny(session, proposal, correlation_id, "PROPOSAL_NOT_EDITABLE")
                result = ActionProposal(
                    user_id=proposal.user_id,
                    task_id=proposal.task_id,
                    trigger_id=proposal.trigger_id,
                    trace_id=proposal.trace_id,
                    action_type=proposal.action_type,
                    recipient=payload.recipient,
                    channel=proposal.channel,
                    content=payload.content,
                    reason=proposal.reason,
                    situation=proposal.situation,
                    created_at=self.clock.now(),
                    expires_at=proposal.expires_at,
                    supersedes_id=proposal.id,
                )
                self._policy(result)
                session.add(result)
                session.flush()
                proposal.status = "SUPERSEDED"
                self.audit(
                    session, "ACTION_EDITED", result, correlation_id, supersedes_id=str(proposal.id)
                )
                self.audit(
                    session,
                    "ACTION_PROPOSED",
                    result,
                    correlation_id,
                    payload_hash=result.payload_hash,
                )
            else:
                decision = "APPROVED" if operation == "approve" else "REJECTED"
                existing = session.scalar(
                    select(ApprovalDecision).where(ApprovalDecision.proposal_id == proposal.id)
                )
                if existing and existing.decision == decision and proposal.status == decision:
                    self._remember_mutation(
                        session, proposal, payload.idempotency_key, digest, proposal
                    )
                    return self.detail(session, proposal)
                if proposal.status != "PENDING_APPROVAL":
                    self._deny(session, proposal, correlation_id, "PROPOSAL_NOT_PENDING")
                if (
                    payload_hash(proposal) != proposal.payload_hash
                    or evaluate_policy(proposal)[0] != "REQUIRE_APPROVAL"
                ):
                    self._deny(session, proposal, correlation_id, "PAYLOAD_OR_POLICY_CHANGED")
                session.add(
                    ApprovalDecision(
                        proposal_id=proposal.id,
                        user_id=proposal.user_id,
                        decision=decision,
                        payload_hash=proposal.payload_hash,
                        created_at=self.clock.now(),
                        expires_at=min(
                            proposal.expires_at, self.clock.now() + timedelta(minutes=5)
                        ),
                    )
                )
                proposal.status = decision
                self.audit(
                    session,
                    "APPROVAL_GRANTED" if decision == "APPROVED" else "APPROVAL_REJECTED",
                    proposal,
                    correlation_id,
                    payload_hash=proposal.payload_hash,
                )
            session.add(
                ActionMutation(
                    proposal_id=proposal.id,
                    idempotency_key=payload.idempotency_key,
                    request_hash=digest,
                    result_proposal_id=result.id,
                )
            )
            session.flush()
            return self.detail(session, result)
