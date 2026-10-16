from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_session
from app.intelligence.contracts import ExecutionResponse, RunAgentsRequest
from app.intelligence.orchestrator import AgentOrchestrator
from app.intelligence.plugins import KernelRuntime
from app.model_routing.budget import BudgetPolicy
from app.model_routing.contracts import EvaluateRequest, ModelRequest, ModelResponse
from app.model_routing.kernel_provider import PreparedDraftProvider, RoutedModelProvider
from app.model_routing.models import BudgetDay, ModelCall
from app.model_routing.providers import FixtureInferenceProvider
from app.model_routing.registry import ProviderRegistry, registry
from app.model_routing.replay import BudgetProbeProvider, FailureProbeProvider
from app.model_routing.service import ModelRoutingService
from app.models import Device
from app.proactive.clock import FixtureClock
from app.proactive.communication import CommunicationAgent, register_communication
from app.proactive.contracts import CommunicationInput, ContextEventInput, EvaluationRead
from app.proactive.models import ContextEvent
from app.proactive.service import ProactiveService
from app.proactive.trigger import ProactiveTriggerEngine, demo_meeting
from app.security.identity import current_user_id
from app.service import fail, find_task

router = APIRouter(prefix="/api/v1", tags=["model-router"])
DB = Annotated[Session, Depends(get_session)]


SCENARIO_PROMPTS = {
    "SIMPLE": "Summarize tomorrow's schedule.",
    "REASONING": (
        "Review tomorrow's meetings, travel constraints, and preferences "
        "and determine whether anything requires planning."
    ),
    "PRIVACY": "Reconcile highly sensitive local-only context.",
    "BUDGET": "Summarize generic budget policy.",
    "FAILURE": "Summarize generic fallback policy.",
}


def routing_service():
    return ModelRoutingService()


Service = Annotated[ModelRoutingService, Depends(routing_service)]


@router.post("/model-router/evaluate", response_model=ModelResponse)
def evaluate(
    payload: EvaluateRequest, request: Request, response: Response, session: DB, service: Service
):
    task = find_task(session, payload.task_id)
    device = session.get(Device, task.current_device_id)
    previous = session.scalar(
        select(ModelCall).where(
            ModelCall.user_id == task.user_id, ModelCall.request_id == payload.request_id
        )
    )
    # Original-key acknowledgment retains the captured routing device after a handoff.
    captured_device = (
        previous.routing_decision["device_context"]
        if previous and previous.task_id == task.id
        else device.type
    )
    model_request = ModelRequest(
        request_id=payload.request_id,
        task_id=task.id,
        user_id=task.user_id,
        trace_id=uuid4(),
        purpose="SUMMARY",
        structured_input={"instruction": SCENARIO_PROMPTS[payload.scenario]},
        required_capabilities=["TEXT"],
        privacy_class="SENSITIVE_LOCAL_ONLY"
        if payload.scenario == "PRIVACY"
        else payload.privacy_class or "PERSONAL",
        complexity="REASONING" if payload.scenario in {"REASONING", "PRIVACY"} else "LOW",
        current_device=captured_device,
        max_output_tokens=payload.max_output_tokens,
        preferred_latency=payload.preferred_latency,
        mode="POLICY_REPLAY" if payload.scenario in {"BUDGET", "FAILURE"} else "NORMAL",
    )
    # Replay probes cannot construct network transports or execute actual priced models.
    if payload.scenario == "BUDGET":
        service = ModelRoutingService(
            providers=ProviderRegistry([BudgetProbeProvider(), FixtureInferenceProvider()]),
            cache=service.cache,
            budget=BudgetPolicy(Decimal(0), Decimal(0)),
            allow_personal_cloud=True,
        )
    elif payload.scenario == "FAILURE":
        service = ModelRoutingService(
            providers=ProviderRegistry([FailureProbeProvider(), FixtureInferenceProvider()]),
            cache=service.cache,
            budget=service.budget,
        )
    session.commit()  # No task read transaction remains held across inference.
    result = service.run(model_request, request.state.correlation_id)
    response.headers["X-Trace-ID"] = str(result.trace_id)
    return result


def safe_call(call):
    return {
        "id": str(call.id),
        "task_id": str(call.task_id),
        "request_id": str(call.request_id),
        "trace_id": str(call.trace_id),
        "purpose": call.purpose,
        "status": call.status,
        "decision": call.routing_decision,
        "attempts": call.attempts,
        "response": call.response_metadata,
        "started_at": call.started_at,
        "completed_at": call.completed_at,
        "safe_error": call.safe_error,
        "accounted_exposure_usd": call.accounted_cost_usd,
    }


@router.get("/model-router/providers")
def providers():
    return {
        "providers": registry.describe(),
        "scenarios": SCENARIO_PROMPTS,
        "local_runtime": "LOCAL RUNTIME NOT CONFIGURED"
        if not settings.local_model_enabled or not settings.local_model_name
        else "CONFIGURED ENDPOINT ONLY / SEE HEALTH",
        "cloud": "ARCHITECTURE ONLY / DISABLED / NO PAID PROVIDERS ENABLED",
    }


@router.get("/model-router/calls")
def calls(session: DB):
    return [
        safe_call(c)
        for c in session.scalars(
            select(ModelCall)
            .where(ModelCall.user_id == current_user_id())
            .order_by(ModelCall.started_at.desc())
            .limit(100)
        )
    ]


@router.get("/tasks/{task_id}/model-calls")
def task_calls(task_id: UUID, session: DB):
    find_task(session, task_id)
    return [
        safe_call(c)
        for c in session.scalars(
            select(ModelCall)
            .where(ModelCall.task_id == task_id, ModelCall.user_id == current_user_id())
            .order_by(ModelCall.started_at.desc())
            .limit(100)
        )
    ]


@router.get("/model-router/budget")
def budget(session: DB):
    day = datetime.now(UTC).date()
    row = session.get(BudgetDay, (current_user_id(), day))
    consumed, reserved = (row.consumed_usd, row.reserved_usd) if row else (Decimal(0), Decimal(0))
    return {
        "day": day.isoformat(),
        "timezone": "UTC",
        "daily_budget_usd": settings.daily_ai_budget_usd,
        "per_request_cap_usd": settings.max_request_cost_usd,
        "consumed_usd": consumed,
        "reserved_usd": reserved,
        "remaining_usd": max(Decimal(0), settings.daily_ai_budget_usd - consumed - reserved),
        "paid_providers_enabled": False,
        "disclosure": "NO PAID PROVIDERS ENABLED; local compute/electricity not priced",
    }


@router.post(
    "/tasks/{task_id}/run-routed-agents", response_model=ExecutionResponse, status_code=201
)
def routed_agents(task_id: UUID, payload: RunAgentsRequest, request: Request, response: Response):
    result = AgentOrchestrator(
        provider=RoutedModelProvider(correlation_id=request.state.correlation_id)
    ).run(task_id, payload.idempotency_key, request.state.correlation_id)
    response.status_code = 200 if result.replayed else 201
    response.headers["X-Trace-ID"] = str(result.execution.trace_id)
    return result


@router.post("/proactive/evaluate-routed", response_model=EvaluationRead)
def routed_proactive(payload: ContextEventInput, request: Request, response: Response, session: DB):
    import asyncio

    task = find_task(session, payload.task_id)
    prior = session.scalar(
        select(ContextEvent).where(
            ContextEvent.task_id == task.id,
            ContextEvent.user_id == task.user_id,
            ContextEvent.idempotency_key == payload.idempotency_key,
        )
    )
    if prior:
        session.commit()
        result = ProactiveService().evaluate(payload, request.state.correlation_id)
    else:
        device = session.get(Device, task.current_device_id)
        trace_id = uuid5(
            NAMESPACE_URL, f"nova:routed-context:{task.user_id}:{task.id}:{payload.idempotency_key}"
        )
        clock = FixtureClock()
        situation, reason = ProactiveTriggerEngine(clock).analyze(demo_meeting(clock, str(task.id)))
        if reason != "SURFACE":
            session.commit()
            result = ProactiveService(clock=clock).evaluate(payload, request.state.correlation_id)
        else:
            draft_input = CommunicationInput(
                task_id=task.id, trace_id=trace_id, situation=situation
            )
            provider = RoutedModelProvider(
                correlation_id=request.state.correlation_id,
                communication_request_id=uuid5(trace_id, "communication-v1"),
                communication_device=device.type,
            )
            session.commit()  # Inference occurs before action locks.
            runtime = KernelRuntime(provider)
            register_communication(runtime)
            try:
                draft = asyncio.run(CommunicationAgent().execute(draft_input, runtime, uuid4()))
            except Exception:
                fail(
                    409,
                    "DRAFT_PREPARATION_UNCONFIRMED",
                    "Draft was not confirmed. Review model history; "
                    "a new event key may be required.",
                )
            from app.intelligence.contracts import ProviderResponse

            completed = session.scalar(
                select(ModelCall).where(
                    ModelCall.user_id == current_user_id(),
                    ModelCall.request_id == provider.communication_request_id,
                )
            )
            prepared = PreparedDraftProvider(
                prepared_input=draft_input,
                provider_name=f"NOVA ModelRouter / {completed.provider}",
                model_name=completed.model,
                prepared_response=ProviderResponse(
                    provider_name=completed.provider,
                    model_name=completed.model,
                    source="DEMO_FIXTURE" if completed.tier == "FIXTURE" else "MODEL_OUTPUT",
                    payload_json=draft.model_dump_json(),
                ),
            )
            session.commit()
            result = ProactiveService(clock=clock, provider=prepared, trace_id=trace_id).evaluate(
                payload, request.state.correlation_id
            )
    response.headers["X-Trace-ID"] = str(result.trace_id)
    return result
