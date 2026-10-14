from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class BudgetDay(Base):
    __tablename__ = "model_budget_days"
    __table_args__ = (
        CheckConstraint("consumed_usd >= 0 AND reserved_usd >= 0", name="ck_budget_nonnegative"),
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    day: Mapped[date] = mapped_column(Date, primary_key=True)
    consumed_usd: Mapped[Decimal] = mapped_column(Numeric(20, 10), default=Decimal(0))
    reserved_usd: Mapped[Decimal] = mapped_column(Numeric(20, 10), default=Decimal(0))


class ModelCall(Base):
    __tablename__ = "model_calls"
    __table_args__ = (
        UniqueConstraint("user_id", "request_id", name="uq_model_user_request"),
        CheckConstraint("status IN ('RUNNING','DONE','FAILED')", name="ck_model_call_status"),
        Index("ix_model_call_task_started", "task_id", "started_at"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    trace_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    request_id: Mapped[UUID] = mapped_column(Uuid)
    request_hash: Mapped[str] = mapped_column(String(64))
    provider: Mapped[str | None] = mapped_column(String(80))
    model: Mapped[str | None] = mapped_column(String(120))
    tier: Mapped[str | None] = mapped_column(String(20))
    purpose: Mapped[str] = mapped_column(String(30))
    privacy_class: Mapped[str] = mapped_column(String(30))
    complexity: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    routing_decision: Mapped[dict] = mapped_column(JSONB)
    attempts: Mapped[list] = mapped_column(JSONB, default=list)
    response_metadata: Mapped[dict | None] = mapped_column(JSONB)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reserved_cost_usd: Mapped[Decimal] = mapped_column(Numeric(20, 10), default=Decimal(0))
    accounted_cost_usd: Mapped[Decimal] = mapped_column(Numeric(20, 10), default=Decimal(0))
    reserved_day: Mapped[date | None] = mapped_column(Date)
    safe_error: Mapped[str | None] = mapped_column(String(60))
