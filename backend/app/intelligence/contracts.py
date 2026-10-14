from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas import DeviceType, IdempotencyKey

Source = Literal["DEMO_FIXTURE"]
AgentName = Literal["CONTEXT", "PLANNER", "CALENDAR", "MEMORY", "CRITIC"]
RunStatus = Literal["WAITING", "RUNNING", "DONE", "FAILED", "SKIPPED"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always")


class Provenance(Contract):
    source: Source = "DEMO_FIXTURE"
    reference: str
    memory_type: Literal["explicit_preference"] | None = None


class Evidence(Contract):
    fact: str
    provenance: Provenance
    plugin: str
    function: str


class CalendarEvent(Contract):
    title: str
    date_label: Literal["tomorrow"]
    starts_at: str
    ends_at: str
    location: str
    provenance: Provenance


class Preference(Contract):
    person: str
    preference: str
    provenance: Provenance


class DeviceContext(Contract):
    device_type: DeviceType
    simulated: Literal[True] = True
    provenance: Provenance


class LocationContext(Contract):
    description: str
    area: str
    provenance: Provenance


class SharedContext(Contract):
    device: DeviceContext | None = None
    location: LocationContext | None = None
    calendar: list[CalendarEvent] = Field(default_factory=list)
    preferences: list[Preference] = Field(default_factory=list)


class ContextNeeds(Contract):
    calendar: bool = False
    preferences: bool = False
    location: bool = False
    person: str | None = None


class ContextOutput(Contract):
    kind: Literal["context"] = "context"
    needs: ContextNeeds
    context: SharedContext


class CalendarOutput(Contract):
    kind: Literal["calendar"] = "calendar"
    events: list[CalendarEvent]


class MemoryOutput(Contract):
    kind: Literal["memory"] = "memory"
    preferences: list[Preference]


class ToolReference(Contract):
    plugin: Literal["CalendarPlugin", "MemoryPlugin", "ContextPlugin"]
    function: Literal[
        "get_events_for_date",
        "find_events_related_to_task",
        "get_preferences_for_person",
        "get_user_preferences",
        "get_device_context",
        "get_demo_location_context",
    ]


class PlanStep(Contract):
    title: str
    action: Literal["review_context", "propose_dinner", "request_confirmation", "deferred_search"]
    requires_approval: bool = False


class Plan(Contract):
    goal: str
    assumptions: list[str]
    constraints: list[Evidence]
    steps: list[PlanStep]
    required_tools: list[ToolReference]
    missing_information: list[str]
    requires_approval: bool


class PlanOutput(Contract):
    kind: Literal["plan"] = "plan"
    plan: Plan
    revision: int = Field(ge=0)


class CritiqueReason(Contract):
    code: Literal[
        "UNSUPPORTED_ASSUMPTION", "MISSING_CONTEXT", "CONFLICT", "UNNECESSARY_ACTION", "PRIVACY"
    ]
    message: str


class CriticOutput(Contract):
    kind: Literal["critic"] = "critic"
    verdict: Literal["PASS", "REVISION_REQUIRED"]
    reasons: list[CritiqueReason]


StructuredOutput = Annotated[
    ContextOutput | CalendarOutput | MemoryOutput | PlanOutput | CriticOutput,
    Field(discriminator="kind"),
]


class PriorResult(Contract):
    agent_name: AgentName
    structured_output: StructuredOutput


class AgentInput(Contract):
    task_id: UUID
    user_id: UUID
    current_device: DeviceType
    task_goal: str = Field(min_length=1, max_length=240)
    available_context: SharedContext
    prior_results: list[PriorResult] = Field(default_factory=list)
    trace_id: UUID
    needs: ContextNeeds = Field(default_factory=ContextNeeds)
    revision: int = Field(default=0, ge=0, le=2)


class AgentResult(Contract):
    agent_name: AgentName
    status: Literal["DONE"] = "DONE"
    summary: str
    structured_output: StructuredOutput
    tools_used: list[ToolReference]
    evidence: list[Evidence]
    warnings: list[str]
    started_at: datetime
    completed_at: datetime


class ProviderResponse(Contract):
    provider_name: str = "FixtureModelProvider"
    model_name: str = "nova-demo-v1"
    source: Literal["DEMO_FIXTURE", "MODEL_OUTPUT"] = "DEMO_FIXTURE"
    payload_json: str


class RunAgentsRequest(Contract):
    idempotency_key: IdempotencyKey


class ExecutionRead(Contract):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    id: UUID
    task_id: UUID
    trace_id: UUID
    status: Literal["RUNNING", "DONE", "FAILED"]
    provider: str
    model: str
    idempotency_key: str
    started_at: datetime
    completed_at: datetime | None
    error: str | None


class ToolCallRead(Contract):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    agent_run_id: UUID
    trace_id: UUID
    plugin: str
    function: str
    status: Literal["DONE", "FAILED"]
    input: dict
    output: dict | None
    started_at: datetime
    completed_at: datetime
    error: str | None


class AgentRunRead(Contract):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    task_id: UUID
    execution_id: UUID
    agent_name: AgentName
    stage: str
    status: RunStatus
    sequence: int
    trace_id: UUID
    provider: str
    model: str
    started_at: datetime | None
    completed_at: datetime | None
    summary: str
    structured_output: StructuredOutput | None
    evidence: list[Evidence]
    warnings: list[str]
    error: str | None
    tool_calls: list[ToolCallRead] = Field(default_factory=list)


class ExecutionResponse(Contract):
    execution: ExecutionRead
    replayed: bool


class IntelligenceRead(Contract):
    task_id: UUID
    execution: ExecutionRead | None
    agent_runs: list[AgentRunRead]
    context: SharedContext | None
    plan: Plan | None
    critic: CriticOutput | None
