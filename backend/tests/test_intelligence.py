import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select

from app.database import SessionLocal
from app.fixtures.personal_context import DemoFixtureRepository
from app.intelligence.agents import (
    CalendarAgent,
    ContextAgent,
    CriticAgent,
    MemoryAgent,
    PlannerAgent,
)
from app.intelligence.contracts import (
    AgentInput,
    AgentResult,
    CalendarOutput,
    ContextNeeds,
    ContextOutput,
    CriticOutput,
    DeviceContext,
    MemoryOutput,
    PlanOutput,
    PriorResult,
    ProviderResponse,
    SharedContext,
)
from app.intelligence.models import AgentExecution, AgentRun, ToolCall
from app.intelligence.orchestrator import recover_interrupted_executions
from app.intelligence.plugins import (
    CalendarPlugin,
    DeviceQuery,
    EmptyQuery,
    KernelRuntime,
    MemoryPlugin,
    PersonQuery,
    TaskQuery,
)
from app.intelligence.provider import FixtureModelProvider
from app.seed import DEMO_USER_ID


def agent_input(**overrides):
    return AgentInput(
        task_id=uuid4(),
        user_id=DEMO_USER_ID,
        current_device="DESKTOP",
        task_goal="Find somewhere for dinner with Sarah tomorrow after my meeting.",
        available_context=SharedContext(),
        trace_id=uuid4(),
        **overrides,
    )


def test_contract_rejects_extra_fields_invalid_device_and_goal():
    payload = agent_input().model_dump()
    for updates in [{"current_device": "REAL_APPLE_DEVICE"}, {"task_goal": ""}, {"shell": "ls"}]:
        with pytest.raises(ValidationError):
            AgentInput.model_validate({**payload, **updates})


def test_fixture_provider_is_deterministic_and_kernel_registered():
    provider = FixtureModelProvider()
    payload = agent_input()
    first = asyncio.run(provider.generate_structured("CONTEXT", payload))
    assert first == asyncio.run(provider.generate_structured("CONTEXT", payload))
    assert first.source == "DEMO_FIXTURE"
    assert first.provider_name == "FixtureModelProvider"
    runtime = KernelRuntime(provider)
    assert runtime.provider is provider
    assert "ContextPlugin.get_device_context" in runtime.discover("CONTEXT")


@pytest.mark.parametrize("person, count", [("Sarah", 1), ("Unknown", 0), ("demo_user", 1)])
def test_explicit_fixture_memories_have_provenance(person, count):
    entries = DemoFixtureRepository().preferences(person)
    assert len(entries) == count
    assert all(
        entry.provenance.source == "DEMO_FIXTURE"
        and entry.provenance.memory_type == "explicit_preference"
        for entry in entries
    )


def test_calendar_plugin_dates_and_task_relevance():
    plugin = CalendarPlugin(DemoFixtureRepository())
    assert plugin.get_events_for_date("tomorrow").events[0].title == "Product Review"
    assert plugin.get_events_for_date("yesterday").events == []
    assert plugin.find_events_related_to_task("A meeting tomorrow").events[0].ends_at == "17:00"
    assert plugin.find_events_related_to_task("A shopping list").events == []


def test_memory_plugin_returns_only_explicit_synthetic_records():
    plugin = MemoryPlugin(DemoFixtureRepository())
    assert "Italian" in plugin.get_preferences_for_person("Sarah").preferences[0].preference
    assert "6:00 PM" in plugin.get_user_preferences().preferences[0].preference
    assert plugin.get_preferences_for_person("stranger").preferences == []


@pytest.mark.parametrize(
    "agent, plugin, function, query, output",
    [
        (
            "CONTEXT",
            "ContextPlugin",
            "get_device_context",
            DeviceQuery(device_type="WEARABLE"),
            DeviceContext,
        ),
        (
            "CALENDAR",
            "CalendarPlugin",
            "find_events_related_to_task",
            TaskQuery(task_goal="meeting"),
            CalendarOutput,
        ),
        (
            "MEMORY",
            "MemoryPlugin",
            "get_preferences_for_person",
            PersonQuery(person_name="Sarah"),
            MemoryOutput,
        ),
        ("MEMORY", "MemoryPlugin", "get_user_preferences", EmptyQuery(), MemoryOutput),
    ],
)
def test_plugins_are_actually_invoked_through_semantic_kernel(
    agent, plugin, function, query, output
):
    records = []
    runtime = KernelRuntime(FixtureModelProvider(), records.append)
    value = asyncio.run(runtime.invoke(agent, uuid4(), uuid4(), plugin, function, query, output))
    assert isinstance(value, output)
    assert records[0].plugin == plugin and records[0].status == "DONE"
    if isinstance(query, TaskQuery):
        assert records[0].input["task_goal"] == "[omitted: task text]"


def test_capability_policy_rejects_wrong_agent_and_arbitrary_function():
    runtime = KernelRuntime(FixtureModelProvider())
    for plugin, function in [("MemoryPlugin", "get_user_preferences"), ("ShellPlugin", "exec")]:
        with pytest.raises(PermissionError):
            asyncio.run(
                runtime.invoke(
                    "PLANNER", uuid4(), uuid4(), plugin, function, EmptyQuery(), MemoryOutput
                )
            )


@pytest.mark.parametrize(
    "agent, expected",
    [
        (ContextAgent(), ContextOutput),
        (CalendarAgent(), CalendarOutput),
        (MemoryAgent(), MemoryOutput),
        (PlannerAgent(), PlanOutput),
        (CriticAgent(), CriticOutput),
    ],
)
def test_each_agent_returns_typed_execution_contract(agent, expected):
    payload = agent_input(
        needs=ContextNeeds(calendar=True, preferences=True, location=True, person="Sarah")
    )
    result = asyncio.run(agent.execute(payload, KernelRuntime(FixtureModelProvider()), uuid4()))
    assert isinstance(result, AgentResult)
    assert isinstance(result.structured_output, expected)
    assert result.agent_name == agent.name and result.status == "DONE"
    assert result.completed_at >= result.started_at
    if agent.name == "CALENDAR":
        assert result.evidence and result.tools_used[0].plugin == "CalendarPlugin"
    if agent.name == "MEMORY":
        assert len(result.structured_output.preferences) == 2


def test_critic_rejects_missing_plan_and_unsupported_assumptions():
    provider = FixtureModelProvider()
    payload = agent_input()
    missing = CriticOutput.model_validate_json(
        asyncio.run(provider.generate_structured("CRITIC", payload)).payload_json
    )
    assert missing.verdict == "REVISION_REQUIRED"
    proposed = PlanOutput.model_validate_json(
        asyncio.run(provider.generate_structured("PLANNER", payload)).payload_json
    )
    proposed.plan.assumptions.append("A restaurant was booked without asking.")
    payload.prior_results = [PriorResult(agent_name="PLANNER", structured_output=proposed)]
    rejected = CriticOutput.model_validate_json(
        asyncio.run(provider.generate_structured("CRITIC", payload)).payload_json
    )
    assert rejected.verdict == "REVISION_REQUIRED"
    assert any(reason.code == "UNSUPPORTED_ASSUMPTION" for reason in rejected.reasons)


def run_api(client, task_id, key="intelligence-test"):
    return client.post(f"/api/v1/tasks/{task_id}/run-agents", json={"idempotency_key": key})


def test_dinner_orchestration_order_revision_trace_persistence_and_handoff(client, task, devices):
    response = run_api(client, task["id"])
    assert response.status_code == 201, response.text
    execution = response.json()["execution"]
    assert execution["status"] == "DONE", response.text
    trace = execution["trace_id"]
    assert response.headers["X-Trace-ID"] == trace
    runs = client.get(f"/api/v1/tasks/{task['id']}/agent-runs").json()
    assert [run["stage"] for run in runs] == [
        "context",
        "planner",
        "calendar",
        "memory",
        "planner_revision",
        "critic",
    ]
    assert all(run["status"] == "DONE" and run["trace_id"] == trace for run in runs)
    assert runs[1]["structured_output"]["plan"]["required_tools"]
    assert runs[4]["structured_output"]["revision"] == 1
    assert runs[5]["structured_output"]["verdict"] == "PASS"
    tools = [tool for run in runs for tool in run["tool_calls"]]
    assert len(tools) == 5 and all(tool["trace_id"] == trace for tool in tools)
    assert any(tool["plugin"] == "CalendarPlugin" for tool in tools)
    assert any(tool["plugin"] == "MemoryPlugin" for tool in tools)
    intelligence = client.get(f"/api/v1/tasks/{task['id']}/plan").json()
    facts = [fact["fact"] for fact in intelligence["plan"]["constraints"]]
    assert any("5:00 PM" in fact for fact in facts)
    assert any("Downtown" in fact for fact in facts)
    assert any("Italian" in fact for fact in facts)
    assert any("6:00 PM" in fact for fact in facts)
    for source, target in [("DESKTOP", "WEARABLE"), ("WEARABLE", "MOBILE")]:
        moved = client.post(
            f"/api/v1/tasks/{task['id']}/handoff",
            json={
                "source_device_id": devices[source],
                "target_device_id": devices[target],
                "idempotency_key": f"move-{target}",
            },
        )
        assert moved.status_code == 200 and moved.json()["task"]["id"] == task["id"]
        assert client.get(f"/api/v1/tasks/{task['id']}/plan").json() == intelligence
    assert (
        client.get(f"/api/v1/tasks/{task['id']}/agent-runs/{runs[2]['id']}").json()["agent_name"]
        == "CALENDAR"
    )
    assert client.get(f"/api/v1/tasks/{uuid4()}/agent-runs/{runs[2]['id']}").status_code == 404
    with SessionLocal() as session:
        assert session.scalar(select(func.count()).select_from(AgentExecution)) == 1
        assert session.scalar(select(func.count()).select_from(AgentRun)) == 6
        assert session.scalar(select(func.count()).select_from(ToolCall)) == 5


def test_exact_execution_retry_does_not_duplicate_agents(client, task):
    first = run_api(client, task["id"]).json()
    replay = run_api(client, task["id"])
    assert replay.status_code == 200 and replay.json()["replayed"]
    assert replay.json()["execution"]["id"] == first["execution"]["id"]
    assert len(client.get(f"/api/v1/tasks/{task['id']}/agent-runs").json()) == 6


def test_task_requirements_skip_unneeded_specialists(client, devices):
    task = client.post(
        "/api/v1/tasks",
        json={"title": "Prepare a checklist", "origin_device_id": devices["DESKTOP"]},
    ).json()
    result = run_api(client, task["id"]).json()
    assert result["execution"]["status"] == "DONE"
    runs = client.get(f"/api/v1/tasks/{task['id']}/agent-runs").json()
    assert [run["status"] for run in runs] == [
        "DONE",
        "DONE",
        "SKIPPED",
        "SKIPPED",
        "SKIPPED",
        "DONE",
    ]
    assert sum(len(run["tool_calls"]) for run in runs) == 1


def test_failed_specialist_stops_dependents_and_records_tool_failure(client, task, monkeypatch):
    def fail_calendar(*args, **kwargs):
        raise RuntimeError("test failure")

    # Preserve SK's registered function metadata; fail the bounded fixture repository.
    monkeypatch.setattr(DemoFixtureRepository, "calendar", fail_calendar)
    response = run_api(client, task["id"])
    assert response.json()["execution"]["status"] == "FAILED"
    state = client.get(f"/api/v1/tasks/{task['id']}/plan").json()
    assert state["plan"] is None
    calendar = next(run for run in state["agent_runs"] if run["stage"] == "calendar")
    assert calendar["status"] == "FAILED" and calendar["tool_calls"][0]["status"] == "FAILED"
    assert all(
        run["status"] == "SKIPPED"
        for run in state["agent_runs"]
        if run["stage"] in {"planner_revision", "critic"}
    )


def test_malformed_provider_output_is_recorded_and_not_used(client, task, monkeypatch):
    class MalformedProvider(FixtureModelProvider):
        async def generate_structured(self, agent, payload):
            return ProviderResponse(payload_json='{"kind":"context","arbitrary_shell":"exec"}')

    monkeypatch.setattr("app.intelligence.orchestrator.provider_factory", MalformedProvider)
    result = run_api(client, task["id"]).json()
    assert result["execution"]["status"] == "FAILED"
    state = client.get(f"/api/v1/tasks/{task['id']}/plan").json()
    assert state["agent_runs"][0]["error"] == "AGENT_OUTPUT_INVALID"
    assert state["plan"] is None


def test_critic_feedback_is_revised_only_by_planner(client, task, monkeypatch):
    class NeedsCorrection(FixtureModelProvider):
        async def generate_structured(self, agent, payload):
            response = await super().generate_structured(agent, payload)
            if agent == "PLANNER" and payload.revision == 1:
                output = PlanOutput.model_validate_json(response.payload_json)
                output.plan.assumptions.append("Unsupported booking assumption.")
                return ProviderResponse(payload_json=output.model_dump_json())
            return response

    monkeypatch.setattr("app.intelligence.orchestrator.provider_factory", NeedsCorrection)
    assert run_api(client, task["id"]).json()["execution"]["status"] == "DONE"
    runs = client.get(f"/api/v1/tasks/{task['id']}/agent-runs").json()
    assert len(runs) == 8
    assert runs[5]["structured_output"]["verdict"] == "REVISION_REQUIRED"
    assert (
        runs[6]["stage"] == "planner_correction" and runs[6]["structured_output"]["revision"] == 2
    )
    assert runs[7]["structured_output"]["verdict"] == "PASS"


def test_running_execution_duplicates_refresh_and_handoff(client, task, devices, monkeypatch):
    entered, release = Event(), Event()

    class GatedProvider(FixtureModelProvider):
        async def generate_structured(self, agent, payload):
            if agent == "CONTEXT":
                entered.set()
                if not release.wait(8):
                    raise RuntimeError("Gate was not released.")
            return await super().generate_structured(agent, payload)

    monkeypatch.setattr("app.intelligence.orchestrator.provider_factory", GatedProvider)
    with ThreadPoolExecutor(max_workers=1) as executor:
        pending = executor.submit(run_api, client, task["id"], "running-key")
        try:
            assert entered.wait(5)
            active = client.get(f"/api/v1/tasks/{task['id']}/plan").json()
            assert active["execution"]["status"] == "RUNNING"
            assert active["agent_runs"][0]["status"] == "RUNNING"
            same = run_api(client, task["id"], "running-key")
            assert same.status_code == 200 and same.json()["replayed"]
            assert run_api(client, task["id"], "different-key").status_code == 409
            moved = client.post(
                f"/api/v1/tasks/{task['id']}/handoff",
                json={
                    "source_device_id": devices["DESKTOP"],
                    "target_device_id": devices["WEARABLE"],
                    "idempotency_key": "handoff-during-execution",
                },
            )
            assert moved.status_code == 200
        finally:
            release.set()
        assert pending.result(timeout=5).json()["execution"]["status"] == "DONE"
    assert (
        client.get(f"/api/v1/tasks/{task['id']}").json()["current_device_id"] == devices["WEARABLE"]
    )
    assert len(client.get(f"/api/v1/tasks/{task['id']}/agent-runs").json()) == 6


def test_interrupted_execution_recovery_never_claims_success(client, task):
    trace = uuid4()
    with SessionLocal.begin() as session:
        session.add(
            AgentExecution(
                id=trace,
                trace_id=trace,
                task_id=task["id"],
                status="RUNNING",
                provider="FixtureModelProvider",
                model="nova-demo-v1",
                idempotency_key="abandoned",
            )
        )
    recover_interrupted_executions()
    state = client.get(f"/api/v1/tasks/{task['id']}/plan").json()
    assert (
        state["execution"]["status"] == "FAILED"
        and state["execution"]["error"] == "APPLICATION_RESTARTED"
    )
    assert state["plan"] is None


def test_intelligence_api_validation_and_empty_state(client, task):
    assert client.get(f"/api/v1/tasks/{task['id']}/plan").json()["execution"] is None
    assert client.post(f"/api/v1/tasks/{task['id']}/run-agents", json={}).status_code == 422
    assert (
        client.post(
            f"/api/v1/tasks/{task['id']}/run-agents",
            json={"idempotency_key": "x", "provider": "paid"},
        ).status_code
        == 422
    )
    assert run_api(client, str(uuid4())).status_code == 404


def test_forged_provider_pass_cannot_bypass_provenance_and_privacy_policy(
    client, task, monkeypatch
):
    class ForgedPassProvider(FixtureModelProvider):
        async def generate_structured(self, agent, payload):
            if agent == "CRITIC":
                return ProviderResponse(
                    payload_json=CriticOutput(verdict="PASS", reasons=[]).model_dump_json()
                )
            response = await super().generate_structured(agent, payload)
            if agent == "PLANNER":
                output = PlanOutput.model_validate_json(response.payload_json)
                output.plan.requires_approval = False
                if output.plan.constraints:
                    output.plan.constraints[0].provenance.reference = "fabricated.provenance"
                return ProviderResponse(payload_json=output.model_dump_json())
            return response

    monkeypatch.setattr("app.intelligence.orchestrator.provider_factory", ForgedPassProvider)
    result = run_api(client, task["id"]).json()
    assert result["execution"]["status"] == "FAILED"
    assert result["execution"]["error"] == "CRITIC_REJECTED"
    state = client.get(f"/api/v1/tasks/{task['id']}/plan").json()
    assert state["plan"] is None and state["critic"]["verdict"] == "REVISION_REQUIRED"
    assert any(reason["code"] == "PRIVACY" for reason in state["critic"]["reasons"])
    assert any(reason["code"] == "UNSUPPORTED_ASSUMPTION" for reason in state["critic"]["reasons"])
    assert len(state["agent_runs"]) == 8  # Bounded correction, never an endless revision loop.


def test_execution_logs_propagate_trace_and_request_correlation(client, task, monkeypatch):
    events = []
    monkeypatch.setattr(
        "app.intelligence.orchestrator.logger.info",
        lambda message, extra=None, **kwargs: events.append((message, extra)),
    )
    response = client.post(
        f"/api/v1/tasks/{task['id']}/run-agents",
        json={"idempotency_key": "trace-propagation"},
        headers={"X-Correlation-ID": "phase2-correlation"},
    )
    trace = response.json()["execution"]["trace_id"]
    assert events and all(extra["trace_id"] == trace for _, extra in events)
    start = next(extra for message, extra in events if message == "execution_started")
    assert start["correlation_id"] == "phase2-correlation"
    assert response.headers["X-Correlation-ID"] == "phase2-correlation"


def test_fixture_orchestration_never_constructs_paid_client_or_external_async_request(
    client, task, monkeypatch
):
    import aiohttp
    import httpx
    import openai
    from azure import identity

    def forbidden(*args, **kwargs):
        raise AssertionError("External model/network/credential access is forbidden.")

    monkeypatch.setattr(openai, "OpenAI", forbidden)
    monkeypatch.setattr(openai, "AsyncOpenAI", forbidden)
    monkeypatch.setattr(identity, "DefaultAzureCredential", forbidden)
    monkeypatch.setattr(aiohttp.ClientSession, "_request", forbidden)
    monkeypatch.setattr(httpx.AsyncClient, "request", forbidden)
    assert run_api(client, task["id"]).json()["execution"]["status"] == "DONE"
