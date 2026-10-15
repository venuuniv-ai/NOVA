from uuid import UUID

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import PlainTextResponse
from sqlalchemy import select

from app.evaluation.contracts import (
    CompareInput,
    EvaluationRunRead,
    ExperimentDefinition,
    ExperimentRunInput,
    RunInput,
)
from app.evaluation.experiments import Experiments, compare
from app.evaluation.models import EvaluationRun, Experiment
from app.evaluation.reports import markdown_report
from app.evaluation.runner import EvaluationRunner, load_dataset, public_store, selected
from app.seed import DEMO_USER_ID

router = APIRouter(prefix="/api/v1", tags=["evaluation"])


@router.get("/evaluation/datasets")
def datasets():
    data, checksum = load_dataset()
    return [
        {
            "name": data.name,
            "version": data.version,
            "digest": checksum,
            "scenarios": len(data.scenarios),
            "categories": {
                c: sum(s.category == c for s in data.scenarios)
                for c in sorted({s.category for s in data.scenarios})
            },
            "suites": {
                suite: len(selected(data, suite)) for suite in ["SMOKE", "REGRESSION", "FULL"]
            },
            "disclosure": "FIXTURE SYSTEM EVALUATION / NOT PRODUCTION QUALITY",
        }
    ]


@router.post("/evaluation/runs", status_code=202)
def start(payload: RunInput, background: BackgroundTasks):
    runner = EvaluationRunner()
    id, replayed = runner.claim(payload)
    if not replayed:
        background.add_task(runner.execute, id)
    return {"id": str(id), "replayed": replayed}


@router.get("/evaluation/runs")
def runs():
    runner = EvaluationRunner()
    with public_store() as s:
        ids = list(
            s.scalars(
                select(EvaluationRun.id)
                .where(EvaluationRun.user_id == DEMO_USER_ID)
                .order_by(EvaluationRun.started_at.desc())
                .limit(100)
            )
        )
    return [runner.read(id, scenarios=False) for id in ids]


@router.get("/evaluation/runs/{id}", response_model=EvaluationRunRead)
def read(id: UUID):
    return EvaluationRunner().read(id)


@router.get("/evaluation/runs/{id}/scenarios")
def scenarios(id: UUID):
    return EvaluationRunner().read(id)["scenarios"]


@router.get("/evaluation/runs/{id}/metrics")
def metrics(id: UUID):
    return EvaluationRunner().read(id, False)["metrics"]


@router.get("/evaluation/runs/{id}/report.md", response_class=PlainTextResponse)
def markdown(id: UUID):
    return markdown_report(EvaluationRunner().read(id))


@router.get("/evaluation/runs/{id}/report.json", response_model=EvaluationRunRead)
def report(id: UUID):
    return EvaluationRunner().read(id)


@router.post("/evaluation/compare")
def comparison(payload: CompareInput):
    runner = EvaluationRunner()
    return compare(runner.read(payload.baseline_id), runner.read(payload.candidate_id))


@router.post("/experiments", status_code=201)
def create(payload: ExperimentDefinition):
    return Experiments().read(Experiments().create(payload))


@router.get("/experiments")
def experiments():
    with public_store() as s:
        ids = list(
            s.scalars(
                select(Experiment.id)
                .where(Experiment.user_id == DEMO_USER_ID)
                .order_by(Experiment.created_at.desc())
                .limit(100)
            )
        )
    return [Experiments().read(id) for id in ids]


@router.get("/experiments/{id}")
def experiment(id: UUID):
    return Experiments().read(id)


@router.post("/experiments/{id}/run", status_code=202)
def run_experiment(id: UUID, payload: ExperimentRunInput, background: BackgroundTasks):
    service = Experiments()
    result, replayed = service.claim(id, payload.idempotency_key)
    if not replayed:
        background.add_task(service.execute, id, result)
    return {"id": str(result), "experiment_id": str(id), "replayed": replayed}
