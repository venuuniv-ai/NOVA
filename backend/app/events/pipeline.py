import hashlib
import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import exists, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased

from app.database import SessionLocal
from app.events.models import DeadLetter, Inbox, Job, Outbox, Projection, Subscription

TOPIC = "nova.events.v1"


class Envelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    user_id: UUID
    task_id: UUID | None
    sequence: int = Field(ge=1)
    event_type: str = Field(max_length=100)
    payload: dict


def envelope(row):
    return Envelope(
        id=row.id,
        user_id=row.user_id,
        task_id=row.task_id,
        sequence=row.sequence,
        event_type=row.event_type,
        payload=row.payload,
    ).model_dump(mode="json")


def publish_one(send):
    """send must synchronously await broker ack. A crash after ack may publish a duplicate."""
    with SessionLocal.begin() as session:
        earlier = aliased(Outbox)
        row = session.scalar(
            select(Outbox)
            .where(
                Outbox.state == "PENDING",
                Outbox.next_attempt_at <= datetime.now(UTC),
                ~exists(
                    select(earlier.id).where(
                        earlier.state.in_(["PENDING", "DEAD"]),
                        earlier.sequence < Outbox.sequence,
                        earlier.task_id == Outbox.task_id,
                    )
                ),
            )
            .order_by(Outbox.sequence)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        if row is None:
            return False
        row.attempts += 1
        try:
            send(str(row.task_id or row.id).encode(), json.dumps(envelope(row)).encode())
            row.state, row.published_at = "PUBLISHED", datetime.now(UTC)
        except Exception:
            row.state = "DEAD" if row.attempts >= 8 else "PENDING"
            row.next_attempt_at = datetime.now(UTC) + timedelta(seconds=min(60, 2**row.attempts))
        return True


def _consume(raw, consumer="projection"):
    """Commit inbox and business effect together, then let Kafka commit the offset."""
    fingerprint = hashlib.sha256(raw).hexdigest()
    try:
        if len(raw) > 16000:
            raise ValueError("Oversized")
        message = Envelope.model_validate_json(raw)
        with SessionLocal.begin() as session:
            source = session.get(Outbox, message.id)
            if source is None or envelope(source) != message.model_dump(mode="json"):
                raise ValueError("Non-authoritative event")
            claimed = session.execute(
                insert(Inbox)
                .values(consumer=consumer, event_id=message.id)
                .on_conflict_do_nothing()
                .returning(Inbox.event_id)
            ).scalar()
            if not claimed:
                return "DUPLICATE"
            if message.task_id and consumer == "projection":
                statement = insert(Projection).values(
                    task_id=message.task_id,
                    user_id=message.user_id,
                    last_sequence=message.sequence,
                    last_event=message.event_type,
                    updated_at=datetime.now(UTC),
                )
                session.execute(
                    statement.on_conflict_do_update(
                        index_elements=[Projection.task_id],
                        set_={
                            "last_sequence": message.sequence,
                            "last_event": message.event_type,
                            "updated_at": datetime.now(UTC),
                        },
                        where=Projection.last_sequence < message.sequence,
                    )
                )
            if (
                consumer == "proactive"
                and message.task_id
                and message.payload.get("transition") == "HANDOFF_DESKTOP_TO_WEARABLE"
            ):
                subscription = session.get(Subscription, message.task_id)
                if (
                    subscription
                    and subscription.enabled
                    and subscription.user_id == message.user_id
                ):
                    session.execute(
                        insert(Job)
                        .values(
                            event_id=message.id,
                            task_id=message.task_id,
                            user_id=message.user_id,
                            state="PENDING",
                            attempts=0,
                            updated_at=datetime.now(UTC),
                        )
                        .on_conflict_do_nothing()
                    )
        return "PROCESSED"
    except (ValueError, TypeError):
        with SessionLocal.begin() as session:
            session.execute(
                insert(DeadLetter)
                .values(
                    consumer=consumer,
                    fingerprint=fingerprint,
                    reason="INVALID_OR_UNTRUSTED_EVENT",
                    created_at=datetime.now(UTC),
                )
                .on_conflict_do_nothing()
            )
        return "DEAD_LETTER"


def work_one():
    from sqlalchemy import text

    # Session advisory lock spans the service's own transactions, and is released on crash.
    from app.database import engine
    from app.proactive.service import ProactiveService
    from app.security.identity import Principal, principal

    with engine.connect() as lock:
        if not lock.scalar(text("SELECT pg_try_advisory_lock(80888001)")):
            return False
        try:
            with SessionLocal.begin() as session:
                job = session.scalar(
                    select(Job)
                    .where(
                        Job.state.in_(["PENDING", "RUNNING"]),
                        Job.next_attempt_at <= datetime.now(UTC),
                    )
                    .order_by(Job.updated_at)
                    .with_for_update()
                    .limit(1)
                )
                if not job:
                    return False
                job.state, job.attempts = "RUNNING", job.attempts + 1
                job_id, task_id, event_id, user_id = job.id, job.task_id, job.event_id, job.user_id
            token = principal.set(Principal(user_id, frozenset({"owner"}), mode="worker"))
            try:
                # This capability is draft-only. No call to approve/execute exists in this worker.
                from app.proactive.contracts import ContextEventInput

                result = ProactiveService().evaluate(
                    ContextEventInput(task_id=task_id, idempotency_key="event-" + str(event_id)),
                    str(event_id),
                )
                with SessionLocal.begin() as session:
                    job = session.get(Job, job_id)
                    job.state, job.updated_at = "DONE", datetime.now(UTC)
                    job.result_id = result.proposal.id if result.proposal else None
            except Exception:
                with SessionLocal.begin() as session:
                    job = session.get(Job, job_id)
                    job.state = "DEAD" if job.attempts >= 5 else "PENDING"
                    job.next_attempt_at = datetime.now(UTC) + timedelta(
                        seconds=min(60, 2**job.attempts)
                    )
            finally:
                principal.reset(token)
            return True
        finally:
            lock.execute(text("SELECT pg_advisory_unlock(80888001)"))


def consume(raw, consumer="projection"):
    from opentelemetry import trace
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    try:
        message = Envelope.model_validate_json(raw) if len(raw) <= 16000 else None
        parent = message.payload.get("traceparent", "") if message else ""
        carrier = {"traceparent": parent} if isinstance(parent, str) and len(parent) == 55 else {}
    except (ValueError, TypeError):
        carrier = {}
    context = TraceContextTextMapPropagator().extract(carrier)
    with trace.get_tracer("nova.events").start_as_current_span(
        "event.consume", context=context
    ) as span:
        span.set_attribute("messaging.consumer.group.name", consumer)
        result = _consume(raw, consumer)
        span.set_attribute("nova.delivery.result", result)
        import logging

        logging.getLogger("nova.events").info(
            "event_" + result.lower(),
            extra={
                "trace_id": format(span.get_span_context().trace_id, "032x")
                if span.get_span_context().is_valid
                else None
            },
        )
        return result
