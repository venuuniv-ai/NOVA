from semantic_kernel.functions import kernel_function

from app.intelligence.contracts import ProviderResponse
from app.intelligence.plugins import ALLOWED, KernelRuntime
from app.proactive.contracts import (
    Attendee,
    CommunicationInput,
    CommunicationOutput,
)


class CommunicationPlugin:
    @kernel_function(description="Resolve a synthetic demo attendee. Never sends communication.")
    def resolve_demo_attendee(self) -> Attendee:
        return Attendee(recipient="Meeting attendee")


class CommunicationAgent:
    """Draft capability only: no session, approval service, or executor is provided."""

    name = "COMMUNICATION"

    async def execute(
        self, payload: CommunicationInput, runtime: KernelRuntime, run_id
    ) -> CommunicationOutput:
        from app.intelligence.plugins import EmptyQuery

        attendee = await runtime.invoke(
            self.name,
            run_id,
            payload.trace_id,
            "CommunicationPlugin",
            "resolve_demo_attendee",
            EmptyQuery(),
            Attendee,
        )
        response = await runtime.provider.generate_communication(payload, attendee)
        if not isinstance(response, ProviderResponse):
            raise ValueError("Invalid provider envelope.")
        result = CommunicationOutput.model_validate_json(response.payload_json)
        if (
            result.intent.task_id != payload.task_id
            or result.intent.trace_id != payload.trace_id
            or result.intent.context_evidence != payload.situation
            or result.intent.recipient != attendee.recipient
        ):
            raise ValueError("Untrusted action intent does not match its owned context.")
        return result


def register_communication(runtime: KernelRuntime):
    runtime.kernel.add_plugin(CommunicationPlugin(), plugin_name="CommunicationPlugin")


# Fixed application allowlist; agents never register or expand their own capabilities.
ALLOWED["COMMUNICATION"] = {("CommunicationPlugin", "resolve_demo_attendee")}


class SimulatedCommunicationAdapter:
    name = "SIMULATED_COMMUNICATION"

    def execute(self, payload: dict, digest: str) -> dict:
        # Pure computation: no networking library, account integration, or transport.
        return {
            "adapter": self.name,
            "status": "DELIVERED_SIMULATION",
            "receipt_id": f"sim-{digest}",
            "payload_hash": digest,
            "disclosure": "SIMULATED / NOT SENT",
            "external_message_sent": False,
        }


class ActionExecutor:
    """Only the application authorization service receives this adapter."""

    def __init__(self):
        self.adapter = SimulatedCommunicationAdapter()

    def execute_authorized(self, payload: dict, digest: str) -> dict:
        return self.adapter.execute(payload, digest)
