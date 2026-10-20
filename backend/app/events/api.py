from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app.events.models import Inbox, Job, Outbox, Projection, Subscription
from app.security.identity import current_user_id
from app.service import find_task

router = APIRouter(prefix="/api/v1/operations", tags=["operations"])


@router.get("/events")
def summary():
    with SessionLocal() as session:
        counts = dict(
            session.execute(
                select(Outbox.state, func.count())
                .where(Outbox.user_id == current_user_id())
                .group_by(Outbox.state)
            ).all()
        )
        return {
            "outbox": counts,
            "delivery": "AT_LEAST_ONCE",
            "effects": "TRANSACTIONAL_INBOX",
            "proactive": "OPT_IN_FIXTURE_DRAFT_ONLY",
            "execution_mode": "SIMULATED / NOT SENT",
        }


@router.post("/tasks/{task_id}/subscribe")
def subscribe(task_id: UUID):
    with SessionLocal.begin() as session:
        find_task(session, task_id)
        session.execute(
            insert(Subscription)
            .values(task_id=task_id, user_id=current_user_id(), enabled=True)
            .on_conflict_do_update(index_elements=[Subscription.task_id], set_={"enabled": True})
        )
        return {"task_id": str(task_id), "enabled": True, "capability": "DRAFT_ONLY"}


@router.get("/tasks/{task_id}")
def task_events(
    task_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    after: int = Query(default=0, ge=0, le=9223372036854775807),
    jobs_after: int = Query(default=0, ge=0, le=9223372036854775807),
    through: int | None = Query(default=None, ge=0, le=9223372036854775807),
):
    # Sequence cursors use the immutable outbox order, including for jobs. The
    # high-water mark excludes newly appended events while paging this view.
    with SessionLocal() as session:
        find_task(session, task_id)
        user = current_user_id()
        scope = (Outbox.task_id == task_id, Outbox.user_id == user)
        latest = session.scalar(select(func.max(Outbox.sequence)).where(*scope)) or 0
        ceiling = min(through, latest) if through is not None else latest
        events = list(
            session.scalars(
                select(Outbox)
                .where(*scope, Outbox.sequence > after, Outbox.sequence <= ceiling)
                .order_by(Outbox.sequence)
                .limit(limit + 1)
            )
        )
        more_events = len(events) > limit
        events = events[:limit]
        ids = [e.id for e in events]
        consumers = {}
        for event_id, consumer in session.execute(
            select(Inbox.event_id, Inbox.consumer).where(
                Inbox.event_id.in_(ids),
                Inbox.consumer.in_(["projection", "proactive", "audit"]),
            )
        ):
            consumers.setdefault(event_id, []).append(consumer)
        jobs = session.execute(
            select(Job, Outbox.sequence)
            .join(Outbox, Job.event_id == Outbox.id)
            .where(
                *scope,
                Job.user_id == user,
                Job.task_id == task_id,
                Outbox.sequence > jobs_after,
                Outbox.sequence <= ceiling,
            )
            .order_by(Outbox.sequence)
            .limit(limit + 1)
        ).all()
        more_jobs = len(jobs) > limit
        jobs = jobs[:limit]
        projection = session.get(Projection, task_id)
        return {
            "task_id": str(task_id),
            "events": [
                {
                    "id": str(e.id),
                    "sequence": e.sequence,
                    "type": e.event_type,
                    "state": e.state,
                    "attempts": e.attempts,
                    "consumers": sorted(consumers.get(e.id, [])),
                }
                for e in events
            ],
            "projection_sequence": (
                projection.last_sequence if projection and projection.user_id == user else None
            ),
            "jobs": [
                {
                    "id": str(j.id),
                    "state": j.state,
                    "attempts": j.attempts,
                    "sequence": sequence,
                    "result_id": str(j.result_id) if j.result_id else None,
                    "diagnostic": "TERMINAL_JOB_FAILURE" if j.state == "DEAD" else None,
                }
                for j, sequence in jobs
            ],
            "page": {
                "limit": limit,
                "through": ceiling,
                "next_after": events[-1].sequence if more_events else None,
                "next_jobs_after": jobs[-1][1] if more_jobs else None,
            },
            "diagnostic_boundary": "METADATA ONLY / NOT A MODEL FAILURE EXPLANATION",
        }


@router.post("/events/{event_id}/retry")
def retry(event_id: UUID):
    from datetime import UTC, datetime

    from app.service import fail

    with SessionLocal.begin() as session:
        row = session.scalar(
            select(Outbox)
            .where(Outbox.id == event_id, Outbox.user_id == current_user_id())
            .with_for_update()
        )
        if row is None:
            fail(404, "EVENT_NOT_FOUND", "Event not found.")
        if row.state == "DEAD":
            row.state, row.attempts, row.next_attempt_at = "PENDING", 0, datetime.now(UTC)
        return {"id": str(row.id), "state": row.state, "payload_changed": False}


@router.post("/jobs/{job_id}/retry")
def retry_job(job_id: UUID):
    from datetime import UTC, datetime

    from app.service import fail

    with SessionLocal.begin() as session:
        job = session.scalar(
            select(Job).where(Job.id == job_id, Job.user_id == current_user_id()).with_for_update()
        )
        if job is None:
            fail(404, "JOB_NOT_FOUND", "Job not found.")
        if job.state == "DEAD":
            job.state, job.attempts, job.next_attempt_at = "PENDING", 0, datetime.now(UTC)
        return {"id": str(job.id), "state": job.state, "original_event_id": str(job.event_id)}
