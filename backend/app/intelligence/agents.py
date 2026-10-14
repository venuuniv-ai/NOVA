from abc import ABC, abstractmethod
from datetime import UTC, datetime
from uuid import UUID

from app.fixtures.personal_context import context_evidence
from app.intelligence.contracts import (
    AgentInput,
    AgentName,
    AgentResult,
    CalendarOutput,
    ContextOutput,
    CriticOutput,
    DeviceContext,
    LocationContext,
    MemoryOutput,
    PlanOutput,
    SharedContext,
    ToolReference,
)
from app.intelligence.plugins import DeviceQuery, EmptyQuery, KernelRuntime, PersonQuery, TaskQuery
from app.intelligence.policy import review_plan


class Agent(ABC):
    name: AgentName

    @abstractmethod
    async def execute(
        self, payload: AgentInput, runtime: KernelRuntime, run_id: UUID
    ) -> AgentResult:
        raise NotImplementedError

    def result(
        self, started: datetime, output, summary: str, tools: list[ToolReference], evidence
    ) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            summary=summary,
            structured_output=output,
            tools_used=tools,
            evidence=evidence,
            warnings=["Synthetic personal context; no outbound actions were executed."],
            started_at=started,
            completed_at=datetime.now(UTC),
        )


class ContextAgent(Agent):
    name: AgentName = "CONTEXT"

    async def execute(self, payload, runtime, run_id):
        started = datetime.now(UTC)
        response = await runtime.provider.generate_structured(self.name, payload)
        output = ContextOutput.model_validate_json(response.payload_json)
        device = await runtime.invoke(
            self.name,
            run_id,
            payload.trace_id,
            "ContextPlugin",
            "get_device_context",
            DeviceQuery(device_type=payload.current_device),
            DeviceContext,
        )
        tools = [ToolReference(plugin="ContextPlugin", function="get_device_context")]
        location = None
        if output.needs.location:
            location = await runtime.invoke(
                self.name,
                run_id,
                payload.trace_id,
                "ContextPlugin",
                "get_demo_location_context",
                EmptyQuery(),
                LocationContext,
            )
            tools.append(
                ToolReference(plugin="ContextPlugin", function="get_demo_location_context")
            )
        output.context = SharedContext(
            device=device,
            location=location,
            visual_evidence=payload.available_context.visual_evidence,
        )
        return self.result(
            started,
            output,
            "Identified required context and retrieved bounded simulated device/location context.",
            tools,
            context_evidence(output.context),
        )


class CalendarAgent(Agent):
    name: AgentName = "CALENDAR"

    async def execute(self, payload, runtime, run_id):
        started = datetime.now(UTC)
        output = await runtime.invoke(
            self.name,
            run_id,
            payload.trace_id,
            "CalendarPlugin",
            "find_events_related_to_task",
            TaskQuery(task_goal=payload.task_goal),
            CalendarOutput,
        )
        return self.result(
            started,
            output,
            "Retrieved relevant synthetic meeting evidence.",
            [ToolReference(plugin="CalendarPlugin", function="find_events_related_to_task")],
            context_evidence(SharedContext(calendar=output.events)),
        )


class MemoryAgent(Agent):
    name: AgentName = "MEMORY"

    async def execute(self, payload, runtime, run_id):
        started = datetime.now(UTC)
        preferences = []
        tools = []
        if payload.needs.person:
            person = await runtime.invoke(
                self.name,
                run_id,
                payload.trace_id,
                "MemoryPlugin",
                "get_preferences_for_person",
                PersonQuery(person_name=payload.needs.person),
                MemoryOutput,
            )
            preferences.extend(person.preferences)
            tools.append(
                ToolReference(plugin="MemoryPlugin", function="get_preferences_for_person")
            )
        user = await runtime.invoke(
            self.name,
            run_id,
            payload.trace_id,
            "MemoryPlugin",
            "get_user_preferences",
            EmptyQuery(),
            MemoryOutput,
        )
        preferences.extend(user.preferences)
        tools.append(ToolReference(plugin="MemoryPlugin", function="get_user_preferences"))
        output = MemoryOutput(preferences=preferences)
        return self.result(
            started,
            output,
            "Retrieved explicit synthetic preferences with provenance.",
            tools,
            context_evidence(SharedContext(preferences=preferences)),
        )


class PlannerAgent(Agent):
    name: AgentName = "PLANNER"

    async def execute(self, payload, runtime, run_id):
        started = datetime.now(UTC)
        response = await runtime.provider.generate_structured(self.name, payload)
        output = PlanOutput.model_validate_json(response.payload_json)
        return self.result(
            started,
            output,
            "Revised plan using specialist evidence."
            if payload.revision
            else "Initial plan identifies missing context and required specialist capabilities.",
            [],
            output.plan.constraints,
        )


class CriticAgent(Agent):
    name: AgentName = "CRITIC"

    async def execute(self, payload, runtime, run_id):
        started = datetime.now(UTC)
        response = await runtime.provider.generate_structured(self.name, payload)
        output = CriticOutput.model_validate_json(response.payload_json)
        policy = review_plan(payload)
        if policy.verdict == "REVISION_REQUIRED":
            output = policy
        return self.result(
            started,
            output,
            f"Critic result: {output.verdict}. Plan remains owned by Planner.",
            [],
            [],
        )
