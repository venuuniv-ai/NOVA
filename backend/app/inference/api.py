from uuid import UUID

from fastapi import APIRouter, Request, Response
from sqlalchemy import select

from app.database import SessionLocal
from app.inference import service
from app.inference.contracts import InferenceInput, ProactiveInferenceInput, ReindexInput
from app.inference.models import InferenceRun, ReindexJob
from app.security.identity import current_user_id, principal
from app.service import fail

router = APIRouter(prefix="/api/v1/inference", tags=["inference"])


@router.get("/models")
def models():
    return service.model_inventory()


@router.get("/health")
def health():
    return service.model_inventory()


@router.post("/generate")
def generate(payload: InferenceInput, request: Request):
    return service.run(payload, request.state.correlation_id)


@router.get("/runs")
def runs():
    with SessionLocal() as session:
        return [
            service.read_run(id)
            for id in session.scalars(
                select(InferenceRun.id)
                .where(InferenceRun.user_id == current_user_id())
                .order_by(InferenceRun.created_at.desc())
                .limit(50)
            )
        ]


@router.get("/runs/{id}")
def detail(id: UUID):
    return service.read_run(id)


@router.post("/reindex")
def create(payload: ReindexInput):
    return service.create_reindex(payload)


@router.get("/reindex")
def jobs():
    with SessionLocal() as session:
        return [
            service.job_read(job)
            for job in session.scalars(
                select(ReindexJob)
                .where(ReindexJob.user_id == current_user_id())
                .order_by(ReindexJob.created_at.desc())
                .limit(50)
            )
        ]


@router.post("/reindex/{id}/step")
def step(id: UUID):
    return service.step_reindex(id)


@router.post("/agents")
def agents(payload: InferenceInput, request: Request):
    from app.inference.providers import selected
    from app.intelligence.orchestrator import AgentOrchestrator
    from app.model_routing.kernel_provider import RoutedModelProvider

    selected(payload.mode, "STRUCTURED")
    return AgentOrchestrator(provider=RoutedModelProvider(strict_inference_mode=payload.mode)).run(
        payload.task_id, str(payload.request_id), request.state.correlation_id
    )


@router.get("/evaluation")
def evaluation():
    if "operator" not in principal.get().roles:
        fail(403, "FORBIDDEN", "Operator role required for evaluation.")
    from app.inference.evaluation import evaluate

    return evaluate()


@router.post("/evaluation/real")
def real_evaluation():
    if "operator" not in principal.get().roles:
        fail(403, "FORBIDDEN", "Operator role required for evaluation.")
    from app.inference.evaluation import evaluate

    return evaluate(include_real=True)


@router.post("/proactive")
def proactive(payload: ProactiveInferenceInput, request: Request, response: Response):
    from app.inference.providers import selected
    from app.model_routing.api import routed_proactive_impl

    selected(payload.mode, "STRUCTURED")
    with SessionLocal() as session:
        return routed_proactive_impl(payload.context, request, response, session, payload.mode)
