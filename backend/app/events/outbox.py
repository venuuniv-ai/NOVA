"""Mapper hooks write bounded events on the business row's exact DB connection/transaction."""

from uuid import uuid4

from sqlalchemy import event, inspect, select

from app.database import _evaluation_schema
from app.events.models import Outbox
from app.models import Base, Task
from app.security.identity import current_user_id

TYPES = {
    "Task",
    "TaskEvent",
    "AgentExecution",
    "ActionProposal",
    "ApprovalDecision",
    "ActionExecution",
    "MemoryRecord",
    "PerceptionRun",
    "ContextEvent",
}


def record(mapper, connection, row):
    kind = type(row).__name__
    if _evaluation_schema.get() or kind not in TYPES:
        return
    if kind == "ContextEvent" and row.source != "OWNED_CONTEXT_V1":
        return
    task_id = row.id if isinstance(row, Task) else getattr(row, "task_id", None)
    owner = getattr(row, "user_id", None)
    if owner is None and task_id:
        owner = connection.scalar(select(Task.user_id).where(Task.id == task_id))
    payload = {
        "version": 1,
        "resource_id": str(row.id),
        "resource_type": kind,
        "status": str(getattr(row, "status", "RECORDED")),
    }
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    carrier = {}
    TraceContextTextMapPropagator().inject(carrier)
    if carrier.get("traceparent"):
        payload["traceparent"] = carrier["traceparent"]
    if kind == "TaskEvent":
        payload["transition"] = row.event_type
    connection.execute(
        Outbox.__table__.insert().values(
            id=uuid4(),
            user_id=owner or current_user_id(),
            task_id=task_id,
            event_type=kind + ".changed",
            payload=payload,
        )
    )


@event.listens_for(Base, "after_insert", propagate=True)
def after_insert(mapper, connection, row):
    record(mapper, connection, row)


@event.listens_for(Base, "after_update", propagate=True)
def after_update(mapper, connection, row):
    if type(row).__name__ == "ContextEvent":
        return  # Emit one immutable trigger; state changes must not enqueue more jobs.
    if any(a.history.has_changes() for a in inspect(row).attrs):
        record(mapper, connection, row)
