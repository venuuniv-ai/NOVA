import hashlib
from uuid import UUID

from sqlalchemy import select

from app.evaluation.contracts import ExperimentAssignment, RunInput
from app.evaluation.models import Assignment, Experiment, ExperimentResult
from app.evaluation.runner import EvaluationRunner, load_dataset, public_store, selected
from app.memory.service import digest
from app.models import User
from app.security.identity import current_user_id
from app.service import fail


def assignment(experiment_id, subject, percentage):
    bucket = (
        int.from_bytes(hashlib.sha256(f"{experiment_id}:{subject}".encode()).digest()[:8], "big")
        % 10000
    )
    return ExperimentAssignment(
        subject=subject,
        bucket=bucket,
        variant="CANDIDATE" if bucket < percentage * 100 else "BASELINE",
    )


def compare(baseline, candidate):
    if baseline["status"] != "DONE" or candidate["status"] != "DONE":
        fail(409, "INCOMPLETE_COMPARISON", "Both runs must be complete")
    if (
        baseline["reproducibility"]["dataset_digest"]
        != candidate["reproducibility"]["dataset_digest"]
        or {s["scenario_id"] for s in baseline["scenarios"]}
        != {s["scenario_id"] for s in candidate["scenarios"]}
        or baseline["reproducibility"]["source_fingerprint"]
        != candidate["reproducibility"]["source_fingerprint"]
    ):
        fail(409, "INCOMPARABLE_RUNS", "Dataset, source and executed scenarios must match")
    a = {m["name"]: m for m in baseline["metrics"]}
    b = {m["name"]: m for m in candidate["metrics"]}
    deltas = [
        {
            "metric": key,
            "baseline": a[key]["value"],
            "candidate": b[key]["value"],
            "delta": b[key]["value"] - a[key]["value"]
            if a[key]["value"] is not None and b[key]["value"] is not None
            else None,
            "baseline_denominator": a[key]["denominator"],
            "candidate_denominator": b[key]["denominator"],
        }
        for key in a
    ]
    drop = b["task_success"]["value"] - a["task_success"]["value"]
    return {
        "deltas": deltas,
        "task_success_regression_gate": "PASS" if drop >= -0.02 else "FAIL",
        "tolerance": 0.02,
        "critical_violations": candidate["summary"]["critical_violations"],
        "gate_status": "FAIL"
        if drop < -0.02 or candidate["summary"]["gate_status"] == "FAIL"
        else "PASS",
        "statistics": "INSUFFICIENT SAMPLE SIZE / NO STATISTICAL SIGNIFICANCE CLAIM",
        "methodology": "Paired fixtures; thresholds 10 vs 2; latency includes setup",
    }


class Experiments:
    def __init__(self, user_id=None):
        self.user_id = user_id or current_user_id()
        self.runner = EvaluationRunner(user_id)

    def create(self, payload):
        hashed = digest(payload.model_dump(exclude={"idempotency_key"}))
        with public_store() as s:
            s.scalar(select(User.id).where(User.id == self.user_id).with_for_update())
            row = s.scalar(
                select(Experiment).where(
                    Experiment.user_id == self.user_id,
                    Experiment.idempotency_key == payload.idempotency_key,
                )
            )
            if row and row.input_hash != hashed:
                fail(409, "IDEMPOTENCY_CONFLICT", "Experiment key changed")
            if not row:
                row = Experiment(
                    user_id=self.user_id,
                    idempotency_key=payload.idempotency_key,
                    input_hash=hashed,
                    definition=payload.model_dump(mode="json"),
                )
                s.add(row)
                s.flush()
            return row.id

    def owned(self, s, id):
        row = s.scalar(
            select(Experiment).where(Experiment.id == id, Experiment.user_id == self.user_id)
        )
        if not row:
            fail(404, "EXPERIMENT_NOT_FOUND", "Experiment not found")
        return row

    def claim(self, id, key):
        with public_store() as s:
            self.owned(s, id)
            s.scalar(select(User.id).where(User.id == self.user_id).with_for_update())
            prior = s.scalar(
                select(ExperimentResult).where(
                    ExperimentResult.experiment_id == id, ExperimentResult.idempotency_key == key
                )
            )
            if prior:
                return prior.id, True
            if s.scalar(
                select(ExperimentResult.id).where(
                    ExperimentResult.experiment_id == id, ExperimentResult.status == "RUNNING"
                )
            ):
                fail(409, "EXPERIMENT_RUNNING", "Experiment already running")
            from app.evaluation.models import EvaluationRun

            if s.scalar(
                select(ExperimentResult.id).where(
                    ExperimentResult.user_id == self.user_id, ExperimentResult.status == "RUNNING"
                )
            ) or s.scalar(
                select(EvaluationRun.id).where(
                    EvaluationRun.user_id == self.user_id, EvaluationRun.status == "RUNNING"
                )
            ):
                fail(
                    409, "EVALUATION_BUSY", "Another evaluation or experiment owns this local slot"
                )
            result = ExperimentResult(user_id=self.user_id, experiment_id=id, idempotency_key=key)
            s.add(result)
            s.flush()
            return result.id, False

    def execute(self, id, result_id):
        before = public_state_fingerprint()
        try:
            with public_store() as s:
                definition = self.owned(s, id).definition
                for scenario in selected(
                    load_dataset()[0], definition["suite"], definition["mode"] == "SHADOW"
                ):
                    prior = s.scalar(
                        select(Assignment).where(
                            Assignment.experiment_id == id,
                            Assignment.subject == scenario.scenario_id,
                        )
                    )
                    if not prior:
                        s.add(
                            Assignment(
                                experiment_id=id,
                                **assignment(
                                    id, scenario.scenario_id, definition["candidate_percentage"]
                                ).model_dump(),
                            )
                        )
            runner = EvaluationRunner(self.user_id, result_id)
            baseline = runner.run(
                RunInput(idempotency_key=f"exp-{result_id}-baseline", suite=definition["suite"]),
                shadow=definition["mode"] == "SHADOW",
            )
            candidate = runner.run(
                RunInput(
                    idempotency_key=f"exp-{result_id}-candidate",
                    suite=definition["suite"],
                    configuration="CAUTIOUS_THRESHOLD",
                ),
                shadow=definition["mode"] == "SHADOW",
            )
            comparison = compare(baseline, candidate)
            with public_store() as s:
                assignments = list(
                    s.scalars(select(Assignment).where(Assignment.experiment_id == id))
                )
                by_id = {r["scenario_id"]: r for r in candidate["scenarios"]}
                ba = {r["scenario_id"]: r for r in baseline["scenarios"]}
                chosen = [
                    by_id[a.subject] if a.variant == "CANDIDATE" else ba[a.subject]
                    for a in assignments
                ]
                comparison.update(
                    mode=definition["mode"] + " SIMULATION",
                    allocation_method="PAIRED OFFLINE REPLAY / BUCKETS SELECT SIMULATED OUTCOMES",
                    assigned_candidates=sum(a.variant == "CANDIDATE" for a in assignments),
                    assignment_denominator=len(assignments),
                    assigned_task_success=sum(r["status"] == "PASS" for r in chosen) / len(chosen),
                    candidate_action_executions=sum(
                        r["observation"].get("action_executions", 0) for r in candidate["scenarios"]
                    ),
                    external_messages=sum(
                        r["observation"].get("external_message_sent", False) for r in chosen
                    ),
                    authoritative_user_state_modified=before != public_state_fingerprint(),
                )
                result = s.get(ExperimentResult, result_id)
                result.baseline_id = UUID(baseline["id"])
                result.candidate_id = UUID(candidate["id"])
                result.status = "DONE"
                result.comparison = comparison
        except Exception:
            with public_store() as s:
                s.get(ExperimentResult, result_id).status = "FAILED"

    def read(self, id):
        with public_store() as s:
            row = self.owned(s, id)
            return {
                "id": str(row.id),
                "definition": row.definition,
                "assignments": [
                    {"subject": a.subject, "bucket": a.bucket, "variant": a.variant}
                    for a in s.scalars(
                        select(Assignment)
                        .where(Assignment.experiment_id == id)
                        .order_by(Assignment.subject)
                    )
                ],
                "results": [
                    {
                        "id": str(r.id),
                        "status": r.status,
                        "baseline_id": str(r.baseline_id) if r.baseline_id else None,
                        "candidate_id": str(r.candidate_id) if r.candidate_id else None,
                        "comparison": r.comparison,
                    }
                    for r in s.scalars(
                        select(ExperimentResult)
                        .where(ExperimentResult.experiment_id == id)
                        .order_by(ExperimentResult.created_at.desc())
                    )
                ],
            }


def public_state_fingerprint():
    """Hash business state locally; never copy personal values into evaluation reports."""
    from app.models import Base

    rows = {}
    with public_store() as session:
        for table in Base.metadata.sorted_tables:
            if not table.name.startswith(("evaluation_", "experiment_")):
                rows[table.name] = sorted(
                    digest(dict(row)) for row in session.execute(select(table)).mappings()
                )
    return digest(rows)
