from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.memory.models import now
from app.models import Base


class InferenceModel(Base):
    __tablename__ = "inference_models"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    metadata_snapshot: Mapped[dict] = mapped_column(JSONB)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class InferenceRun(Base):
    __tablename__ = "inference_runs"
    __table_args__ = (
        UniqueConstraint("user_id", "request_id", name="uq_inference_request"),
        CheckConstraint("state IN ('RUNNING','DONE','FAILED')", name="ck_inference_state"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    request_id: Mapped[UUID] = mapped_column(Uuid)
    request_hash: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(20))
    metadata_snapshot: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class EmbeddingVersion(Base):
    __tablename__ = "embedding_versions"
    namespace: Mapped[str] = mapped_column(String(120), primary_key=True)
    model_id: Mapped[str] = mapped_column(String(120))
    fingerprint: Mapped[str] = mapped_column(String(64))
    version: Mapped[str] = mapped_column(String(80))
    dimension: Mapped[int]
    simulation: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ReindexJob(Base):
    __tablename__ = "reindex_jobs"
    __table_args__ = (
        UniqueConstraint("user_id", "request_id", name="uq_reindex_request"),
        CheckConstraint("state IN ('READY','DONE','FAILED')", name="ck_reindex_state"),
        CheckConstraint("processed >= 0", name="ck_reindex_processed"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"))
    request_id: Mapped[UUID] = mapped_column(Uuid)
    request_hash: Mapped[str] = mapped_column(String(64))
    namespace: Mapped[str] = mapped_column(ForeignKey("embedding_versions.namespace"))
    mode: Mapped[str] = mapped_column(String(20))
    state: Mapped[str] = mapped_column(String(20))
    cursor: Mapped[UUID | None] = mapped_column(Uuid)
    upper_bound: Mapped[UUID | None] = mapped_column(Uuid)
    processed: Mapped[int] = mapped_column(default=0)
    error: Mapped[str | None] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
