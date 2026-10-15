import math
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
Key = Annotated[str, StringConstraints(pattern=r"^[a-zA-Z0-9_.:-]{1,128}$")]
Scalar = bool | int | Annotated[float, Field(allow_inf_nan=False)] | Text | None
Severity = Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
Suite = Literal["SMOKE", "REGRESSION", "FULL"]
Configuration = Literal["BASELINE", "CAUTIOUS_THRESHOLD"]
Category = Literal[
    "CONTINUITY", "AGENTS", "PROACTIVE", "ROUTING", "PERCEPTION", "MEMORY", "END_TO_END"
]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", revalidate_instances="always", allow_inf_nan=False)


class Check(Contract):
    name: Key
    field: Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_.]{0,80}$")]
    operation: Literal["EQ", "NE", "CONTAINS", "EXCLUDES", "SET", "LTE"] = "EQ"
    expected: Scalar | Annotated[list[Scalar], Field(max_length=30)]
    grader: Literal[
        "EXACT_MATCH", "SET_MATCH", "TRACE_MATCH", "POLICY", "RULE_BASED", "DETERMINISTIC"
    ]
    severity: Severity = "HIGH"
    metric: Key = "task_success"

    @model_validator(mode="after")
    def safe_path(self):
        if "__" in self.field or len(self.field.split(".")) > 4:
            raise ValueError("Unsupported observation path")
        return self


class EvaluationScenario(Contract):
    scenario_id: Key
    version: Literal[1]
    category: Category
    description: Text
    operation: Literal[
        "continuity", "agents", "proactive", "routing", "perception", "memory", "end_to_end"
    ]
    initial_state: Literal["ISOLATED_FIXTURE_V1"] = "ISOLATED_FIXTURE_V1"
    input: dict[Literal["case"], Key]
    checks: list[Check] = Field(min_length=1, max_length=20)
    tags: list[Literal["smoke", "regression", "metamorphic", "safety"]] = Field(max_length=4)

    @model_validator(mode="after")
    def complete_definition(self):
        if set(self.input) != {"case"} or self.operation != self.category.lower():
            raise ValueError("Scenario requires its typed case and matching category")
        if len({check.name for check in self.checks}) != len(self.checks):
            raise ValueError("Duplicate grader names would distort denominators")
        return self


class EvaluationDataset(Contract):
    name: Literal["nova-golden"] = "nova-golden"
    version: Literal["1.0.0"] = "1.0.0"
    fixture_version: Literal["nova-fixtures-v1"] = "nova-fixtures-v1"
    scenarios: list[EvaluationScenario] = Field(min_length=100, max_length=150)

    @model_validator(mode="after")
    def unique(self):
        if len({s.scenario_id for s in self.scenarios}) != len(self.scenarios):
            raise ValueError("Duplicate scenario identity")
        return self


class GraderResult(Contract):
    name: Key
    grader: str
    severity: Severity
    metric: Key
    passed: bool
    expected: Scalar | list[Scalar]
    observed: Scalar | list[Scalar]
    reason: Text


class MetricResult(Contract):
    name: Key
    numerator: float | None
    denominator: int = Field(ge=0)
    value: float | None
    methodology: Text
    unit: Literal["ratio", "ms", "USD", "count"] = "ratio"

    @model_validator(mode="after")
    def valid(self):
        if any(v is not None and not math.isfinite(v) for v in [self.numerator, self.value]):
            raise ValueError("Nonfinite metric")
        if self.denominator == 0 and (self.value is not None or self.numerator is not None):
            raise ValueError("Zero denominator requires unknown value")
        if self.unit == "ratio" and self.value is not None and not 0 <= self.value <= 1:
            raise ValueError("Invalid ratio")
        if self.unit == "ratio" and self.denominator:
            if (
                self.numerator is None
                or self.value is None
                or not 0 <= self.numerator <= self.denominator
                or not math.isclose(self.value, self.numerator / self.denominator, abs_tol=1e-12)
            ):
                raise ValueError("Ratio must match its defined numerator/denominator")
        return self


class RegressionGateResult(Contract):
    name: Key
    status: Literal["PASS", "FAIL", "NOT_APPLICABLE"]
    observed: float | None
    threshold: float
    methodology: Text
    version: Literal["gates-v1"] = "gates-v1"


class RunInput(Contract):
    idempotency_key: Key
    dataset_version: Literal["1.0.0"] = "1.0.0"
    suite: Suite = "SMOKE"
    configuration: Configuration = "BASELINE"
    fixture_judge: bool = False


class CompareInput(Contract):
    baseline_id: UUID
    candidate_id: UUID


class ExperimentDefinition(Contract):
    idempotency_key: Key
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
    mode: Literal["AB", "SHADOW", "CANARY"]
    candidate_percentage: int = Field(default=20, ge=0, le=100)
    suite: Suite = "REGRESSION"
    baseline: Literal["BASELINE"] = "BASELINE"
    candidate: Literal["CAUTIOUS_THRESHOLD"] = "CAUTIOUS_THRESHOLD"


class ExperimentAssignment(Contract):
    subject: Key
    bucket: int = Field(ge=0, le=9999)
    variant: Literal["BASELINE", "CANDIDATE"]


class ExperimentRunInput(Contract):
    idempotency_key: Key


class JudgeRequest(Contract):
    rubric_version: Literal["coherence-v1"] = "coherence-v1"
    content: Annotated[str, StringConstraints(max_length=1000)]


class JudgeResponse(Contract):
    rubric_version: Literal["coherence-v1"] = "coherence-v1"
    score: int = Field(ge=0, le=2)
    reason: Text
    provider: Literal["fixture-judge"] = "fixture-judge"
    model: Literal["deterministic-rubric-v1"] = "deterministic-rubric-v1"
    simulation: Literal[True] = True
    trace_id: UUID
    disclosure: Literal["FIXTURE JUDGE / NOT REAL LLM-AS-JUDGE"] = (
        "FIXTURE JUDGE / NOT REAL LLM-AS-JUDGE"
    )


class ScenarioEvaluationResult(Contract):
    scenario_id: Key
    version: int = Field(ge=1)
    category: Category
    status: Literal["PASS", "FAIL", "ERROR"]
    elapsed_ms: float = Field(ge=0, allow_inf_nan=False)
    observation: dict
    graders: list[GraderResult] = Field(max_length=20)
    judge: JudgeResponse | None

    @model_validator(mode="after")
    def bounded(self):
        import json

        if len(json.dumps(self.observation, allow_nan=False)) > 32000:
            raise ValueError("Observation exceeds evidence bound")
        return self


class EvaluationRunRead(Contract):
    id: UUID
    status: Literal["RUNNING", "DONE", "FAILED"]
    suite: Suite
    configuration: Configuration
    configuration_fingerprint: Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
    reproducibility: dict
    summary: dict
    metrics: list[MetricResult] = Field(max_length=30)
    gates: list[RegressionGateResult] = Field(max_length=20)
    scenarios: list[ScenarioEvaluationResult] = Field(max_length=150)
    started_at: str
    completed_at: str | None
    safe_error: str | None
