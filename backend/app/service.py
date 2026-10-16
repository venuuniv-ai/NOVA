import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Device, Task, TaskEvent
from app.schemas import HandoffRequest, HandoffResponse, TaskCreate
from app.security.identity import current_user_id

logger = logging.getLogger("nova.tasks")
TRANSITIONS = {("DESKTOP", "WEARABLE"), ("WEARABLE", "MOBILE")}


def fail(status: int, code: str, message: str) -> None:
    raise HTTPException(status_code=status, detail={"code": code, "message": message})


def find_device(session: Session, device_id: UUID) -> Device:
    device = session.scalar(
        select(Device).where(Device.id == device_id, Device.user_id == current_user_id())
    )
    if device is None:
        fail(422, "INVALID_DEVICE", "Device does not belong to the demo user.")
    from app.security.models import DeviceRegistration

    registration = session.get(DeviceRegistration, device_id)
    if registration and not registration.enabled:
        fail(422, "DEVICE_REVOKED", "Device registration is revoked.")
    return device


def find_task(session: Session, task_id: UUID, *, lock: bool = False) -> Task:
    query = select(Task).where(Task.id == task_id, Task.user_id == current_user_id())
    if lock:
        query = query.with_for_update()
    task = session.scalar(query)
    if task is None:
        fail(404, "TASK_NOT_FOUND", "Task was not found.")
    return task


def create_task(session: Session, payload: TaskCreate, correlation_id: str) -> Task:
    origin = find_device(session, payload.origin_device_id)
    if origin.type != "DESKTOP":
        fail(422, "INVALID_ORIGIN", "Phase 1 tasks must originate on Desktop.")
    task = Task(
        user_id=current_user_id(),
        title=payload.title,
        description=payload.description,
        origin_device_id=origin.id,
        current_device_id=origin.id,
        status="ACTIVE",
    )
    session.add(task)
    session.flush()
    session.add(
        TaskEvent(
            task_id=task.id,
            event_type="TASK_CREATED",
            source_device_id=None,
            target_device_id=origin.id,
            sequence=1,
            event_metadata={"correlation_id": correlation_id},
        )
    )
    session.commit()
    logger.info("task_created", extra={"task_id": str(task.id), "correlation_id": correlation_id})
    return task


def handoff_task(
    session: Session, task_id: UUID, payload: HandoffRequest, correlation_id: str
) -> HandoffResponse:
    # Serialize ALL mutations of this task. A racing retry sees the first commit.
    task = find_task(session, task_id, lock=True)
    existing = session.scalar(
        select(TaskEvent).where(
            TaskEvent.task_id == task_id, TaskEvent.idempotency_key == payload.idempotency_key
        )
    )
    if existing is not None:
        if (existing.source_device_id, existing.target_device_id) != (
            payload.source_device_id,
            payload.target_device_id,
        ):
            fail(409, "IDEMPOTENCY_CONFLICT", "This key was already used for a different handoff.")
        # Check retries BEFORE current-device validation: historical retries remain valid.
        response = HandoffResponse(task=task, event=existing, replayed=True)
        session.commit()
        logger.info(
            "handoff_replayed", extra={"task_id": str(task_id), "correlation_id": correlation_id}
        )
        return response

    source = find_device(session, payload.source_device_id)
    target = find_device(session, payload.target_device_id)
    if task.current_device_id != source.id:
        fail(409, "STALE_SOURCE", "The task has moved. Reload before handing it off.")
    if (source.type, target.type) not in TRANSITIONS:
        fail(409, "INVALID_TRANSITION", "Allowed path: DESKTOP → WEARABLE → MOBILE.")

    task.current_device_id = target.id
    task.updated_at = datetime.now(UTC)
    sequence = (
        session.scalar(select(func.max(TaskEvent.sequence)).where(TaskEvent.task_id == task_id)) + 1
    )
    event = TaskEvent(
        task_id=task.id,
        event_type=f"HANDOFF_{source.type}_TO_{target.type}",
        source_device_id=source.id,
        target_device_id=target.id,
        idempotency_key=payload.idempotency_key,
        sequence=sequence,
        event_metadata={"correlation_id": correlation_id},
    )
    session.add(event)
    session.flush()
    session.commit()
    logger.info("task_handoff", extra={"task_id": str(task_id), "correlation_id": correlation_id})
    return HandoffResponse(task=task, event=event, replayed=False)
