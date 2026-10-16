import hashlib
import json
import logging
import os
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select

from app.database import SessionLocal, _evaluation_schema
from app.evaluation.contracts import EvaluationDataset, JudgeRequest, RunInput
from app.evaluation.flows import FLOWS
from app.evaluation.graders import gates, grade, metrics
from app.evaluation.isolation import reset_scenario, scenario_database
from app.evaluation.judge import FixtureJudge
from app.evaluation.models import (
    Dataset,
    EvaluationRun,
    ExperimentResult,
    ScenarioResult,
)
from app.memory.service import digest
from app.models import User
from app.security.identity import current_user_id
from app.service import fail

logger = logging.getLogger("nova.evaluation")

DISCLOSURE = "LOCAL FIXTURE SYSTEM / NOT PRODUCTION RELIABILITY; NOT REAL CV OR SEMANTIC QUALITY"
SHADOW_EXCLUDED = {
    "changed_payload",
    "approve_only",
    "simulation",
    "execute_retry",
    "edit_approved",
}


def load_dataset():
    raw = Path(__file__).with_name("datasets").joinpath("nova-golden-v1.json").read_bytes()
    dataset = EvaluationDataset.model_validate_json(raw)
    return dataset, hashlib.sha256(raw).hexdigest()


def selected(dataset, suite, shadow=False):
    rows = [s for s in dataset.scenarios if suite == "FULL" or suite.lower() in s.tags]
    if shadow:
        rows = [
            s
            for s in rows
            if not (s.operation == "proactive" and s.input["case"] in SHADOW_EXCLUDED)
        ]
    return rows


@contextmanager
def public_store():
    token = _evaluation_schema.set(None)
    try:
        with SessionLocal.begin() as session:
            yield session
    finally:
        _evaluation_schema.reset(token)


def source_fingerprint():
    root = Path(__file__).parents[1]
    return digest(
        {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*.py"))
        }
    )


class EvaluationRunner:
    def __init__(self, user_id=None, experiment_result_id=None):
        self.user_id = user_id or current_user_id()
        self.experiment_result_id = experiment_result_id

    def claim(self, payload: RunInput, shadow=False):
        dataset, checksum = load_dataset()
        hashed = digest([payload.model_dump(exclude={"idempotency_key"}), shadow])
        with public_store() as s:
            if not s.scalar(select(User.id).where(User.id == self.user_id).with_for_update()):
                fail(404, "USER_NOT_FOUND", "Evaluation owner not found")
            prior = s.scalar(
                select(EvaluationRun).where(
                    EvaluationRun.user_id == self.user_id,
                    EvaluationRun.idempotency_key == payload.idempotency_key,
                )
            )
            if prior:
                if prior.input_hash != hashed:
                    fail(
                        409,
                        "IDEMPOTENCY_CONFLICT",
                        "Evaluation key belongs to another configuration",
                    )
                return prior.id, True
            active_experiment = s.scalar(
                select(ExperimentResult.id).where(
                    ExperimentResult.user_id == self.user_id, ExperimentResult.status == "RUNNING"
                )
            )
            if active_experiment and active_experiment != self.experiment_result_id:
                fail(409, "EXPERIMENT_RUNNING", "An experiment owns the evaluation slot")
            if s.scalar(
                select(EvaluationRun.id).where(
                    EvaluationRun.user_id == self.user_id, EvaluationRun.status == "RUNNING"
                )
            ):
                fail(409, "EVALUATION_RUNNING", "One local evaluation may run per owner")
            stored = s.scalar(
                select(Dataset).where(
                    Dataset.name == dataset.name, Dataset.version == dataset.version
                )
            )
            if stored and stored.digest != checksum:
                fail(
                    409,
                    "DATASET_VERSION_CONFLICT",
                    "Changed dataset content requires a new version",
                )
            if not stored:
                stored = Dataset(
                    name=dataset.name,
                    version=dataset.version,
                    digest=checksum,
                    scenario_versions={r.scenario_id: r.version for r in dataset.scenarios},
                )
                s.add(stored)
                s.flush()
            reproducibility = {
                "dataset": dataset.name,
                "dataset_version": dataset.version,
                "dataset_digest": checksum,
                "fixture_version": dataset.fixture_version,
                "source_fingerprint": source_fingerprint(),
                "code_checkpoint": os.environ.get("EVALUATION_CODE_CHECKPOINT"),
                "provider_mode": "FIXTURE_ONLY",
                "seed": 0,
                "grader_version": "checks-v2",
                "gate_version": "gates-v1",
                "shadow_simulation": shadow,
                "judge": "FIXTURE" if payload.fixture_judge else "DISABLED",
                "real_judge": "REAL LLM JUDGE NOT CONFIGURED",
                "disclosure": DISCLOSURE,
                "scenario_count": len(selected(dataset, payload.suite, shadow)),
            }
            row = EvaluationRun(
                user_id=self.user_id,
                dataset_id=stored.id,
                idempotency_key=payload.idempotency_key,
                input_hash=hashed,
                suite=payload.suite,
                configuration=payload.configuration,
                configuration_fingerprint=digest(
                    [payload.model_dump(exclude={"idempotency_key"}), reproducibility]
                ),
                reproducibility=reproducibility,
                status="RUNNING",
            )
            s.add(row)
            s.flush()
            return row.id, False

    def execute(self, run_id, fault=None):
        # fault is an internal callable used only by Python tests, never an API field.
        with public_store() as s:
            row = self.owned(s, run_id)
            if row.status != "RUNNING":
                return
            mode = row.configuration
            suite = row.suite
            shadow = row.reproducibility["shadow_simulation"]
            use_judge = row.reproducibility["judge"] == "FIXTURE"
        dataset, checksum = load_dataset()
        if checksum != row.reproducibility["dataset_digest"]:
            self.fail(run_id, "DATASET_CHANGED_AFTER_CLAIM")
            return
        try:
            with scenario_database(run_id) as schema:
                for scenario in selected(dataset, suite, shadow):
                    start = time.perf_counter()
                    try:
                        reset_scenario(schema)
                        from app.database import _evaluation_shadow

                        shadow_token = _evaluation_shadow.set(shadow)
                        try:
                            observation = FLOWS[scenario.operation](scenario.input["case"], mode)
                        finally:
                            _evaluation_shadow.reset(shadow_token)
                        from app.proactive.models import ActionExecution

                        with SessionLocal() as state:
                            executions = list(state.scalars(select(ActionExecution)))
                        from app.model_routing.models import ModelCall

                        with SessionLocal() as state:
                            calls = list(state.scalars(select(ModelCall)))
                        observation["scenario_input"] = scenario.input
                        observation["accounting"] = [
                            {
                                "estimated_cost_usd": c.response_metadata.get("estimated_cost_usd"),
                                "cost_status": c.response_metadata.get("cost_status"),
                                "trace_id": str(c.trace_id),
                                "usage_source": c.response_metadata.get("usage_source"),
                            }
                            for c in calls
                        ]
                        observation["external_message_sent"] = any(
                            bool(e.receipt.get("external_message_sent")) for e in executions
                        )
                        observation["action_executions"] = len(executions)
                        if fault:
                            observation = fault(scenario, observation)
                        graders = [
                            grade(c, observation).model_dump(mode="json") for c in scenario.checks
                        ]
                        status = "PASS" if all(g["passed"] for g in graders) else "FAIL"
                    except Exception as error:
                        code = "SCENARIO_EXECUTION_FAILED_" + type(error).__name__[:40]
                        logger.error(code, extra={"trace_id": str(run_id)})
                        observation = {"safe_error": code}
                        graders = [
                            grade(c, observation).model_dump(mode="json") for c in scenario.checks
                        ]
                        status = "ERROR"
                    result = ScenarioResult(
                        run_id=run_id,
                        scenario_id=scenario.scenario_id,
                        scenario_version=scenario.version,
                        category=scenario.category,
                        status=status,
                        elapsed_ms=round((time.perf_counter() - start) * 1000, 3),
                        observation=observation,
                        graders=graders,
                        judge=FixtureJudge()
                        .review(JudgeRequest(content="Persisted fixture scenario result"))
                        .model_dump(mode="json")
                        if use_judge
                        else None,
                    )
                    if len(json.dumps(observation)) > 32000:
                        raise ValueError("Observation bound exceeded")
                    with public_store() as s:
                        s.add(result)
                reset_scenario(schema)  # removes only this scope's generated media before DROP
            with public_store() as s:
                results = list(
                    s.scalars(
                        select(ScenarioResult)
                        .where(ScenarioResult.run_id == run_id)
                        .order_by(ScenarioResult.scenario_id)
                    )
                )
                row = self.owned(s, run_id)
                row.metrics = metrics(results)
                row.gates = gates(results, row.metrics)
                row.summary = {
                    "evaluated": len(results),
                    "passed": sum(r.status == "PASS" for r in results),
                    "failed": sum(r.status != "PASS" for r in results),
                    "critical_violations": sum(
                        not g["passed"] and g["severity"] == "CRITICAL"
                        for r in results
                        for g in r.graders
                    ),
                    "gate_status": "FAIL"
                    if any(g["status"] == "FAIL" for g in row.gates)
                    else "PASS",
                }
                row.status = "DONE"
                row.completed_at = datetime.now(UTC)
        except Exception as error:
            code = "EVALUATION_FAILED_" + type(error).__name__[:40]
            logger.error(code, extra={"trace_id": str(run_id)})
            self.fail(run_id, code)

    def fail(self, run_id, code):
        with public_store() as s:
            row = self.owned(s, run_id)
            row.status = "FAILED"
            row.safe_error = code
            row.completed_at = datetime.now(UTC)

    def owned(self, s, id):
        row = s.scalar(
            select(EvaluationRun).where(
                EvaluationRun.id == id, EvaluationRun.user_id == self.user_id
            )
        )
        if not row:
            fail(404, "EVALUATION_NOT_FOUND", "Evaluation run not found")
        return row

    def read(self, id, scenarios=True):
        with public_store() as s:
            row = self.owned(s, id)
            results = (
                list(
                    s.scalars(
                        select(ScenarioResult)
                        .where(ScenarioResult.run_id == id)
                        .order_by(ScenarioResult.scenario_id)
                    )
                )
                if scenarios
                else []
            )
            return {
                "id": str(row.id),
                "status": row.status,
                "suite": row.suite,
                "configuration": row.configuration,
                "configuration_fingerprint": row.configuration_fingerprint,
                "reproducibility": row.reproducibility,
                "summary": row.summary,
                "metrics": row.metrics,
                "gates": row.gates,
                "started_at": row.started_at.isoformat(),
                "completed_at": row.completed_at.isoformat() if row.completed_at else None,
                "safe_error": row.safe_error,
                "scenarios": [
                    {
                        "scenario_id": r.scenario_id,
                        "version": r.scenario_version,
                        "category": r.category,
                        "status": r.status,
                        "elapsed_ms": r.elapsed_ms,
                        "observation": r.observation,
                        "graders": r.graders,
                        "judge": r.judge,
                    }
                    for r in results
                ],
            }

    def run(self, payload, shadow=False):
        id, replayed = self.claim(payload, shadow)
        if not replayed:
            self.execute(id)
        return self.read(id)


def recover_evaluations():
    interrupted = []
    with public_store() as s:
        for row in s.scalars(select(EvaluationRun).where(EvaluationRun.status == "RUNNING")):
            row.status = "FAILED"
            interrupted.append(row.id)
            row.safe_error = "APPLICATION_RESTARTED"
            row.completed_at = datetime.now(UTC)

    from app.evaluation.isolation import cleanup_interrupted_schema

    for run_id in interrupted:
        cleanup_interrupted_schema(run_id)


def recover_experiments():
    with public_store() as session:
        for row in session.scalars(
            select(ExperimentResult).where(ExperimentResult.status == "RUNNING")
        ):
            row.status = "FAILED"
