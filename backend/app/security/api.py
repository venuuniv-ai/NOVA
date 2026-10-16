from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Device, User
from app.security.identity import current_user_id
from app.security.models import DeviceRegistration
from app.service import fail

router = APIRouter(prefix="/api/v1/auth/devices", tags=["device-security"])


class RegisterDevice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    device_id: UUID


@router.get("")
def registered_devices():
    with SessionLocal() as session:
        rows = []
        for device in session.scalars(select(Device).where(Device.user_id == current_user_id())):
            state = session.get(DeviceRegistration, device.id)
            rows.append(
                {
                    "device_id": str(device.id),
                    "type": device.type,
                    "enabled": state.enabled if state else True,
                    "version": state.version if state else 0,
                    "simulation": True,
                }
            )
        return rows


def change(device_id, enabled):
    with SessionLocal.begin() as session:
        session.scalar(select(User.id).where(User.id == current_user_id()).with_for_update())
        device = session.scalar(
            select(Device).where(Device.id == device_id, Device.user_id == current_user_id())
        )
        if not device:
            fail(404, "DEVICE_NOT_FOUND", "Device not found.")
        state = session.get(DeviceRegistration, device_id)
        if state is None:
            state = DeviceRegistration(
                device_id=device_id,
                user_id=current_user_id(),
                enabled=enabled,
                version=1,
                updated_at=datetime.now(UTC),
            )
            session.add(state)
        elif state.enabled != enabled:
            state.enabled, state.version, state.updated_at = (
                enabled,
                state.version + 1,
                datetime.now(UTC),
            )
        return {
            "device_id": str(device_id),
            "enabled": state.enabled,
            "version": state.version,
            "simulation": True,
            "new_token_required": True,
        }


@router.post("/register")
def register(payload: RegisterDevice):
    return change(payload.device_id, True)


@router.post("/{device_id}/revoke")
def revoke(device_id: UUID):
    return change(device_id, False)
