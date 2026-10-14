import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import ValidationError
from sqlalchemy import select

from app.database import SessionLocal
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
    AgentRunRead,
    CalendarOutput,
    ContextOutput,
    CriticOutput,
    ExecutionRead,
    ExecutionResponse,
    IntelligenceRead,
    MemoryOutput,
    Plan,
    PlanOutput,
    PriorResult,
    SharedContext,
)
from app.intelligence.models import AgentExecution, AgentRun, ToolCall
from app.intelligence.plugins import KernelRuntime, ToolRecord
from app.intelligence.provider import FixtureModelProvider, ModelProvider
from app.models import Device
from app.service import fail, find_task

logger = logging.getLogger("nova.intelligence")
STAGES = [
    ("CONTEXT", "context"),
    ("PLANNER", "planner"),
    ("CALENDAR", "calendar"),
    ("MEMORY", "memory"),
    ("PLANNER", "planner_revision"),
    ("CRITIC", "critic"),
]


def provider_factory() -> ModelProvider:
    # Explicit zero-cost policy: only this deterministic service is configured.
    return FixtureModelProvider()


def record_tool(record: ToolRecord) -> None:
    with SessionLocal.begin() as session:
        session.add(ToolCall(**record.model_dump()))
    logger.info("tool_complete", extra={"trace_id": str(record.trace_id)})


class AgentOrchestrator:
    def __init__(self, provider: ModelProvider | None = None, visual_context=None):
        self.visual_context = [v.model_dump(mode="json") for v in (visual_context or [])]
        self.runtime = KernelRuntime(provider or provider_factory(), record_tool)
        self.agents = {
            agent.name: agent
            for agent in [
                ContextAgent(),
                PlannerAgent(),
                CalendarAgent(),
                MemoryAgent(),
                CriticAgent(),
            ]
        }

    def run(self, task_id: UUID, key: str, correlation_id: str) -> ExecutionResponse:
        with SessionLocal.begin() as session:
            task = find_task(session, task_id, lock=True)
            existing = session.scalar(
                select(AgentExecution).where(
                    AgentExecution.task_id == task_id, AgentExecution.idempotency_key == key
                )
            )
            if existing:
                return ExecutionResponse(
                    execution=ExecutionRead.model_validate(existing), replayed=True
                )
            active = session.scalar(
                select(AgentExecution.id).where(
                    AgentExecution.task_id == task_id, AgentExecution.status == "RUNNING"
                )
            )
            if active:
                fail(409, "EXECUTION_IN_PROGRESS", "An execution is already running for this task.")
            trace_id = uuid4()
            provider = self.runtime.provider
            execution = AgentExecution(
                id=trace_id,
                trace_id=trace_id,
                task_id=task.id,
                status="RUNNING",
                provider=provider.provider_name,
                model=provider.model_name,
                idempotency_key=key,
            )
            session.add(execution)
            session.flush()
            runs = {}
            for sequence, (agent, stage) in enumerate(STAGES, 1):
                run = AgentRun(
                    task_id=task.id,
                    execution_id=trace_id,
                    trace_id=trace_id,
                    agent_name=agent,
                    stage=stage,
                    sequence=sequence,
                    status="WAITING",
                    provider=provider.provider_name,
                    model=provider.model_name,
                )
                session.add(run)
                session.flush()
                runs[stage] = run.id
            device = session.get(Device, task.current_device_id)
            payload = AgentInput(
                task_id=task.id,
                user_id=task.user_id,
                current_device=device.type,
                task_goal=task.title,
                available_context=SharedContext(visual_evidence=self.visual_context),
                trace_id=trace_id,
            )
        # The task lock is released before any agent/plugin/provider execution.
        logger.info(
            "execution_started",
            extra={
                "trace_id": str(trace_id),
                "task_id": str(task_id),
                "correlation_id": correlation_id,
            },
        )
        try:
            asyncio.run(self._execute(payload, runs))
        except Exception:
            self._fail_execution(trace_id, "ORCHESTRATION_FAILED")
        with SessionLocal() as session:
            stored = session.get(AgentExecution, trace_id)
            return ExecutionResponse(execution=ExecutionRead.model_validate(stored), replayed=False)

    async def _stage(self, run_id: UUID, payload: AgentInput) -> AgentResult:
        with SessionLocal.begin() as session:
            run = session.get(AgentRun, run_id)
            run.status = "RUNNING"
            run.started_at = datetime.now(UTC)
            name = run.agent_name
        logger.info("agent_started", extra={"trace_id": str(payload.trace_id), "agent_name": name})
        try:
            result = await self.agents[name].execute(payload, self.runtime, run_id)
            result = AgentResult.model_validate(result.model_dump(mode="json"))
            if result.agent_name != name:
                raise ValueError("Agent result does not match its contract.")
            with SessionLocal.begin() as session:
                run = session.get(AgentRun, run_id)
                run.status = "DONE"
                run.summary = result.summary
                run.started_at = result.started_at
                run.completed_at = result.completed_at
                run.structured_output = result.structured_output.model_dump(mode="json")
                run.evidence = [item.model_dump(mode="json") for item in result.evidence]
                run.warnings = result.warnings
            logger.info(
                "agent_complete", extra={"trace_id": str(payload.trace_id), "agent_name": name}
            )
            return result
        except Exception as error:
            code = (
                "AGENT_OUTPUT_INVALID"
                if isinstance(error, ValidationError)
                else "AGENT_EXECUTION_FAILED"
            )
            with SessionLocal.begin() as session:
                run = session.get(AgentRun, run_id)
                run.status = "FAILED"
                run.completed_at = datetime.now(UTC)
                run.error = code
                run.summary = "Agent failed; dependent execution is stopped."
            logger.error(
                "agent_failed", extra={"trace_id": str(payload.trace_id), "agent_name": name}
            )
            raise

    def _skip(self, run_id: UUID, reason: str):
        with SessionLocal.begin() as session:
            run = session.get(AgentRun, run_id)
            run.status = "SKIPPED"
            run.completed_at = datetime.now(UTC)
            run.summary = reason

    def _fail_execution(self, trace_id: UUID, code: str):
        with SessionLocal.begin() as session:
            execution = session.get(AgentExecution, trace_id)
            execution.status = "FAILED"
            execution.error = code
            execution.completed_at = datetime.now(UTC)
            for run in session.scalars(
                select(AgentRun).where(
                    AgentRun.execution_id == trace_id, AgentRun.status.in_(["WAITING", "RUNNING"])
                )
            ):
                run.status = "SKIPPED" if run.status == "WAITING" else "FAILED"
                run.error = code
                run.completed_at = execution.completed_at
                run.summary = "Stopped after a critical failure; no result invented."
        logger.error("execution_failed", extra={"trace_id": str(trace_id)})

    def _remember(self, payload: AgentInput, result: AgentResult) -> AgentInput:
        context = payload.available_context.model_copy(deep=True)
        output = result.structured_output
        needs = payload.needs
        if isinstance(output, ContextOutput):
            context, needs = output.context, output.needs
        elif isinstance(output, CalendarOutput):
            context.calendar = output.events
        elif isinstance(output, MemoryOutput):
            context.preferences = output.preferences
        next_payload = AgentInput(
            **{
                **payload.model_dump(),
                "available_context": context,
                "needs": needs,
                "prior_results": [
                    *payload.prior_results,
                    PriorResult(agent_name=result.agent_name, structured_output=output),
                ],
            }
        )
        with SessionLocal.begin() as session:
            execution = session.get(AgentExecution, payload.trace_id)
            execution.context = context.model_dump(mode="json")
            if isinstance(output, CriticOutput):
                execution.critic = output.model_dump(mode="json")
        return next_payload

    def _correction_runs(self, trace_id: UUID) -> tuple[UUID, UUID]:
        with SessionLocal.begin() as session:
            execution = session.get(AgentExecution, trace_id)
            ids = []
            for sequence, (name, stage) in enumerate(
                [("PLANNER", "planner_correction"), ("CRITIC", "critic_recheck")], 7
            ):
                run = AgentRun(
                    task_id=execution.task_id,
                    execution_id=trace_id,
                    trace_id=trace_id,
                    agent_name=name,
                    stage=stage,
                    sequence=sequence,
                    status="WAITING",
                    provider=execution.provider,
                    model=execution.model,
                )
                session.add(run)
                session.flush()
                ids.append(run.id)
            return ids[0], ids[1]

    async def _execute(self, payload: AgentInput, runs: dict[str, UUID]):
        payload = self._remember(payload, await self._stage(runs["context"], payload))
        initial = await self._stage(runs["planner"], payload)
        payload = self._remember(payload, initial)
        required = {tool.plugin for tool in initial.structured_output.plan.required_tools}
        jobs = []
        for stage, needed in [
            ("calendar", payload.needs.calendar and "CalendarPlugin" in required),
            ("memory", payload.needs.preferences and "MemoryPlugin" in required),
        ]:
            if needed:
                jobs.append(self._stage(runs[stage], payload))
            else:
                self._skip(
                    runs[stage], "Not required by this task; no specialist or plugin was invoked."
                )
        results = await asyncio.gather(*jobs, return_exceptions=True)
        if any(isinstance(result, BaseException) for result in results):
            self._fail_execution(payload.trace_id, "SPECIALIST_FAILED")
            return
        for result in results:
            payload = self._remember(payload, result)
        if jobs:
            payload.revision = 1
            payload = self._remember(payload, await self._stage(runs["planner_revision"], payload))
        else:
            self._skip(runs["planner_revision"], "No specialist evidence required revision.")
        critic = await self._stage(runs["critic"], payload)
        payload = self._remember(payload, critic)
        if critic.structured_output.verdict == "REVISION_REQUIRED":
            planner_id, critic_id = self._correction_runs(payload.trace_id)
            payload.revision = 2
            payload = self._remember(payload, await self._stage(planner_id, payload))
            critic = await self._stage(critic_id, payload)
            payload = self._remember(payload, critic)
        if critic.structured_output.verdict != "PASS":
            self._fail_execution(payload.trace_id, "CRITIC_REJECTED")
            return
        plan = next(
            result.structured_output.plan
            for result in reversed(payload.prior_results)
            if isinstance(result.structured_output, PlanOutput)
        )
        with SessionLocal.begin() as session:
            execution = session.get(AgentExecution, payload.trace_id)
            execution.final_plan = plan.model_dump(mode="json")
            execution.status = "DONE"
            execution.completed_at = datetime.now(UTC)
        logger.info(
            "execution_complete",
            extra={"trace_id": str(payload.trace_id), "task_id": str(payload.task_id)},
        )


def read_runs(session, task_id: UUID, execution_id: UUID | None = None) -> list[AgentRunRead]:
    find_task(session, task_id)
    query = select(AgentRun).where(AgentRun.task_id == task_id)
    if execution_id:
        query = query.where(AgentRun.execution_id == execution_id)
    return [
        AgentRunRead.model_validate(run)
        for run in session.scalars(query.order_by(AgentRun.execution_id, AgentRun.sequence))
    ]


def read_intelligence(session, task_id: UUID) -> IntelligenceRead:
    find_task(session, task_id)
    execution = session.scalar(
        select(AgentExecution)
        .where(AgentExecution.task_id == task_id)
        .order_by(AgentExecution.started_at.desc(), AgentExecution.id.desc())
        .limit(1)
    )
    if execution is None:
        return IntelligenceRead(
            task_id=task_id, execution=None, agent_runs=[], context=None, plan=None, critic=None
        )
    return IntelligenceRead(
        task_id=task_id,
        execution=ExecutionRead.model_validate(execution),
        agent_runs=read_runs(session, task_id, execution.id),
        context=SharedContext.model_validate(execution.context) if execution.context else None,
        plan=Plan.model_validate(execution.final_plan) if execution.final_plan else None,
        critic=CriticOutput.model_validate(execution.critic) if execution.critic else None,
    )


def recover_interrupted_executions():
    """Single-process local startup: terminate abandoned workflows, never invent completion."""
    with SessionLocal() as session:
        ids = session.scalars(
            select(AgentExecution.id).where(AgentExecution.status == "RUNNING")
        ).all()
    # Recovery does not need a provider or kernel.
    service = object.__new__(AgentOrchestrator)
    for trace_id in ids:
        service._fail_execution(trace_id, "APPLICATION_RESTARTED")
