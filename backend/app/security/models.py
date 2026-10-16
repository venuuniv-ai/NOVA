from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Identity(Base):
    __tablename__ = "auth_identities"
    __table_args__ = (UniqueConstraint("issuer", "subject", name="uq_auth_subject"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    issuer: Mapped[str] = mapped_column(String(250))
    subject: Mapped[str] = mapped_column(String(250))
    roles: Mapped[list] = mapped_column(JSONB)
    enabled: Mapped[bool] = mapped_column(default=True)
    version: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DeviceRegistration(Base):
    __tablename__ = "auth_device_registrations"
    device_id: Mapped[UUID] = mapped_column(ForeignKey("devices.id"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    enabled: Mapped[bool] = mapped_column(default=True)
    version: Mapped[int] = mapped_column(default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
