import math
from statistics import median

from app.evaluation.contracts import GraderResult, MetricResult, RegressionGateResult


def grade(check, observation):
    value = observation
    present = True
    for part in check.field.split("."):
        if not isinstance(value, dict) or part not in value:
            present = False
            value = None
            break
        value = value[part]
    try:
        passed = (
            present
            and {
                "EQ": lambda: value == check.expected,
                "NE": lambda: value is not None and value != check.expected,
                "CONTAINS": lambda: check.expected in value,
                "EXCLUDES": lambda: check.expected not in value,
                "SET": lambda: set(value) == set(check.expected),
                "LTE": lambda: value <= check.expected,
            }[check.operation]()
        )
    except (TypeError, ValueError):
        passed = False
    if isinstance(value, (dict, list)):
        value = (
            value[:30]
            if isinstance(value, list)
            and all(isinstance(v, (str, int, float, bool)) for v in value)
            else None
        )
    return GraderResult(
        name=check.name,
        grader=check.grader,
        severity=check.severity,
        metric=check.metric,
        passed=bool(passed),
        expected=check.expected,
        observed=value,
        reason="Expectation satisfied" if passed else "Expected observation differs or is missing",
    )


def metrics(results):
    data = []
    for name in [
        "task_success",
        "agent_compliance",
        "tool_correctness",
        "tool_argument_exact_match",
        "memory_compliance",
        "perception_compliance",
        "routing_compliance",
        "proactive_compliance",
        "policy_compliance",
    ]:
        grades = [g for r in results for g in r.graders if g["metric"] == name]
        passed = (
            sum(r.status == "PASS" for r in results)
            if name == "task_success"
            else sum(g["passed"] for g in grades)
        )
        n = len(results) if name == "task_success" else len(grades)
        data.append(
            MetricResult(
                name=name,
                numerator=passed if n else None,
                denominator=n,
                value=passed / n if n else None,
                methodology="Passing scenarios / executed scenarios"
                if name == "task_success"
                else "Passing named checks / applicable named checks; checks-v2",
            )
        )
    elapsed = sorted(r.elapsed_ms for r in results)
    for name, value in [
        ("fixture_latency_p50", median(elapsed) if len(elapsed) >= 20 else None),
        (
            "fixture_latency_p95",
            elapsed[math.ceil(len(elapsed) * 0.95) - 1] if len(elapsed) >= 20 else None,
        ),
    ]:
        data.append(
            MetricResult(
                name=name,
                numerator=value,
                denominator=len(elapsed) if value is not None else 0,
                value=value,
                unit="ms",
                methodology="Fixture wall time incl setup; nearest-rank P95/median P50; min 20",
            )
        )
    # Reuse only actual ModelRoutingService metadata; do not infer missing prices.
    costs = [c for r in results for c in r.observation.get("accounting", [])]
    known = [
        float(c["estimated_cost_usd"]) for c in costs if c.get("estimated_cost_usd") is not None
    ]
    data.append(
        MetricResult(
            name="configured_api_cost_usd",
            numerator=sum(known) if known else None,
            denominator=len(known),
            value=sum(known) if known else None,
            unit="USD",
            methodology="Phase 4 estimate sum; known calls only; missing costs excluded",
        )
    )
    for name, status in [
        ("unknown_cost_calls", "COST_UNKNOWN"),
        ("unpriced_local_compute_calls", "LOCAL_COMPUTE_NOT_PRICED"),
        ("fixture_zero_api_spend_calls", "FIXTURE_ZERO_API_SPEND"),
    ]:
        count = sum(c.get("cost_status") == status for c in costs)
        data.append(
            MetricResult(
                name=name,
                numerator=count if costs else None,
                denominator=len(costs),
                value=count if costs else None,
                unit="count",
                methodology="Recorded Phase 4 accounting categories; no missing price inferred",
            )
        )
    for key in ["recall_at_5", "mrr"]:
        scores = [float(r.observation[key]) for r in results if key in r.observation]
        data.append(
            MetricResult(
                name=key,
                numerator=sum(scores) if scores else None,
                denominator=len(scores),
                value=sum(scores) / len(scores) if scores else None,
                methodology="Expected memory IDs; fixture system only",
            )
        )
    return [m.model_dump(mode="json") for m in data]


def gates(results, metric_rows):
    critical = sum(
        not g["passed"] and g["severity"] == "CRITICAL" for r in results for g in r.graders
    )
    errors = sum(r.status == "ERROR" for r in results)
    success = next(m["value"] for m in metric_rows if m["name"] == "task_success")
    p95 = next(m["value"] for m in metric_rows if m["name"] == "fixture_latency_p95")
    return [
        RegressionGateResult(
            name=name,
            status="NOT_APPLICABLE" if value is None else "PASS" if passed else "FAIL",
            observed=value,
            threshold=threshold,
            methodology=method,
        ).model_dump(mode="json")
        for name, value, threshold, passed, method in [
            (
                "critical_violations",
                critical,
                0,
                critical == 0,
                "Any critical privacy/HITL/isolation/provenance invariant failure blocks",
            ),
            (
                "execution_errors",
                errors,
                0,
                errors == 0,
                "Unexpected scenario execution error blocks",
            ),
            (
                "minimum_task_success",
                success,
                0.95,
                success is not None and success >= 0.95,
                "Predeclared fixture task-success floor 0.95; no requirement for perfect quality",
            ),
            (
                "fixture_latency_limit",
                p95,
                60000,
                p95 is not None and p95 <= 60000,
                "Fixture P95 limit 60s; insufficient samples not applicable",
            ),
        ]
    ]
