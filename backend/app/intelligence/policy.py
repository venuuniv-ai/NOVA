"""Deterministic plan checks; a provider's PASS cannot bypass application policy."""

from app.fixtures.personal_context import context_evidence
from app.intelligence.contracts import AgentInput, CriticOutput, CritiqueReason, PlanOutput


def review_plan(payload: AgentInput) -> CriticOutput:
    proposed = next(
        (
            result.structured_output
            for result in reversed(payload.prior_results)
            if isinstance(result.structured_output, PlanOutput)
        ),
        None,
    )
    reasons = []
    if proposed is None:
        return CriticOutput(
            verdict="REVISION_REQUIRED",
            reasons=[
                CritiqueReason(code="MISSING_CONTEXT", message="No proposed plan was supplied.")
            ],
        )
    expected = {item.model_dump_json() for item in context_evidence(payload.available_context)}
    actual = {item.model_dump_json() for item in proposed.plan.constraints}
    if actual - expected:
        reasons.append(
            CritiqueReason(
                code="UNSUPPORTED_ASSUMPTION",
                message="A constraint or its provenance is unsupported.",
            )
        )
    if expected - actual or proposed.plan.required_tools:
        reasons.append(
            CritiqueReason(
                code="MISSING_CONTEXT",
                message="Evidence is missing or required context tools remain.",
            )
        )
    if proposed.plan.goal != payload.task_goal:
        reasons.append(
            CritiqueReason(code="CONFLICT", message="Plan goal differs from the owned task.")
        )
    if any(
        assumption != "All personal context is synthetic DEMO_FIXTURE data."
        for assumption in proposed.plan.assumptions
    ):
        reasons.append(
            CritiqueReason(
                code="UNSUPPORTED_ASSUMPTION",
                message="An assumption is unsupported by the supplied fixture context.",
            )
        )
    if any(
        step.action in {"request_confirmation", "deferred_search"} and not step.requires_approval
        for step in proposed.plan.steps
    ):
        reasons.append(
            CritiqueReason(
                code="PRIVACY",
                message="Outbound actions must remain approval-gated and unexecuted.",
            )
        )
    if "dinner" in payload.task_goal.casefold() and not proposed.plan.requires_approval:
        reasons.append(
            CritiqueReason(code="PRIVACY", message="Dinner actions require user approval.")
        )
    if payload.needs.calendar and not payload.available_context.calendar:
        reasons.append(
            CritiqueReason(code="MISSING_CONTEXT", message="Calendar evidence is missing.")
        )
    if payload.needs.preferences and not payload.available_context.preferences:
        reasons.append(
            CritiqueReason(code="MISSING_CONTEXT", message="Preference evidence is missing.")
        )
    if any(
        "found a restaurant" in step.title.casefold() or "booked" in step.title.casefold()
        for step in proposed.plan.steps
    ):
        reasons.append(
            CritiqueReason(
                code="UNNECESSARY_ACTION",
                message="Restaurant discovery and booking are outside Phase 2.",
            )
        )
    return CriticOutput(verdict="REVISION_REQUIRED" if reasons else "PASS", reasons=reasons)
