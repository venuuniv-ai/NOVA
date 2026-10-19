from typing import Literal
from uuid import UUID, uuid4

from pydantic import Field, model_validator

from app.intelligence.contracts import Contract
from app.proactive.contracts import ContextEventInput

Mode = Literal["FIXTURE", "LOCAL_REAL", "DISABLED"]


class InferenceInput(Contract):
    task_id: UUID
    request_id: UUID = Field(default_factory=uuid4)
    mode: Mode = "FIXTURE"
    operation: Literal["TEXT", "STRUCTURED", "RAG", "EMBED", "VISION"] = "RAG"
    benchmark_label: Literal["SHORT", "LONG", "STRUCTURED"] | None = None
    query: str = Field(default="", max_length=500)
    retrieval: Literal["HYBRID", "LEXICAL", "SEMANTIC"] = "HYBRID"
    media_id: UUID | None = None
    max_output_tokens: int = Field(default=256, ge=16, le=1024)


class Quote(Contract):
    evidence_id: UUID
    quote: str = Field(min_length=1, max_length=700)


class GroundedOutput(Contract):
    claims: list[Quote] = Field(default_factory=list, max_length=8)
    abstain: bool

    @model_validator(mode="after")
    def consistent(self):
        if self.abstain == bool(self.claims):
            raise ValueError("Abstention cannot contain claims; answers require evidence.")
        return self


class GroundedSelection(Contract):
    """Internal opt-in wire contract; all fields required, no action authority."""

    abstain: bool
    evidence_index: int | None = Field(ge=0, le=7, strict=True)
    answer: str | None = Field(min_length=1, max_length=500, strict=True)

    @model_validator(mode="after")
    def consistent(self):
        if self.abstain:
            if self.evidence_index is not None or self.answer is not None:
                raise ValueError("Abstention requires null selection and answer.")
        elif self.evidence_index is None or self.answer is None:
            raise ValueError("An answer requires an evidence selection.")
        return self


class ReindexInput(Contract):
    task_id: UUID
    request_id: UUID = Field(default_factory=uuid4)
    mode: Mode = "FIXTURE"


class ProactiveInferenceInput(Contract):
    mode: Mode = "FIXTURE"
    context: ContextEventInput
