import json
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
from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import UserDefinedType

from app.models import Base


class Vector(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw):
        return "VECTOR"

    def bind_processor(self, dialect):
        return lambda value: (
            json.dumps(value, allow_nan=False) if not isinstance(value, str) else value
        )

    def result_processor(self, dialect, coltype):
        return lambda value: json.loads(value) if isinstance(value, str) else value


def now():
    return datetime.now(UTC)


class MemoryRecord(Base):
    __tablename__ = "memory_records"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE','PENDING_CONFIRMATION','SUPERSEDED',"
            "'DELETED','EXPIRED','REJECTED')",
            name="ck_memory_status",
        ),
        CheckConstraint(
            "scope IN ('USER','TASK') AND ((scope='USER' AND task_id IS NULL) "
            "OR (scope='TASK' AND task_id IS NOT NULL))",
            name="ck_memory_scope",
        ),
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="ck_memory_confidence",
        ),
        CheckConstraint(
            "valid_until IS NULL OR valid_from IS NULL OR valid_until > valid_from",
            name="ck_memory_time",
        ),
        Index("ix_memory_owned_active", "user_id", "status", "scope", "subject", "predicate"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[UUID | None] = mapped_column(ForeignKey("tasks.id"))
    memory_type: Mapped[str] = mapped_column(String(30))
    subject: Mapped[str] = mapped_column(String(80))
    predicate: Mapped[str] = mapped_column(String(40))
    value: Mapped[str] = mapped_column(String(500))
    normalized_text: Mapped[str] = mapped_column(String(700))
    canonical_hash: Mapped[str] = mapped_column(String(64), index=True)
    origin: Mapped[str] = mapped_column(String(40))
    explicitness: Mapped[str] = mapped_column(String(20))
    confirmed: Mapped[bool] = mapped_column(default=False)
    confidence: Mapped[float | None]
    status: Mapped[str] = mapped_column(String(30))
    scope: Mapped[str] = mapped_column(String(10))
    privacy_class: Mapped[str] = mapped_column(String(30))
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_reference: Mapped[str] = mapped_column(String(160))
    supersedes_id: Mapped[UUID | None] = mapped_column(ForeignKey("memory_records.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    policy_decision: Mapped[str] = mapped_column(String(30))
    policy_reason: Mapped[str] = mapped_column(String(100))


class MemoryEmbedding(Base):
    __tablename__ = "memory_embeddings"
    __table_args__ = (
        UniqueConstraint(
            "memory_id", "provider", "model", "dimension", name="uq_memory_embedding_namespace"
        ),
        CheckConstraint("vector_dims(embedding) = dimension", name="ck_memory_vector_dimension"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    memory_id: Mapped[UUID] = mapped_column(ForeignKey("memory_records.id"), index=True)
    provider: Mapped[str] = mapped_column(String(80))
    model: Mapped[str] = mapped_column(String(120))
    dimension: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[list] = mapped_column(Vector())
    simulation: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class MemoryAudit(Base):
    __tablename__ = "memory_audits"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    memory_id: Mapped[UUID] = mapped_column(ForeignKey("memory_records.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(60))
    trace_id: Mapped[UUID] = mapped_column(Uuid)
    safe_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class MemoryMutation(Base):
    __tablename__ = "memory_mutations"
    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_memory_mutation_key"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    request_hash: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class MemoryRetrieval(Base):
    __tablename__ = "memory_retrievals"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[UUID | None] = mapped_column(ForeignKey("tasks.id"), index=True)
    trace_id: Mapped[UUID] = mapped_column(Uuid)
    query_hash: Mapped[str] = mapped_column(String(64))
    hits: Mapped[list] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


# Teach Alembic reflection the extension type without adding an ML dependency.

ischema_names["vector"] = Vector
