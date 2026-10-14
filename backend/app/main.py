import logging
import re
import time
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import get_session
from app.intelligence.api import router as intelligence_router
from app.intelligence.models import AgentExecution
from app.intelligence.orchestrator import recover_interrupted_executions
from app.logging import configure_logging
from app.memory.api import router as memory_router
from app.model_routing.api import router as model_router
from app.model_routing.models import ModelCall
from app.model_routing.service import recover_model_calls
from app.models import Device, Task, TaskEvent
from app.perception.api import router as perception_router
from app.perception.service import recover_perception
from app.proactive.api import router as proactive_router
from app.proactive.models import ActionProposal
from app.schemas import DeviceRead, EventRead, HandoffRequest, HandoffResponse, TaskCreate, TaskRead
from app.seed import DEMO_USER_ID
from app.service import create_task, find_task, handoff_task

logger = logging.getLogger("nova.http")
DB = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    recover_interrupted_executions()
    recover_model_calls()
    recover_perception()
    yield


app = FastAPI(title="NOVA Core", version="1.0.0", lifespan=lifespan)
app.include_router(intelligence_router)
app.include_router(proactive_router)
app.include_router(model_router)
app.include_router(perception_router)
app.include_router(memory_router)


@app.middleware("http")
async def correlate(request: Request, call_next):
    incoming = request.headers.get("X-Correlation-ID", "")
    correlation_id = incoming if re.fullmatch(r"[A-Za-z0-9._:-]{1,64}", incoming) else str(uuid4())
    request.state.correlation_id = correlation_id
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("unhandled_request_error", extra={"correlation_id": correlation_id})
        response = JSONResponse(
            status_code=500,
            content={
                "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
                "correlation_id": correlation_id,
            },
        )
    response.headers["X-Correlation-ID"] = correlation_id
    logger.info(
        "request_complete",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
            "trace_id": response.headers.get("X-Trace-ID"),
        },
    )
    return response


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, error: StarletteHTTPException):
    detail = (
        error.detail
        if isinstance(error.detail, dict)
        else {"code": "HTTP_ERROR", "message": str(error.detail)}
    )
    return JSONResponse(
        status_code=error.status_code,
        content={
            "error": detail,
            "correlation_id": request.state.correlation_id,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, error: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "details": [
                    {"location": list(e["loc"]), "message": e["msg"]} for e in error.errors()
                ],
            },
            "correlation_id": request.state.correlation_id,
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, error: SQLAlchemyError):
    logger.error("database_unavailable", extra={"correlation_id": request.state.correlation_id})
    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "DATABASE_UNAVAILABLE",
                "message": "Persistent storage is unavailable.",
            },
            "correlation_id": request.state.correlation_id,
        },
    )


@app.get("/health/live")
def live():
    return {"status": "alive"}


@app.get("/health/ready")
def ready(session: DB):
    # DB connectivity, migrated tables, and the three seeded contexts are required.
    session.execute(text("SELECT 1"))
    session.execute(select(Task.id).limit(1))
    session.execute(select(AgentExecution.id).limit(1))
    session.execute(select(ActionProposal.id).limit(1))
    session.execute(select(ModelCall.id).limit(1))
    count = session.scalar(
        select(func.count()).select_from(Device).where(Device.user_id == DEMO_USER_ID)
    )
    if count != 3:
        raise HTTPException(
            503, detail={"code": "NOT_READY", "message": "Demo devices are not seeded."}
        )
    return {"status": "ready", "database": "available"}


@app.get("/api/v1/devices", response_model=list[DeviceRead])
def devices(session: DB):
    devices = session.scalars(select(Device).where(Device.user_id == DEMO_USER_ID)).all()
    order = {"DESKTOP": 0, "WEARABLE": 1, "MOBILE": 2}
    return sorted(devices, key=lambda device: order[device.type])


@app.post("/api/v1/tasks", response_model=TaskRead, status_code=201)
def new_task(payload: TaskCreate, request: Request, session: DB):
    return create_task(session, payload, request.state.correlation_id)


@app.get("/api/v1/tasks", response_model=list[TaskRead])
def tasks(
    session: DB,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return session.scalars(
        select(Task)
        .where(Task.user_id == DEMO_USER_ID)
        .order_by(Task.created_at.desc(), Task.id)
        .limit(limit)
        .offset(offset)
    ).all()


@app.get("/api/v1/tasks/{task_id}", response_model=TaskRead)
def task(task_id: UUID, session: DB):
    return find_task(session, task_id)


@app.post("/api/v1/tasks/{task_id}/handoff", response_model=HandoffResponse)
def handoff(task_id: UUID, payload: HandoffRequest, request: Request, session: DB):
    return handoff_task(session, task_id, payload, request.state.correlation_id)


@app.get("/api/v1/tasks/{task_id}/events", response_model=list[EventRead])
def events(task_id: UUID, session: DB):
    find_task(session, task_id)
    return session.scalars(
        select(TaskEvent).where(TaskEvent.task_id == task_id).order_by(TaskEvent.sequence)
    ).all()
