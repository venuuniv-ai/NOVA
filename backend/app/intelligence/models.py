from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class AgentExecution(Base):
    __tablename__ = "agent_executions"
    __table_args__ = (
        UniqueConstraint("task_id", "idempotency_key", name="uq_execution_task_key"),
        CheckConstraint("status IN ('RUNNING', 'DONE', 'FAILED')", name="ck_execution_status"),
        Index("ix_execution_task_started", "task_id", "started_at"),
        Index(
            "uq_execution_active_task",
            "task_id",
            unique=True,
            postgresql_where=text("status = 'RUNNING'"),
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    trace_id: Mapped[UUID] = mapped_column(Uuid, unique=True)
    status: Mapped[str] = mapped_column(String(20))
    provider: Mapped[str] = mapped_column(String(80))
    model: Mapped[str] = mapped_column(String(80))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(String(100))
    context: Mapped[dict | None] = mapped_column(JSONB)
    final_plan: Mapped[dict | None] = mapped_column(JSONB)
    critic: Mapped[dict | None] = mapped_column(JSONB)


class AgentRun(Base):
    __tablename__ = "agent_runs"
    __table_args__ = (
        UniqueConstraint("execution_id", "sequence", name="uq_run_execution_sequence"),
        CheckConstraint(
            "status IN ('WAITING','RUNNING','DONE','FAILED','SKIPPED')", name="ck_run_status"
        ),
        Index("ix_run_task_trace", "task_id", "trace_id"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    execution_id: Mapped[UUID] = mapped_column(ForeignKey("agent_executions.id"), index=True)
    trace_id: Mapped[UUID] = mapped_column(ForeignKey("agent_executions.trace_id"))
    agent_name: Mapped[str] = mapped_column(String(20))
    stage: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(20))
    sequence: Mapped[int] = mapped_column(Integer)
    provider: Mapped[str] = mapped_column(String(80))
    model: Mapped[str] = mapped_column(String(80))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str] = mapped_column(String(500), default="")
    structured_output: Mapped[dict | None] = mapped_column(JSONB)
    evidence: Mapped[list] = mapped_column(JSONB, default=list)
    warnings: Mapped[list] = mapped_column(JSONB, default=list)
    error: Mapped[str | None] = mapped_column(String(100))
    tool_calls: Mapped[list["ToolCall"]] = relationship(lazy="selectin")


class ToolCall(Base):
    __tablename__ = "tool_calls"
    __table_args__ = (CheckConstraint("status IN ('DONE','FAILED')", name="ck_tool_status"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    agent_run_id: Mapped[UUID] = mapped_column(ForeignKey("agent_runs.id"), index=True)
    trace_id: Mapped[UUID] = mapped_column(ForeignKey("agent_executions.trace_id"), index=True)
    plugin: Mapped[str] = mapped_column(String(80))
    function: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(20))
    input: Mapped[dict] = mapped_column(JSONB)
    output: Mapped[dict | None] = mapped_column(JSONB)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(String(100))
