import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("length(trim(name)) > 0", name="ck_user_name"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (
        UniqueConstraint("user_id", "type", name="uq_device_user_type"),
        CheckConstraint("type IN ('DESKTOP', 'MOBILE', 'WEARABLE')", name="ck_device_type"),
        CheckConstraint("length(trim(name)) > 0", name="ck_device_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE')", name="ck_task_status"),
        CheckConstraint("length(trim(title)) > 0", name="ck_task_title"),
        Index("ix_task_user_created", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(240))
    description: Mapped[str] = mapped_column(Text, default="")
    origin_device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"))
    current_device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TaskEvent(Base):
    __tablename__ = "task_events"
    __table_args__ = (
        UniqueConstraint("task_id", "idempotency_key", name="uq_event_task_idempotency"),
        UniqueConstraint("task_id", "sequence", name="uq_event_task_sequence"),
        Index("ix_event_task_created", "task_id", "created_at"),
        CheckConstraint(
            "(event_type = 'TASK_CREATED' AND idempotency_key IS NULL) OR "
            "(event_type IN ('HANDOFF_DESKTOP_TO_WEARABLE', 'HANDOFF_WEARABLE_TO_MOBILE') "
            "AND idempotency_key IS NOT NULL)",
            name="ck_event_type_key",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tasks.id"))
    event_type: Mapped[str] = mapped_column(String(64))
    source_device_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("devices.id"))
    target_device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id"))
    idempotency_key: Mapped[str | None] = mapped_column(String(128))
    # DeclarativeBase reserves `metadata`; retain the requested SQL column name.
    event_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
    sequence: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
