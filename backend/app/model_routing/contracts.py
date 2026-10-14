from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import Field, StringConstraints, model_validator

from app.intelligence.contracts import Contract
from app.schemas import DeviceType

Privacy = Literal["PUBLIC", "INTERNAL", "PERSONAL", "SENSITIVE_LOCAL_ONLY"]
Complexity = Literal["LOW", "MEDIUM", "HIGH", "REASONING"]
Tier = Literal["FIXTURE", "SMALL", "FRONTIER", "REASONING", "VISION", "LOCAL"]
Capability = Literal["TEXT", "STRUCTURED", "REASONING", "REASONING_REPLAY"]
Purpose = Literal["SUMMARY", "PLANNING", "CRITIQUE", "CONTEXT", "COMMUNICATION"]
ErrorCode = Literal[
    "TIMEOUT",
    "UNAVAILABLE",
    "RATE_LIMITED",
    "INVALID_RESPONSE",
    "CONTEXT_LIMIT",
    "AUTH_ERROR",
    "BUDGET_BLOCKED",
    "POLICY_BLOCKED",
    "UNKNOWN_PROVIDER_ERROR",
]


class TextOutput(Contract):
    summary: Annotated[str, StringConstraints(min_length=1, max_length=4000)]


class ModelRequest(Contract):
    request_id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    trace_id: UUID
    user_id: UUID
    modality: Literal["TEXT"] = "TEXT"
    purpose: Purpose
    structured_input: dict
    required_capabilities: list[Capability] = Field(default_factory=lambda: ["TEXT"], max_length=4)
    privacy_class: Privacy = "INTERNAL"
    complexity: Complexity = "LOW"
    preferred_latency: Literal["FAST", "BALANCED", "QUALITY"] = "BALANCED"
    current_device: DeviceType
    max_output_tokens: int = Field(default=512, ge=16, le=4096)
    mode: Literal["NORMAL", "POLICY_REPLAY"] = "NORMAL"
    schema_version: Literal["nova-model-v1"] = "nova-model-v1"

    @model_validator(mode="after")
    def bounded_input(self):
        import json

        if len(json.dumps(self.structured_input, ensure_ascii=False).encode()) > 32000:
            raise ValueError("Model input exceeds the bounded context size.")
        return self


class Price(Contract):
    input_cost_per_million: Decimal = Field(ge=0, le=10000)
    output_cost_per_million: Decimal = Field(ge=0, le=10000)
    currency: Literal["USD"] = "USD"
    effective_date: str = Field(min_length=1, max_length=30)
    source: str = Field(min_length=1, max_length=200)


class ProviderSpec(Contract):
    provider: str = Field(min_length=1, max_length=80)
    model: str = Field(min_length=1, max_length=120)
    kind: Literal["FIXTURE", "LOCAL", "CLOUD", "TEST_POLICY"]
    tiers: list[Tier]
    capabilities: list[Capability]
    enabled: bool
    input_token_limit: int = Field(default=32768, ge=128, le=131072)
    output_token_limit: int = Field(default=4096, ge=16, le=4096)
    latency_class: Literal["FAST", "BALANCED", "SLOW"] = "BALANCED"
    strength: int = Field(default=1, ge=0, le=10)
    priced_external: bool = False
    price: Price | None = None


class ProviderResult(Contract):
    output: dict
    finish_reason: Literal["stop", "length", "fixture"]
    input_tokens: int | None = Field(default=None, ge=0, strict=True)
    output_tokens: int | None = Field(default=None, ge=0, strict=True)
    usage_source: Literal["PROVIDER_REPORTED", "LOCAL_ESTIMATED", "UNKNOWN"] = "UNKNOWN"

    @model_validator(mode="after")
    def consistent_usage(self):
        if (self.input_tokens is None) != (self.output_tokens is None):
            raise ValueError("Partial token usage is not reliable usage.")
        if self.usage_source == "PROVIDER_REPORTED" and self.input_tokens is None:
            raise ValueError("Reported usage requires counts.")
        if self.usage_source == "UNKNOWN" and self.input_tokens is not None:
            raise ValueError("Unknown usage cannot invent counts.")
        return self


class Candidate(Contract):
    provider: str
    model: str
    eligible: bool
    reasons: list[str]


class RoutingDecision(Contract):
    selected_provider: str | None
    selected_model: str | None
    selected_tier: Tier | None
    primary_preference: str
    candidates: list[Candidate]
    reason_codes: list[str]
    privacy_class: Privacy
    complexity: Complexity
    classification_reason: str
    privacy_decision: str
    budget_decision: str
    fallback_chain: list[str]
    cache_eligible: bool
    policy_version: str = "routing-v1"
    device_context: DeviceType


class ModelResponse(Contract):
    request_id: UUID
    task_id: UUID
    trace_id: UUID
    provider: str | None
    model: str | None
    route_tier: Tier | None
    output: dict | None
    finish_reason: str | None
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    latency_ms: float | None
    usage_source: Literal["PROVIDER_REPORTED", "LOCAL_ESTIMATED", "UNKNOWN"]
    estimated_cost_usd: Decimal | None
    cost_status: str
    cache_status: Literal["HIT", "MISS", "BYPASS", "ERROR"]
    fallback_used: bool
    status: Literal["DONE", "FAILED", "RUNNING"]
    safe_error: ErrorCode | None
    decision: RoutingDecision
    mode: Literal["NORMAL", "POLICY_REPLAY"]
    replayed: bool = False


class EvaluateRequest(Contract):
    task_id: UUID
    request_id: UUID = Field(default_factory=uuid4)
    scenario: Literal["SIMPLE", "REASONING", "PRIVACY", "BUDGET", "FAILURE"] = "SIMPLE"
    privacy_class: Privacy | None = None
    preferred_latency: Literal["FAST", "BALANCED", "QUALITY"] = "BALANCED"
    max_output_tokens: int = Field(default=512, ge=16, le=4096)
