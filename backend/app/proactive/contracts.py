from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import ConfigDict, Field, StringConstraints

from app.intelligence.contracts import Contract
from app.schemas import IdempotencyKey

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
Recipient = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class MeetingContext(Contract):
    meeting_id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=120)
    starts_at: datetime
    location: str = Field(min_length=1, max_length=120)
    current_location: str = Field(min_length=1, max_length=120)
    travel_minutes: int = Field(ge=0, le=240)
    confidence: float = Field(ge=0, le=1)
    proactive_enabled: bool


class Situation(Contract):
    meeting: MeetingContext
    current_time: datetime
    minutes_available: float
    travel_minutes: int
    lateness_minutes: float
    arrival_at: datetime
    source: Literal["DEMO_FIXTURE"] = "DEMO_FIXTURE"


class ContextEventInput(Contract):
    task_id: UUID
    event_type: Literal["TIME_TICK", "CALENDAR_CHANGED", "DEVICE_CHANGED", "TASK_UPDATED"] = (
        "TIME_TICK"
    )
    scenario: Literal["MEETING_TRAVEL_RISK"] = "MEETING_TRAVEL_RISK"
    idempotency_key: IdempotencyKey


class ActionIntent(Contract):
    action_type: Literal["NOTIFY_ATTENDEE"] = "NOTIFY_ATTENDEE"
    recipient: Recipient
    channel: Literal["MESSAGE"] = "MESSAGE"
    content: Text
    reason: Annotated[str, StringConstraints(min_length=1, max_length=500)]
    task_id: UUID
    trace_id: UUID
    source_agent: Literal["COMMUNICATION"] = "COMMUNICATION"
    context_evidence: Situation


class CommunicationOutput(Contract):
    kind: Literal["communication"] = "communication"
    intent: ActionIntent


class CommunicationInput(Contract):
    task_id: UUID
    trace_id: UUID
    situation: Situation


class Attendee(Contract):
    recipient: Recipient
    channel: Literal["MESSAGE"] = "MESSAGE"
    source: Literal["DEMO_FIXTURE"] = "DEMO_FIXTURE"


class Mutation(Contract):
    idempotency_key: IdempotencyKey


class EditRequest(Mutation):
    content: Text
    recipient: Recipient


class DraftSituation(Contract):
    draft_contract: Literal["OWNED_CONTEXT_V1"]
    context_event_id: UUID


class ProposalRead(Contract):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    task_id: UUID
    trigger_id: UUID
    trace_id: UUID
    action_type: str
    recipient: str
    channel: str
    content: str
    reason: str
    status: str
    payload_hash: str
    policy_version: str
    policy_decision: str
    policy_reason: str
    created_at: datetime
    expires_at: datetime
    supersedes_id: UUID | None
    situation: Situation | DraftSituation
    clock_mode: Literal["FIXTURE", "SYSTEM"] = "FIXTURE"


class ApprovalRead(Contract):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    proposal_id: UUID
    user_id: UUID
    decision: str
    payload_hash: str
    created_at: datetime
    expires_at: datetime


class ExecutionRead(Contract):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    proposal_id: UUID
    approval_id: UUID
    idempotency_key: str
    adapter: str
    status: str
    receipt: dict
    started_at: datetime
    completed_at: datetime
    safe_error: str | None


class ProposalDetail(Contract):
    proposal: ProposalRead
    approval: ApprovalRead | None
    execution: ExecutionRead | None


class EvaluationRead(Contract):
    trigger_id: UUID
    trace_id: UUID
    status: str
    reason: str
    situation: Situation
    proposal: ProposalRead | None


class AuditRead(Contract):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    event_type: str
    user_id: UUID
    task_id: UUID
    proposal_id: UUID | None
    trace_id: UUID
    created_at: datetime
    safe_metadata: dict
