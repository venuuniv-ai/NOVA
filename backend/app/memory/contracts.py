from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas import IdempotencyKey

MemoryType = Literal["PREFERENCE", "FACT", "EPISODIC", "TASK_CONTEXT"]
Origin = Literal[
    "USER_EXPLICIT",
    "USER_CORRECTION",
    "AGENT_INFERRED",
    "VISUAL_OBSERVATION",
    "TASK_OUTCOME",
    "FIXTURE",
]
Status = Literal["ACTIVE", "PENDING_CONFIRMATION", "SUPERSEDED", "DELETED", "EXPIRED", "REJECTED"]
Privacy = Literal["INTERNAL", "PERSONAL", "SENSITIVE_LOCAL_ONLY"]
Predicate = Literal[
    "preferred_cuisine",
    "preferred_beverage",
    "dining_preference",
    "dinner_time",
    "project_deadline",
    "task_note",
    "task_outcome",
]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, revalidate_instances="always")


class MemoryInput(Contract):
    idempotency_key: IdempotencyKey
    memory_type: MemoryType = "PREFERENCE"
    subject: str = Field(default="demo_user", min_length=1, max_length=80)
    predicate: Predicate = "dining_preference"
    value: str = Field(min_length=1, max_length=500)
    scope: Literal["USER", "TASK"] = "USER"
    task_id: UUID | None = None
    privacy_class: Privacy = "PERSONAL"
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    @field_validator("subject", "value")
    @classmethod
    def strip_text(cls, value):
        if not value.strip():
            raise ValueError("Blank memory field.")
        return value.strip()

    @model_validator(mode="after")
    def scope_and_time(self):
        if self.scope == "TASK" and not self.task_id:
            raise ValueError("Task scope requires a task.")
        if self.scope == "USER" and self.task_id:
            raise ValueError("User scope does not take a task binding.")
        if self.memory_type == "TASK_CONTEXT" and self.scope != "TASK":
            raise ValueError("Task context remains task-scoped.")
        for moment in [self.valid_from, self.valid_until]:
            if moment and moment.tzinfo is None:
                raise ValueError("Validity timestamps require a timezone.")
        if self.valid_from and self.valid_until and self.valid_until <= self.valid_from:
            raise ValueError("Invalid validity interval.")
        return self


class MemoryMutation(Contract):
    idempotency_key: IdempotencyKey


class Correction(MemoryMutation):
    value: str = Field(min_length=1, max_length=500)

    @field_validator("value")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Blank correction.")
        return value.strip()


class Confirmation(MemoryMutation):
    edited_value: str | None = Field(default=None, min_length=1, max_length=500)

    @field_validator("edited_value")
    @classmethod
    def nonblank(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Blank confirmation edit.")
        return value.strip() if value else value


class VisualCandidateRequest(MemoryMutation):
    task_id: UUID
    observation_id: UUID


class MemoryCandidate(Contract):
    memory_type: MemoryType
    subject: str = Field(min_length=1, max_length=80)
    predicate: Predicate
    value: str = Field(min_length=1, max_length=500)
    origin: Literal["AGENT_INFERRED", "VISUAL_OBSERVATION", "TASK_OUTCOME"]
    confidence: float = Field(ge=0, le=1, allow_inf_nan=False)
    source_reference: UUID
    task_id: UUID
    scope: Literal["USER", "TASK"] = "USER"
    privacy_class: Privacy = "PERSONAL"


class MemoryRead(Contract):
    id: UUID
    user_id: UUID
    task_id: UUID | None
    memory_type: MemoryType
    subject: str
    predicate: Predicate
    value: str
    normalized_text: str
    origin: Origin
    explicitness: Literal["EXPLICIT", "INFERRED", "FIXTURE"]
    confirmed: bool
    confidence: float | None
    status: Status
    scope: Literal["USER", "TASK"]
    privacy_class: Privacy
    valid_from: datetime | None
    valid_until: datetime | None
    source_reference: str
    supersedes_id: UUID | None
    created_at: datetime
    updated_at: datetime
    policy_decision: Literal["STORE", "ASK_CONFIRMATION", "REJECT", "TASK_ONLY"]
    policy_reason: str


class MemoryQuery(Contract):
    retrieval_strategy: Literal["HYBRID", "LEXICAL", "SEMANTIC"] = "HYBRID"
    task_id: UUID | None = None
    query: str = Field(default="", max_length=500)
    types: list[MemoryType] = Field(
        default_factory=lambda: ["PREFERENCE", "FACT", "EPISODIC", "TASK_CONTEXT"], max_length=4
    )
    subject: str | None = Field(default=None, max_length=80)
    predicate: Predicate | None = None
    scope: Literal["USER", "TASK"] | None = None
    privacy_ceiling: Privacy = "PERSONAL"
    limit: int = Field(default=10, ge=1, le=20)
    as_of_time: datetime | None = None

    @model_validator(mode="after")
    def valid_time(self):
        if self.as_of_time and self.as_of_time.tzinfo is None:
            raise ValueError("Retrieval time must have a timezone.")
        if self.scope == "TASK" and not self.task_id:
            raise ValueError("Task retrieval requires task binding.")
        return self


class MemoryHit(Contract):
    memory_id: UUID
    memory: MemoryRead
    retrieval_sources: list[Literal["STRUCTURED", "LEXICAL", "SEMANTIC"]]
    reason_codes: list[str]
    structured_rank: int | None
    lexical_rank: int | None
    semantic_rank: int | None
    semantic_similarity: float | None
    fused_score: float
    fused_rank: int
    embedding_provider: str
    embedding_model: str
    embedding_simulation: bool


class RetrievalResult(Contract):
    id: UUID
    trace_id: UUID
    hits: list[MemoryHit]
    disclosure: str


class EmbeddingRequest(Contract):
    text: str = Field(min_length=1, max_length=1000)
    privacy_class: Privacy


class EmbeddingResult(Contract):
    provider: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=120)
    dimension: int = Field(ge=1, le=2000)
    vector: list[float] = Field(min_length=1, max_length=2000)
    simulation: bool
    latency_ms: float = Field(ge=0, allow_inf_nan=False)
    usage_source: Literal["UNKNOWN"] = "UNKNOWN"

    @model_validator(mode="after")
    def vector_valid(self):
        import math

        if (
            len(self.vector) != self.dimension
            or any(not math.isfinite(v) for v in self.vector)
            or sum(v * v for v in self.vector) == 0
        ):
            raise ValueError("Invalid embedding vector.")
        return self
