from uuid import UUID

from fastapi import APIRouter, Response

from app.memory.contracts import (
    Confirmation,
    Correction,
    MemoryInput,
    MemoryMutation,
    MemoryQuery,
    MemoryRead,
    RetrievalResult,
    VisualCandidateRequest,
)
from app.memory.service import MemoryService

router = APIRouter(prefix="/api/v1", tags=["memory"])


@router.post("/memory", response_model=MemoryRead, status_code=201)
def create(payload: MemoryInput):
    return MemoryService().mutate("create", payload.idempotency_key, payload)


@router.get("/memory", response_model=list[MemoryRead])
def memories():
    return MemoryService().list()


@router.get("/memory/candidates", response_model=list[MemoryRead])
def candidates():
    return MemoryService().list(pending=True)


@router.post("/memory/candidates/visual", response_model=MemoryRead, status_code=201)
def visual_candidate(payload: VisualCandidateRequest):
    return MemoryService().mutate("visual", payload.idempotency_key, payload)


@router.post("/memory/search", response_model=RetrievalResult)
def search(payload: MemoryQuery, response: Response):
    result = MemoryService().search(payload)
    response.headers["X-Trace-ID"] = str(result.trace_id)
    return result


@router.get("/memory/{memory_id}", response_model=MemoryRead)
def detail(memory_id: UUID):
    return MemoryService().detail(memory_id)


@router.get("/memory/{memory_id}/history")
def history(memory_id: UUID):
    return MemoryService().history(memory_id)


@router.post("/memory/{memory_id}/correct", response_model=MemoryRead)
def correct(memory_id: UUID, payload: Correction):
    return MemoryService().mutate("correct", payload.idempotency_key, payload, memory_id)


@router.delete("/memory/{memory_id}", response_model=MemoryRead)
def delete(memory_id: UUID, payload: MemoryMutation):
    return MemoryService().mutate("delete", payload.idempotency_key, payload, memory_id)


@router.post("/memory/candidates/{memory_id}/confirm", response_model=MemoryRead)
def confirm(memory_id: UUID, payload: Confirmation):
    return MemoryService().mutate("confirm", payload.idempotency_key, payload, memory_id)


@router.post("/memory/candidates/{memory_id}/reject", response_model=MemoryRead)
def reject(memory_id: UUID, payload: MemoryMutation):
    return MemoryService().mutate("reject", payload.idempotency_key, payload, memory_id)


@router.get("/tasks/{task_id}/memory", response_model=RetrievalResult)
def task_context(task_id: UUID):
    return MemoryService().search(MemoryQuery(task_id=task_id, limit=20))
