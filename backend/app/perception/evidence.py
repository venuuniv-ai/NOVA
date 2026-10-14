from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas import DeviceType

Processor = Literal["FIXTURE_VISION", "CLIP", "DINOV2", "SAM", "FIXTURE_VLM"]
ScoreType = Literal["NONE", "CLIP_COSINE", "SAM_IOU", "VLM_SELF_REPORTED"]


class ContextEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")
    observation_id: UUID
    media_id: UUID
    processor: Processor
    model: str
    simulation: bool
    score: float | None
    score_type: ScoreType
    timestamp: datetime
    device: DeviceType
    source: Literal["IMAGE", "FIXTURE_IMAGE"]
    sha256: str
    label: str = Field(max_length=100)
    interpretation: str = Field(max_length=500)
