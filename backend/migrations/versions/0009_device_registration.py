"""Revocable simulated device identity; old continuity IDs are preserved."""

import sqlalchemy as sa
from alembic import op

revision = "0009_device_registration"
down_revision = "0008_security_outbox"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auth_device_registrations",
        sa.Column("device_id", sa.Uuid(), sa.ForeignKey("devices.id"), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_auth_device_registrations_user_id", "auth_device_registrations", ["user_id"]
    )


def downgrade():
    op.drop_index("ix_auth_device_registrations_user_id", table_name="auth_device_registrations")
    op.drop_table("auth_device_registrations")
