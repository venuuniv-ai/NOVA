"""Persistent task continuity foundation.

Revision ID: 0001_core
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_core"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_user_name"),
    )
    op.create_table(
        "devices",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("user_id", "type", name="uq_device_user_type"),
        sa.CheckConstraint("type IN ('DESKTOP', 'MOBILE', 'WEARABLE')", name="ck_device_type"),
        sa.CheckConstraint("length(trim(name)) > 0", name="ck_device_name"),
    )
    op.create_index("ix_devices_user_id", "devices", ["user_id"])
    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("origin_device_id", sa.Uuid(), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("current_device_id", sa.Uuid(), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("status IN ('ACTIVE')", name="ck_task_status"),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_task_title"),
    )
    op.create_index("ix_tasks_current_device_id", "tasks", ["current_device_id"])
    op.create_index("ix_task_user_created", "tasks", ["user_id", "created_at"])
    op.create_table(
        "task_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("task_id", sa.Uuid(), sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("source_device_id", sa.Uuid(), sa.ForeignKey("devices.id"), nullable=True),
        sa.Column("target_device_id", sa.Uuid(), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("idempotency_key", sa.String(128), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("task_id", "idempotency_key", name="uq_event_task_idempotency"),
        sa.UniqueConstraint("task_id", "sequence", name="uq_event_task_sequence"),
        sa.CheckConstraint(
            "(event_type = 'TASK_CREATED' AND idempotency_key IS NULL) OR "
            "(event_type IN ('HANDOFF_DESKTOP_TO_WEARABLE', 'HANDOFF_WEARABLE_TO_MOBILE') "
            "AND idempotency_key IS NOT NULL)",
            name="ck_event_type_key",
        ),
    )
    op.create_index("ix_event_task_created", "task_events", ["task_id", "created_at"])


def downgrade():
    op.drop_table("task_events")
    op.drop_table("tasks")
    op.drop_table("devices")
    op.drop_table("users")
