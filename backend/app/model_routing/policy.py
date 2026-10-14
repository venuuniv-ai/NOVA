from decimal import Decimal

from app.model_routing.contracts import ModelRequest, ProviderSpec

PRIVACY_ORDER = ["PUBLIC", "INTERNAL", "PERSONAL", "SENSITIVE_LOCAL_ONLY"]


def classify(request: ModelRequest) -> tuple[str, str, str]:
    text = str(request.structured_input).casefold()
    privacy_floor = (
        "PERSONAL"
        if request.purpose in {"COMMUNICATION", "PLANNING", "CRITIQUE", "CONTEXT"}
        or any(word in text for word in ["schedule", "meeting", "preference", "sarah"])
        else "INTERNAL"
    )
    if any(
        marker in text
        for marker in (
            "sensitive_local_only",
            "private_key",
            "password",
            "social security",
            "medical record",
        )
    ):
        privacy_floor = "SENSITIVE_LOCAL_ONLY"
    privacy = PRIVACY_ORDER[
        max(PRIVACY_ORDER.index(privacy_floor), PRIVACY_ORDER.index(request.privacy_class))
    ]
    complexity = request.complexity
    reason = "EXPLICIT_PURPOSE"
    if "REASONING" in request.required_capabilities:
        complexity, reason = "REASONING", "REQUIRED_CAPABILITY"
    elif request.purpose == "CRITIQUE" or "reconcile" in text or "travel constraints" in text:
        complexity, reason = "REASONING", "CONSTRAINT_RECONCILIATION"
    elif request.purpose == "PLANNING" and complexity == "LOW":
        complexity, reason = "MEDIUM", "MULTI_CONSTRAINT_PLANNING"
    return privacy, complexity, reason


def requires_budget(spec: ProviderSpec) -> bool:
    return spec.kind == "CLOUD" or spec.priced_external


def upper_bound_cost(spec: ProviderSpec, max_output: int) -> Decimal | None:
    if not requires_budget(spec):
        return Decimal(0)
    if spec.price is None:
        return None
    return (
        Decimal(spec.input_token_limit) * spec.price.input_cost_per_million
        + Decimal(max_output) * spec.price.output_cost_per_million
    ) / Decimal(1_000_000)


def eligibility(request, spec, available, allow_personal_cloud=False):
    reasons = []
    if not spec.enabled or not available:
        reasons.append("PROVIDER_UNAVAILABLE")
    if spec.kind == "CLOUD" or spec.priced_external:
        if request.privacy_class == "SENSITIVE_LOCAL_ONLY":
            reasons.append("PRIVACY_LOCAL_ONLY")
        if request.privacy_class == "PERSONAL" and not allow_personal_cloud:
            reasons.append("PERSONAL_CLOUD_DISABLED")
    required = set(request.required_capabilities)
    if request.complexity == "REASONING":
        required.add("REASONING")
    if spec.kind == "FIXTURE":
        if "REASONING" in required:
            required.discard("REASONING")
            required.add("REASONING_REPLAY")
    if required - set(spec.capabilities):
        reasons.append("CAPABILITY_UNSUPPORTED")
    if request.current_device == "WEARABLE" and spec.kind == "LOCAL":
        reasons.append("DEVICE_LIMITED")
    elif (
        request.current_device == "MOBILE"
        and request.complexity in {"HIGH", "REASONING"}
        and spec.kind == "LOCAL"
    ):
        reasons.append("DEVICE_LIMITED")
    if request.preferred_latency == "FAST" and spec.latency_class == "SLOW":
        reasons.append("LATENCY_LIMIT")
    if request.max_output_tokens > spec.output_token_limit:
        reasons.append("CONTEXT_LIMIT")
    return reasons
