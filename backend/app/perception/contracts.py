from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from app.intelligence.contracts import Contract
from app.perception.evidence import ContextEvidence
from app.schemas import DeviceType, IdempotencyKey

Processor = Literal["FIXTURE_VISION", "CLIP", "DINOV2", "SAM", "FIXTURE_VLM", "LOCAL_VLM"]
ScoreType = Literal["NONE", "CLIP_COSINE", "SAM_IOU", "VLM_SELF_REPORTED"]


class Region(Contract):
    x: float = Field(ge=0, le=1, allow_inf_nan=False)
    y: float = Field(ge=0, le=1, allow_inf_nan=False)
    width: float = Field(gt=0, le=1, allow_inf_nan=False)
    height: float = Field(gt=0, le=1, allow_inf_nan=False)

    @model_validator(mode="after")
    def bounds(self):
        if self.x + self.width > 1 or self.y + self.height > 1:
            raise ValueError("Region escapes image.")
        return self


class VisualOutput(Contract):
    observation_type: Literal[
        "OBJECT", "SCENE", "SEMANTIC_MATCH", "REGION", "SEGMENT", "TEXTUAL_INTERPRETATION"
    ]
    label: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    processor: Processor
    model: str = Field(min_length=1, max_length=120)
    simulation: bool
    score: float | None = Field(default=None, ge=-1, le=1, allow_inf_nan=False)
    score_type: ScoreType = "NONE"
    region: Region | None = None
    mask_reference: UUID | None = None

    @model_validator(mode="after")
    def semantics(self):
        fixture = self.processor.startswith("FIXTURE")
        if fixture != self.simulation:
            raise ValueError("Processor origin contradicts simulation.")
        expected = {"CLIP": "CLIP_COSINE", "SAM": "SAM_IOU"}.get(self.processor, "NONE")
        if self.score_type != expected or (self.score is None) != (expected == "NONE"):
            raise ValueError("Score semantics contradict processor.")
        if self.processor != "SAM" and (self.region or self.mask_reference):
            raise ValueError("Only SAM returns geometry in Phase 5.")
        if self.processor == "SAM" and (
            self.score < 0 or not self.region or not self.mask_reference
        ):
            raise ValueError("SAM requires nonnegative IOU and bound mask geometry.")
        if fixture and (self.region or self.mask_reference):
            raise ValueError("Fixture has no geometry.")
        if self.processor == "CLIP" and self.observation_type != "SEMANTIC_MATCH":
            raise ValueError("CLIP is semantic similarity, not detection.")
        if self.processor == "DINOV2" and self.observation_type != "REGION":
            raise ValueError("DINO provides features, not semantic labels.")
        if self.processor == "SAM" and self.observation_type != "SEGMENT":
            raise ValueError("SAM provides segmentation, not semantic identity.")
        return self


class VisionOutput(Contract):
    observations: list[VisualOutput] = Field(max_length=16)
    interpretation: str = Field(max_length=500)


class PerceptionRequest(Contract):
    media_id: UUID
    idempotency_key: IdempotencyKey
    privacy_class: Literal["PERSONAL", "SENSITIVE_LOCAL_ONLY"] = "PERSONAL"
    processors: list[Literal["FIXTURE_VISION", "CLIP", "DINOV2", "SAM"]] = Field(
        default_factory=lambda: ["FIXTURE_VISION", "CLIP", "DINOV2", "SAM"], max_length=4
    )
    use_vlm: bool = True
    allow_fixture: bool = True

    @model_validator(mode="after")
    def unique_processors(self):
        if len(set(self.processors)) != len(self.processors):
            raise ValueError("Duplicate processor.")
        return self


class FixtureRequest(Contract):
    idempotency_key: IdempotencyKey


class ObservationRead(VisualOutput):
    id: UUID
    media_id: UUID
    sha256: str
    source: Literal["IMAGE", "FIXTURE_IMAGE"]
    device: DeviceType
    created_at: datetime
    evidence: str = "Untrusted visual evidence; no authorization or memory write."


class ReasonRequest(Contract):
    idempotency_key: IdempotencyKey
    propose_action: bool = False


class PerceptionResult(Contract):
    id: UUID
    task_id: UUID
    media_id: UUID
    trace_id: UUID
    privacy_class: str
    status: Literal["RUNNING", "DONE", "PARTIAL", "FAILED"]
    simulation: bool
    processors: list[dict]
    observations: list[ObservationRead]
    context: list[ContextEvidence]
    warnings: list[str]
    started_at: datetime
    completed_at: datetime | None
    replayed: bool = False
