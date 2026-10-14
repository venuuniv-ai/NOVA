from datetime import UTC, datetime
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
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


def now():
    return datetime.now(UTC)


class MediaAsset(Base):
    __tablename__ = "media_assets"
    __table_args__ = (
        UniqueConstraint("task_id", "idempotency_key", name="uq_media_task_key"),
        CheckConstraint("width > 0 AND height > 0 AND byte_size > 0", name="ck_media_dimensions"),
        Index("ix_media_task_created", "task_id", "created_at"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    device_id: Mapped[UUID] = mapped_column(ForeignKey("devices.id"))
    sha256: Mapped[str] = mapped_column(String(64))
    mime_type: Mapped[str] = mapped_column(String(40), default="image/png")
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    byte_size: Mapped[int] = mapped_column(Integer)
    sanitized_reference: Mapped[str] = mapped_column(String(80))
    source: Mapped[str] = mapped_column(String(20))
    metadata_removed: Mapped[bool]
    idempotency_key: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class PerceptionRun(Base):
    __tablename__ = "perception_runs"
    __table_args__ = (
        UniqueConstraint("task_id", "idempotency_key", name="uq_perception_task_key"),
        CheckConstraint(
            "status IN ('RUNNING','DONE','PARTIAL','FAILED')", name="ck_perception_status"
        ),
        Index("ix_perception_task_started", "task_id", "started_at"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    media_id: Mapped[UUID] = mapped_column(ForeignKey("media_assets.id"))
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    trace_id: Mapped[UUID] = mapped_column(Uuid, unique=True)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))
    privacy_class: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20))
    simulation: Mapped[bool]
    warnings: Mapped[list] = mapped_column(JSONB, default=list)
    context: Mapped[list] = mapped_column(JSONB, default=list)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ProcessorRun(Base):
    __tablename__ = "processor_runs"
    __table_args__ = (
        UniqueConstraint("perception_run_id", "processor", name="uq_perception_processor"),
        CheckConstraint(
            "status IN ('DONE','FAILED','SKIPPED','UNAVAILABLE')", name="ck_processor_status"
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    perception_run_id: Mapped[UUID] = mapped_column(ForeignKey("perception_runs.id"))
    processor: Mapped[str] = mapped_column(String(40))
    model: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(20))
    simulation: Mapped[bool]
    latency_ms: Mapped[float | None]
    safe_error: Mapped[str | None] = mapped_column(String(60))


class VisualObservation(Base):
    __tablename__ = "visual_observations"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    perception_run_id: Mapped[UUID] = mapped_column(ForeignKey("perception_runs.id"), index=True)
    processor_run_id: Mapped[UUID] = mapped_column(ForeignKey("processor_runs.id"))
    output: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class MediaArtifact(Base):
    __tablename__ = "media_artifacts"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    media_id: Mapped[UUID] = mapped_column(ForeignKey("media_assets.id"))
    processor_run_id: Mapped[UUID] = mapped_column(ForeignKey("processor_runs.id"))
    sha256: Mapped[str] = mapped_column(String(64))
    byte_size: Mapped[int] = mapped_column(Integer)
    sanitized_reference: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
