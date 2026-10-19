"""Explicit inference metadata, embedding versions and restartable reindexing."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "0011_inference_registry"
down_revision = "0010_event_retry_bounds"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "inference_models",
        sa.Column("id", sa.String(80), primary_key=True),
        sa.Column("metadata_snapshot", JSONB, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "embedding_versions",
        sa.Column("namespace", sa.String(120), primary_key=True),
        sa.Column("model_id", sa.String(120), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("version", sa.String(80), nullable=False),
        sa.Column("dimension", sa.Integer, nullable=False),
        sa.Column("simulation", sa.Boolean, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "inference_runs",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("user_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("task_id", sa.Uuid, sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("request_id", sa.Uuid, nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("metadata_snapshot", JSONB, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "request_id", name="uq_inference_request"),
        sa.CheckConstraint("state IN ('RUNNING','DONE','FAILED')", name="ck_inference_state"),
    )
    op.create_table(
        "reindex_jobs",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("user_id", sa.Uuid, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("task_id", sa.Uuid, sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("request_id", sa.Uuid, nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column(
            "namespace",
            sa.String(120),
            sa.ForeignKey("embedding_versions.namespace"),
            nullable=False,
        ),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("cursor", sa.Uuid),
        sa.Column("upper_bound", sa.Uuid),
        sa.Column("processed", sa.Integer, nullable=False),
        sa.Column("error", sa.String(60)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "request_id", name="uq_reindex_request"),
        sa.CheckConstraint("state IN ('READY','DONE','FAILED')", name="ck_reindex_state"),
        sa.CheckConstraint("processed >= 0", name="ck_reindex_processed"),
    )


def downgrade():
    for name in ["reindex_jobs", "inference_runs", "embedding_versions", "inference_models"]:
        op.drop_table(name)
