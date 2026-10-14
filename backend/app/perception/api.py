from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import Response as BinaryResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_session
from app.perception.contracts import (
    FixtureRequest,
    PerceptionRequest,
    PerceptionResult,
    ReasonRequest,
)
from app.perception.media import MediaIngestionService, fixture_bytes
from app.perception.models import MediaArtifact, MediaAsset, PerceptionRun
from app.perception.processors import processors
from app.perception.service import PerceptionOrchestrator
from app.schemas import IdempotencyKey
from app.seed import DEMO_USER_ID
from app.service import find_task

router = APIRouter(prefix="/api/v1", tags=["perception"])
DB = Annotated[Session, Depends(get_session)]
ingestion = MediaIngestionService()


@router.get("/perception/processors")
def processor_status():
    return {
        "processors": [
            {
                "processor": p.processor,
                "model": p.model,
                "status": p.status(),
                "simulation": p.simulation,
            }
            for p in processors()
        ],
        "vlm": "REAL VLM NOT CONFIGURED / FIXTURE VLM ONLY",
    }


@router.post("/tasks/{task_id}/media/fixture", status_code=201)
def fixture(task_id: UUID, payload: FixtureRequest):
    return ingestion.ingest(
        task_id, payload.idempotency_key, fixture_bytes(), "image/png", fixture=True
    )


@router.post("/tasks/{task_id}/media", status_code=201)
async def upload(
    task_id: UUID, request: Request, idempotency_key: Annotated[IdempotencyKey, Header()]
):
    import asyncio

    with SessionLocal() as session:
        find_task(session, task_id)
    data = await ingestion.read_upload(request)
    return await asyncio.to_thread(
        ingestion.ingest, task_id, idempotency_key, data, request.headers.get("content-type", "")
    )


@router.get("/tasks/{task_id}/media")
def media_list(task_id: UUID, session: DB):
    find_task(session, task_id)
    return [
        ingestion.read(m)
        for m in session.scalars(
            select(MediaAsset)
            .where(MediaAsset.task_id == task_id, MediaAsset.user_id == DEMO_USER_ID)
            .order_by(MediaAsset.created_at.desc())
            .limit(100)
        )
    ]


@router.get("/tasks/{task_id}/media/{media_id}/content")
def media_content(task_id: UUID, media_id: UUID, session: DB):
    media = ingestion.owned(session, task_id, media_id)
    return BinaryResponse(
        content=ingestion.verified_bytes(media),
        media_type="image/png",
        headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; sandbox",
        },
    )


@router.get("/tasks/{task_id}/artifacts/{artifact_id}/content")
def mask_content(task_id: UUID, artifact_id: UUID, session: DB):
    from app.service import fail

    artifact = session.get(MediaArtifact, artifact_id)
    if not artifact:
        fail(404, "ARTIFACT_NOT_FOUND", "Artifact was not found.")
    ingestion.owned(session, task_id, artifact.media_id)
    return BinaryResponse(
        content=ingestion.verified_bytes(artifact),
        media_type="image/png",
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@router.post("/tasks/{task_id}/perception", response_model=PerceptionResult)
def perceive(task_id: UUID, payload: PerceptionRequest, request: Request, response: Response):
    result = PerceptionOrchestrator().run(task_id, payload, request.state.correlation_id)
    response.headers["X-Trace-ID"] = str(result.trace_id)
    return result


@router.get("/tasks/{task_id}/perception", response_model=list[PerceptionResult])
def runs(task_id: UUID, session: DB):
    find_task(session, task_id)
    service = PerceptionOrchestrator()
    ids = session.scalars(
        select(PerceptionRun.id)
        .where(PerceptionRun.task_id == task_id)
        .order_by(PerceptionRun.started_at.desc())
        .limit(100)
    ).all()
    return [service.read(session, task_id, id) for id in ids]


@router.get("/tasks/{task_id}/perception/{run_id}", response_model=PerceptionResult)
def detail(task_id: UUID, run_id: UUID, session: DB):
    return PerceptionOrchestrator().read(session, task_id, run_id)


@router.post("/tasks/{task_id}/perception/{run_id}/reason")
def reason(task_id: UUID, run_id: UUID, payload: ReasonRequest, request: Request):
    from app.perception.service import VisualReasoningService

    return VisualReasoningService().run(task_id, run_id, payload, request.state.correlation_id)
