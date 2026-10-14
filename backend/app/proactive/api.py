from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.proactive.contracts import (
    AuditRead,
    ContextEventInput,
    EditRequest,
    EvaluationRead,
    Mutation,
    ProposalDetail,
    ProposalRead,
)
from app.proactive.models import AuditEvent, ProactiveTrigger
from app.proactive.service import ProactiveService
from app.seed import DEMO_USER_ID
from app.service import find_task

router = APIRouter(prefix="/api/v1", tags=["proactive-actions"])
DB = Annotated[Session, Depends(get_session)]


def get_service():
    return ProactiveService()


Service = Annotated[ProactiveService, Depends(get_service)]


@router.post("/proactive/evaluate", response_model=EvaluationRead)
def evaluate(payload: ContextEventInput, request: Request, response: Response, service: Service):
    result = service.evaluate(payload, request.state.correlation_id)
    response.headers["X-Trace-ID"] = str(result.trace_id)
    return result


@router.get("/tasks/{task_id}/proactive")
def proactive(task_id: UUID, session: DB):
    find_task(session, task_id)
    return [
        dict(
            id=str(t.id),
            trace_id=str(t.trace_id),
            status=t.status,
            reason=t.reason,
            situation=t.situation,
            agent_record=t.agent_record,
        )
        for t in session.scalars(
            select(ProactiveTrigger)
            .where(ProactiveTrigger.task_id == task_id, ProactiveTrigger.user_id == DEMO_USER_ID)
            .order_by(ProactiveTrigger.created_at, ProactiveTrigger.id)
        )
    ]


@router.get("/tasks/{task_id}/proposals", response_model=list[ProposalRead])
def proposals(task_id: UUID, request: Request, service: Service):
    return service.list_proposals(task_id, request.state.correlation_id)


@router.get("/proposals/{proposal_id}", response_model=ProposalDetail)
def proposal(proposal_id: UUID, request: Request, service: Service):
    return service.get(proposal_id, request.state.correlation_id)


@router.post("/proposals/{proposal_id}/edit", response_model=ProposalDetail)
def edit(
    proposal_id: UUID, payload: EditRequest, request: Request, response: Response, service: Service
):
    result = service.mutate(proposal_id, "edit", payload, request.state.correlation_id)
    response.headers["X-Trace-ID"] = str(result.proposal.trace_id)
    return result


def mutation_endpoint(operation):
    def endpoint(
        proposal_id: UUID, payload: Mutation, request: Request, response: Response, service: Service
    ):
        result = service.mutate(proposal_id, operation, payload, request.state.correlation_id)
        response.headers["X-Trace-ID"] = str(result.proposal.trace_id)
        return result

    return endpoint


for operation in ("approve", "reject", "execute"):
    router.add_api_route(
        f"/proposals/{{proposal_id}}/{operation}",
        mutation_endpoint(operation),
        methods=["POST"],
        response_model=ProposalDetail,
        name=operation,
    )


@router.get("/tasks/{task_id}/audit-events", response_model=list[AuditRead])
def audit(task_id: UUID, session: DB):
    find_task(session, task_id)
    return session.scalars(
        select(AuditEvent)
        .where(AuditEvent.task_id == task_id, AuditEvent.user_id == DEMO_USER_ID)
        .order_by(AuditEvent.created_at, AuditEvent.id)
    ).all()
