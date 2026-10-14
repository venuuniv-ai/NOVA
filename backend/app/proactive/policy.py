import hashlib
import json
from typing import Literal

from app.proactive.contracts import ActionIntent

PolicyDecision = Literal["ALLOW_WITHOUT_APPROVAL", "REQUIRE_APPROVAL", "DENY"]
POLICY_VERSION = "communication-v1"


def canonical_payload(proposal) -> dict:
    return {
        "action_type": proposal.action_type,
        "recipient": proposal.recipient,
        "channel": proposal.channel,
        "content": proposal.content,
        "task_id": str(proposal.task_id),
    }


def payload_hash(proposal) -> str:
    return hashlib.sha256(
        json.dumps(
            canonical_payload(proposal), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()


def evaluate_policy(proposal) -> tuple[PolicyDecision, str]:
    try:
        ActionIntent.model_validate(
            {
                **canonical_payload(proposal),
                "trace_id": proposal.trace_id,
                "source_agent": "COMMUNICATION",
                "reason": proposal.reason,
                "context_evidence": proposal.situation,
            }
        )
    except (ValueError, TypeError):
        return "DENY", "Malformed or unsupported communication payload."
    # No model-controlled approval flag is consulted. No communication is approval-free.
    return (
        "REQUIRE_APPROVAL",
        "Every communication requires exact human approval, including simulation.",
    )
