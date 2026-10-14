"""Narrow deterministic policy, not general profiling or natural-language truth inference."""

BAD = (
    "ignore previous",
    "ignore all previous",
    "system prompt",
    "execute tool",
    "approve action",
    "send the message",
    "api_key",
    "password",
    "private key",
    "social security",
    "medical diagnosis",
    "religion",
    "sexual orientation",
    "political affiliation",
    "race=",
    "ethnicity",
)


class MemoryPolicy:
    def decide(self, origin, memory_type, scope, text, confidence=None, conflict=False):
        if any(marker in text.casefold() for marker in BAD):
            return "REJECT", "UNSUPPORTED_OR_UNSAFE_CONTENT"
        if memory_type == "TASK_CONTEXT" or scope == "TASK":
            if origin in {"USER_EXPLICIT", "USER_CORRECTION", "FIXTURE"}:
                return "TASK_ONLY", "BOUNDED_TASK_CONTEXT"
        if origin in {"AGENT_INFERRED", "VISUAL_OBSERVATION", "TASK_OUTCOME"}:
            return "ASK_CONFIRMATION", "UNCONFIRMED_INFERENCE"
        if conflict and origin != "USER_CORRECTION":
            return "ASK_CONFIRMATION", "STRUCTURED_CONTRADICTION"
        return "STORE", "EXPLICIT_OR_FIXTURE_SOURCE"
