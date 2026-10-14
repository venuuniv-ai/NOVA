from datetime import datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

DeviceType = Literal["DESKTOP", "WEARABLE", "MOBILE"]
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=240)]
IdempotencyKey = Annotated[
    str,
    StringConstraints(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$"),
]


class DeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    name: str
    type: DeviceType
    created_at: datetime


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Title
    description: str = Field(default="", max_length=10000)
    origin_device_id: UUID


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    title: str
    description: str
    origin_device_id: UUID
    current_device_id: UUID
    status: Literal["ACTIVE"]
    created_at: datetime
    updated_at: datetime


class HandoffRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_device_id: UUID
    target_device_id: UUID
    idempotency_key: IdempotencyKey


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: UUID
    task_id: UUID
    event_type: str
    source_device_id: UUID | None
    target_device_id: UUID
    idempotency_key: str | None
    metadata: dict[str, Any] = Field(validation_alias="event_metadata")
    sequence: int
    created_at: datetime


class HandoffResponse(BaseModel):
    task: TaskRead
    event: EventRead
    replayed: bool
