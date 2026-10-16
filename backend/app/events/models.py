from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


def now():
    return datetime.now(UTC)


class Outbox(Base):
    __tablename__ = "event_outbox"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sequence: Mapped[int] = mapped_column(BigInteger, Identity(), unique=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[UUID | None] = mapped_column(ForeignKey("tasks.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(default=0)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    state: Mapped[str] = mapped_column(String(20), default="PENDING")
    __table_args__ = (
        Index("ix_outbox_pending", "state", "sequence"),
        CheckConstraint("state IN ('PENDING','PUBLISHED','DEAD')", name="ck_outbox_state"),
        CheckConstraint("attempts >= 0", name="ck_outbox_attempts"),
    )


class Inbox(Base):
    __tablename__ = "event_inbox"
    consumer: Mapped[str] = mapped_column(String(60), primary_key=True)
    event_id: Mapped[UUID] = mapped_column(ForeignKey("event_outbox.id"), primary_key=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Projection(Base):
    __tablename__ = "event_task_projections"
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    last_sequence: Mapped[int] = mapped_column(BigInteger)
    last_event: Mapped[str] = mapped_column(String(100))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Subscription(Base):
    __tablename__ = "event_subscriptions"
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    enabled: Mapped[bool] = mapped_column(default=True)


class Job(Base):
    __tablename__ = "event_jobs"
    __table_args__ = (
        CheckConstraint("state IN ('PENDING','RUNNING','DONE','DEAD')", name="ck_event_job_state"),
        CheckConstraint("attempts >= 0", name="ck_event_job_attempts"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey("event_outbox.id"), unique=True)
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    state: Mapped[str] = mapped_column(String(20), default="PENDING")
    attempts: Mapped[int] = mapped_column(default=0)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    result_id: Mapped[UUID | None]
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DeadLetter(Base):
    __tablename__ = "event_dead_letters"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    consumer: Mapped[str] = mapped_column(String(60))
    fingerprint: Mapped[str] = mapped_column(String(64))
    reason: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (UniqueConstraint("consumer", "fingerprint", name="uq_event_dead_letter"),)
