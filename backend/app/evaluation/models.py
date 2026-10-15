from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


def now():
    return datetime.now(UTC)


class Dataset(Base):
    __tablename__ = "evaluation_datasets"
    __table_args__ = (UniqueConstraint("name", "version", name="uq_evaluation_dataset_version"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(60))
    version: Mapped[str] = mapped_column(String(30))
    digest: Mapped[str] = mapped_column(String(64))
    scenario_versions: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"
    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_evaluation_run_key"),
        CheckConstraint("status IN ('RUNNING','DONE','FAILED')", name="ck_evaluation_run_status"),
        Index(
            "uq_evaluation_active_user",
            "user_id",
            unique=True,
            postgresql_where=text("status = 'RUNNING'"),
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("evaluation_datasets.id"))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    input_hash: Mapped[str] = mapped_column(String(64))
    suite: Mapped[str] = mapped_column(String(20))
    configuration: Mapped[str] = mapped_column(String(40))
    configuration_fingerprint: Mapped[str] = mapped_column(String(64))
    reproducibility: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20))
    summary: Mapped[dict] = mapped_column(JSONB, default=dict)
    metrics: Mapped[list] = mapped_column(JSONB, default=list)
    gates: Mapped[list] = mapped_column(JSONB, default=list)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    safe_error: Mapped[str | None] = mapped_column(String(80))


class ScenarioResult(Base):
    __tablename__ = "evaluation_scenario_results"
    __table_args__ = (
        UniqueConstraint("run_id", "scenario_id", name="uq_evaluation_scenario_run"),
        CheckConstraint("status IN ('PASS','FAIL','ERROR')", name="ck_evaluation_scenario_status"),
        CheckConstraint("elapsed_ms >= 0", name="ck_evaluation_elapsed"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    run_id: Mapped[UUID] = mapped_column(ForeignKey("evaluation_runs.id"), index=True)
    scenario_id: Mapped[str] = mapped_column(String(128))
    scenario_version: Mapped[int]
    category: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20))
    elapsed_ms: Mapped[float]
    observation: Mapped[dict] = mapped_column(JSONB)
    graders: Mapped[list] = mapped_column(JSONB)
    judge: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Experiment(Base):
    __tablename__ = "experiment_definitions"
    __table_args__ = (UniqueConstraint("user_id", "idempotency_key", name="uq_experiment_key"),)
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    input_hash: Mapped[str] = mapped_column(String(64))
    definition: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Assignment(Base):
    __tablename__ = "experiment_assignments"
    __table_args__ = (
        UniqueConstraint("experiment_id", "subject", name="uq_experiment_assignment"),
        CheckConstraint("variant IN ('BASELINE','CANDIDATE')", name="ck_experiment_variant"),
        CheckConstraint("bucket >= 0 AND bucket < 10000", name="ck_experiment_bucket"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    experiment_id: Mapped[UUID] = mapped_column(ForeignKey("experiment_definitions.id"), index=True)
    subject: Mapped[str] = mapped_column(String(128))
    bucket: Mapped[int]
    variant: Mapped[str] = mapped_column(String(20))


class ExperimentResult(Base):
    __tablename__ = "experiment_results"
    __table_args__ = (
        CheckConstraint(
            "status IN ('RUNNING','DONE','FAILED')", name="ck_experiment_result_status"
        ),
        Index(
            "uq_experiment_active_user",
            "user_id",
            unique=True,
            postgresql_where=text("status = 'RUNNING'"),
        ),
        UniqueConstraint("experiment_id", "idempotency_key", name="uq_experiment_result_key"),
    )
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    experiment_id: Mapped[UUID] = mapped_column(ForeignKey("experiment_definitions.id"), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(128))
    baseline_id: Mapped[UUID | None] = mapped_column(ForeignKey("evaluation_runs.id"))
    candidate_id: Mapped[UUID | None] = mapped_column(ForeignKey("evaluation_runs.id"))
    status: Mapped[str] = mapped_column(String(20), default="RUNNING")
    comparison: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
