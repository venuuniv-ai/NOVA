from app.model_routing.contracts import Candidate, RoutingDecision
from app.model_routing.policy import classify, eligibility, requires_budget, upper_bound_cost


class ModelRouter:
    def __init__(self, budget, allow_personal_cloud=False):
        self.budget, self.allow_personal_cloud = budget, allow_personal_cloud

    def choose(self, request, providers, circuits):
        privacy, complexity, classification = classify(request)
        owned = request.model_copy(
            deep=True, update={"privacy_class": privacy, "complexity": complexity}
        )
        candidates, eligible = [], []
        reasons = [
            "LOCAL_PREFERRED",
            "REASONING_REQUIRED" if complexity == "REASONING" else f"{complexity}_COMPLEXITY",
        ]
        if privacy == "SENSITIVE_LOCAL_ONLY":
            reasons.append("PRIVACY_LOCAL_ONLY")
        budget_decision = "NO_PAID_PROVIDER_REQUIRED"
        for provider in providers:
            spec = provider.spec
            excluded = eligibility(owned, spec, provider.available(), self.allow_personal_cloud)
            if circuits[spec.provider].state() == "OPEN":
                excluded.append("PROVIDER_CIRCUIT_OPEN")
            cost = upper_bound_cost(spec, owned.max_output_tokens)
            if requires_budget(spec) and (cost is None or cost > self.budget.per_request):
                if cost is None:
                    excluded.append("COST_UNKNOWN")
                excluded.append("BUDGET_BLOCKED")
                budget_decision = "DOWNGRADE"
            candidates.append(
                Candidate(
                    provider=spec.provider,
                    model=spec.model,
                    eligible=not excluded,
                    reasons=excluded,
                )
            )
            for reason in excluded:
                if reason not in reasons:
                    reasons.append(reason)
            if not excluded:
                eligible.append(provider)
        eligible.sort(
            key=lambda p: (
                p.spec.kind == "FIXTURE",
                p.spec.kind != "LOCAL" if complexity in {"LOW", "MEDIUM"} else False,
                -p.spec.strength,
            )
        )
        if owned.modality == "IMAGE":
            reasons += ["VISION_REQUIRED", "NO_LOCAL_VLM_CONFIGURED", "CLOUD_VISUAL_FORBIDDEN"]
            if eligible and eligible[0].spec.kind == "FIXTURE":
                reasons.append("FIXTURE_VISION_REPLAY")
        selected = eligible[0] if eligible else None
        if selected and selected.spec.kind == "FIXTURE":
            reasons += ["FIXTURE_FALLBACK", "FIXTURE_NOT_AN_LLM"]
            if complexity == "REASONING":
                reasons += ["NO_REAL_REASONING_PROVIDER", "REASONING_REPLAY_LIMITATION"]
        if budget_decision == "DOWNGRADE":
            reasons.append("BUDGET_DOWNGRADE")
        if selected is None:
            reasons.append("NO_ELIGIBLE_PROVIDER")
        decision = RoutingDecision(
            selected_provider=selected.spec.provider if selected else None,
            selected_model=selected.spec.model if selected else None,
            selected_tier=(
                "VISION"
                if owned.modality == "IMAGE"
                else "FIXTURE"
                if selected.spec.kind == "FIXTURE"
                else "REASONING"
                if complexity == "REASONING"
                else selected.spec.tiers[0]
            )
            if selected
            else None,
            primary_preference="reasoning-capable provider"
            if complexity == "REASONING"
            else "local",
            candidates=candidates,
            reason_codes=reasons,
            privacy_class=privacy,
            complexity=complexity,
            classification_reason=classification,
            privacy_decision="LOCAL_ONLY"
            if privacy == "SENSITIVE_LOCAL_ONLY"
            else "POLICY_CHECKED",
            budget_decision=budget_decision,
            fallback_chain=[p.spec.provider for p in eligible],
            cache_eligible=privacy != "SENSITIVE_LOCAL_ONLY",
            device_context=request.current_device,
        )
        return owned, decision, eligible
