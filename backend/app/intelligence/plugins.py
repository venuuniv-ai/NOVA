from collections.abc import Callable
from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments, kernel_function

from app.fixtures.personal_context import DemoFixtureRepository
from app.intelligence.contracts import (
    AgentName,
    CalendarOutput,
    Contract,
    DeviceContext,
    LocationContext,
    MemoryOutput,
)
from app.intelligence.provider import ModelProvider
from app.schemas import DeviceType


class CalendarPlugin:
    def __init__(self, repository: DemoFixtureRepository):
        self._repository = repository

    @kernel_function(description="Retrieve synthetic demo events for the relative date tomorrow.")
    def get_events_for_date(self, date_label: str) -> CalendarOutput:
        return CalendarOutput(events=self._repository.calendar(date_label))

    @kernel_function(
        description="Retrieve synthetic meetings relevant to a task; no real calendar access."
    )
    def find_events_related_to_task(self, task_goal: str) -> CalendarOutput:
        return CalendarOutput(
            events=self._repository.calendar("tomorrow")
            if "meeting" in task_goal.casefold() or "tomorrow" in task_goal.casefold()
            else []
        )


class MemoryPlugin:
    def __init__(self, repository: DemoFixtureRepository):
        from app.memory.plugin import MemoryReader

        self.reader = MemoryReader()

    @kernel_function(
        description="Retrieve eligible owned preferences for a person, retaining true provenance."
    )
    def get_preferences_for_person(self, person_name: str) -> MemoryOutput:
        return self.reader.preferences(person_name)

    @kernel_function(
        description="Retrieve eligible owned user preferences, retaining true provenance."
    )
    def get_user_preferences(self) -> MemoryOutput:
        return self.reader.preferences("demo_user")


class ContextPlugin:
    def __init__(self, repository: DemoFixtureRepository):
        self._repository = repository

    @kernel_function(description="Describe the simulated current device context.")
    def get_device_context(self, device_type: DeviceType) -> DeviceContext:
        return self._repository.device(device_type)

    @kernel_function(
        description="Retrieve the synthetic meeting-end location. No real location access."
    )
    def get_demo_location_context(self) -> LocationContext:
        return self._repository.location()


class ToolRecord(Contract):
    trace_id: UUID
    agent_run_id: UUID
    plugin: str
    function: str
    status: str
    input: dict
    output: dict | None
    started_at: datetime
    completed_at: datetime
    error: str | None = None


class DeviceQuery(Contract):
    device_type: DeviceType


class TaskQuery(Contract):
    task_goal: str


class PersonQuery(Contract):
    person_name: str


class EmptyQuery(Contract):
    pass


T = TypeVar("T", bound=Contract)
ALLOWED = {
    "CONTEXT": {
        ("ContextPlugin", "get_device_context"),
        ("ContextPlugin", "get_demo_location_context"),
    },
    "CALENDAR": {
        ("CalendarPlugin", "get_events_for_date"),
        ("CalendarPlugin", "find_events_related_to_task"),
    },
    "MEMORY": {
        ("MemoryPlugin", "get_preferences_for_person"),
        ("MemoryPlugin", "get_user_preferences"),
    },
    "PLANNER": set(),
    "CRITIC": set(),
}


class KernelRuntime:
    def __init__(
        self, provider: ModelProvider, recorder: Callable[[ToolRecord], None] | None = None
    ):
        self.kernel = Kernel()
        repository = DemoFixtureRepository()
        self.memory_plugin = MemoryPlugin(repository)
        for name, plugin in [
            ("CalendarPlugin", CalendarPlugin(repository)),
            ("MemoryPlugin", self.memory_plugin),
            ("ContextPlugin", ContextPlugin(repository)),
        ]:
            self.kernel.add_plugin(plugin, plugin_name=name)
        self.kernel.add_service(provider)
        self.service_id = provider.service_id
        self.recorder = recorder

    def bind_memory(self, user_id, task_id):
        from app.memory.plugin import MemoryReader

        # Kernel keeps the registered plugin instance; bind its reader to server-owned context.
        self.memory_plugin.reader = MemoryReader(user_id, task_id)

    @property
    def provider(self) -> ModelProvider:
        service = self.kernel.get_service(self.service_id)
        if not isinstance(service, ModelProvider):
            raise TypeError("Unapproved provider service.")
        return service

    def discover(self, agent: AgentName) -> list[str]:
        return sorted(
            f"{plugin}.{function}"
            for plugin, function in ALLOWED[agent]
            if self.kernel.get_function(plugin, function)
        )

    async def invoke(
        self,
        agent: AgentName,
        run_id: UUID,
        trace_id: UUID,
        plugin: str,
        function: str,
        arguments: Contract,
        output_type: type[T],
    ) -> T:
        if (plugin, function) not in ALLOWED[agent]:
            raise PermissionError("Agent cannot invoke this capability.")
        self.kernel.get_function(
            plugin, function
        )  # Discover before invoking the registered function.
        started = datetime.now(UTC)
        stored_input = arguments.model_dump(mode="json")
        if isinstance(arguments, TaskQuery):
            stored_input = {"task_goal": "[omitted: task text]"}
        try:
            result = await self.kernel.invoke(
                plugin_name=plugin,
                function_name=function,
                arguments=KernelArguments(**arguments.model_dump()),
                metadata={"trace_id": str(trace_id)},
            )
            if result is None:
                raise ValueError("Plugin returned no result.")
            value = output_type.model_validate(result.value)
        except Exception:
            if self.recorder:
                self.recorder(
                    ToolRecord(
                        trace_id=trace_id,
                        agent_run_id=run_id,
                        plugin=plugin,
                        function=function,
                        input=stored_input,
                        output=None,
                        status="FAILED",
                        started_at=started,
                        completed_at=datetime.now(UTC),
                        error="TOOL_FAILED",
                    )
                )
            raise
        if self.recorder:
            self.recorder(
                ToolRecord(
                    trace_id=trace_id,
                    agent_run_id=run_id,
                    plugin=plugin,
                    function=function,
                    input=stored_input,
                    output=value.model_dump(mode="json"),
                    status="DONE",
                    started_at=started,
                    completed_at=datetime.now(UTC),
                )
            )
        return value
