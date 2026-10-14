from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.intelligence.contracts import (
    AgentRunRead,
    ExecutionResponse,
    IntelligenceRead,
    RunAgentsRequest,
)
from app.intelligence.models import AgentRun
from app.intelligence.orchestrator import AgentOrchestrator, read_intelligence, read_runs
from app.service import fail, find_task

router = APIRouter(prefix="/api/v1/tasks", tags=["intelligence"])
DB = Annotated[Session, Depends(get_session)]


@router.post("/{task_id}/run-agents", response_model=ExecutionResponse, status_code=201)
def run_agents(task_id: UUID, payload: RunAgentsRequest, request: Request, response: Response):
    result = AgentOrchestrator().run(task_id, payload.idempotency_key, request.state.correlation_id)
    response.status_code = 200 if result.replayed else 201
    response.headers["X-Trace-ID"] = str(result.execution.trace_id)
    return result


@router.get("/{task_id}/agent-runs", response_model=list[AgentRunRead])
def agent_runs(task_id: UUID, session: DB):
    return read_runs(session, task_id)


@router.get("/{task_id}/agent-runs/{run_id}", response_model=AgentRunRead)
def agent_run(task_id: UUID, run_id: UUID, session: DB):
    find_task(session, task_id)
    run = session.scalar(select(AgentRun).where(AgentRun.id == run_id, AgentRun.task_id == task_id))
    if run is None:
        fail(404, "AGENT_RUN_NOT_FOUND", "Agent run was not found for this task.")
    return AgentRunRead.model_validate(run)


@router.get("/{task_id}/plan", response_model=IntelligenceRead)
def plan(task_id: UUID, session: DB):
    return read_intelligence(session, task_id)
