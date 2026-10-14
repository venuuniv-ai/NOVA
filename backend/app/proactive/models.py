from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class ContextEvent(Base):
    __tablename__ = "context_events"
    __table_args__ = (UniqueConstraint("task_id", "idempotency_key", name="uq_context_task_key"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(30))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(30))
    payload: Mapped[dict] = mapped_column(JSONB)
    trace_id: Mapped[UUID] = mapped_column(Uuid, unique=True)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))


class ProactiveTrigger(Base):
    __tablename__ = "proactive_triggers"
    __table_args__ = (
        Index("ix_trigger_user_fingerprint", "user_id", "fingerprint"),
        CheckConstraint("status IN ('SURFACED','SUPPRESSED','FAILED')", name="ck_trigger_status"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey("context_events.id"), unique=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), index=True)
    trace_id: Mapped[UUID] = mapped_column(Uuid, unique=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str] = mapped_column(String(100))
    situation: Mapped[dict] = mapped_column(JSONB)
    agent_record: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ActionProposal(Base):
    __tablename__ = "action_proposals"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PROPOSED','PENDING_APPROVAL','APPROVED','REJECTED','EXPIRED',"
            "'EXECUTED','FAILED','SUPERSEDED')",
            name="ck_proposal_status",
        ),
        Index("ix_proposal_task_created", "task_id", "created_at"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    trigger_id: Mapped[UUID] = mapped_column(ForeignKey("proactive_triggers.id"))
    trace_id: Mapped[UUID] = mapped_column(Uuid)
    action_type: Mapped[str] = mapped_column(String(40))
    recipient: Mapped[str] = mapped_column(String(120))
    channel: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(String(1000))
    reason: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20))
    payload_hash: Mapped[str] = mapped_column(String(64))
    policy_version: Mapped[str] = mapped_column(String(60))
    policy_decision: Mapped[str] = mapped_column(String(30))
    policy_reason: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    supersedes_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("action_proposals.id"), unique=True
    )
    situation: Mapped[dict] = mapped_column(JSONB)


class ApprovalDecision(Base):
    __tablename__ = "approval_decisions"
    __table_args__ = (
        CheckConstraint("decision IN ('APPROVED','REJECTED')", name="ck_approval_decision"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    proposal_id: Mapped[UUID] = mapped_column(ForeignKey("action_proposals.id"), unique=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    decision: Mapped[str] = mapped_column(String(20))
    payload_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ActionExecution(Base):
    __tablename__ = "action_executions"
    __table_args__ = (
        CheckConstraint("status IN ('DONE','FAILED')", name="ck_action_execution_status"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    proposal_id: Mapped[UUID] = mapped_column(ForeignKey("action_proposals.id"), unique=True)
    approval_id: Mapped[UUID] = mapped_column(ForeignKey("approval_decisions.id"), unique=True)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    adapter: Mapped[str] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(20))
    receipt: Mapped[dict] = mapped_column(JSONB)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    safe_error: Mapped[str | None] = mapped_column(String(100))


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (Index("ix_audit_task_created", "task_id", "created_at"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(50))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    proposal_id: Mapped[UUID | None] = mapped_column(ForeignKey("action_proposals.id"))
    trace_id: Mapped[UUID] = mapped_column(Uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    safe_metadata: Mapped[dict] = mapped_column(JSONB)


class ActionMutation(Base):
    __tablename__ = "action_mutations"
    __table_args__ = (
        UniqueConstraint("proposal_id", "idempotency_key", name="uq_mutation_proposal_key"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    proposal_id: Mapped[UUID] = mapped_column(ForeignKey("action_proposals.id"))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))
    result_proposal_id: Mapped[UUID] = mapped_column(ForeignKey("action_proposals.id"))
