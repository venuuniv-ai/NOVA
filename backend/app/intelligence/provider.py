from abc import ABC, abstractmethod

from semantic_kernel.services.ai_service_client_base import AIServiceClientBase

from app.fixtures.personal_context import context_evidence
from app.intelligence.contracts import (
    AgentInput,
    AgentName,
    ContextNeeds,
    ContextOutput,
    Plan,
    PlanOutput,
    PlanStep,
    ProviderResponse,
    ToolReference,
)
from app.intelligence.policy import review_plan


class ModelProvider(AIServiceClientBase, ABC):
    """A kernel-registered service contract; no commercial transport is implemented."""

    provider_name: str
    model_name: str
    capabilities: tuple[str, ...]

    @abstractmethod
    async def generate_structured(self, agent: AgentName, payload: AgentInput) -> ProviderResponse:
        raise NotImplementedError


class FixtureModelProvider(ModelProvider):
    service_id: str = "fixture"
    ai_model_id: str = "nova-demo-v1"
    provider_name: str = "FixtureModelProvider"
    model_name: str = "nova-demo-v1"
    capabilities: tuple[str, ...] = ("structured_output", "deterministic", "DEMO_FIXTURE")

    async def generate_structured(self, agent: AgentName, payload: AgentInput) -> ProviderResponse:
        goal = payload.task_goal.casefold()
        if agent == "CONTEXT":
            output = ContextOutput(
                needs=ContextNeeds(
                    calendar="meeting" in goal or "tomorrow" in goal,
                    preferences="dinner" in goal or "preference" in goal,
                    location="dinner" in goal or "location" in goal,
                    person="Sarah" if "sarah" in goal else None,
                ),
                context=payload.available_context,
            )
        elif agent == "PLANNER":
            constraints = context_evidence(payload.available_context)
            required = []
            missing = []
            if payload.needs.calendar and not payload.available_context.calendar:
                required.append(
                    ToolReference(plugin="CalendarPlugin", function="find_events_related_to_task")
                )
                missing.append("Synthetic calendar context has not been retrieved.")
            if payload.needs.preferences and not payload.available_context.preferences:
                required.append(
                    ToolReference(plugin="MemoryPlugin", function="get_user_preferences")
                )
                missing.append("Explicit synthetic preferences have not been retrieved.")
            dinner = "dinner" in goal
            if dinner:
                missing.extend(
                    [
                        "Actual restaurant options and availability are unknown.",
                        "Sarah's availability is unconfirmed.",
                    ]
                )
            steps = [
                PlanStep(
                    title="Review the supplied context and explicit constraints.",
                    action="review_context",
                )
            ]
            if dinner:
                steps.extend(
                    [
                        PlanStep(
                            title=(
                                "Propose dinner consistent with the recorded time, "
                                "area, and cuisine preferences."
                            ),
                            action="propose_dinner",
                        ),
                        PlanStep(
                            title="Ask the user to confirm the proposal and Sarah's availability.",
                            action="request_confirmation",
                            requires_approval=True,
                        ),
                        PlanStep(
                            title=(
                                "Restaurant discovery is deferred to a later external-tool phase; "
                                "no restaurants were searched."
                            ),
                            action="deferred_search",
                            requires_approval=True,
                        ),
                    ]
                )
            output = PlanOutput(
                revision=payload.revision,
                plan=Plan(
                    goal=payload.task_goal,
                    assumptions=["All personal context is synthetic DEMO_FIXTURE data."],
                    constraints=constraints,
                    steps=steps,
                    required_tools=required,
                    missing_information=missing,
                    requires_approval=dinner,
                ),
            )
        elif agent == "CRITIC":
            output = review_plan(payload)

        else:
            raise ValueError(
                "Specialists return validated plugin evidence, not generated model content."
            )
        return ProviderResponse(payload_json=output.model_dump_json())
