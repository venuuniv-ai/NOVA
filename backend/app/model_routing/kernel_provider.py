import asyncio
from uuid import UUID, uuid4

from app.intelligence.contracts import ProviderResponse
from app.intelligence.provider import FixtureModelProvider, ModelProvider
from app.model_routing.contracts import ModelRequest
from app.model_routing.service import ModelRoutingService
from app.proactive.contracts import CommunicationInput
from app.schemas import DeviceType
from app.security.identity import current_user_id


class RoutedModelProvider(ModelProvider):
    """Kernel service facade: NOVA routes; agents keep the existing typed interface."""

    service_id: str = "routed"
    ai_model_id: str = "nova-router-v1"
    provider_name: str = "NOVA ModelRouter"
    model_name: str = "router-selected"
    capabilities: tuple[str, ...] = ("structured_output", "policy_routing")

    strict_inference_mode: str | None = None

    def routing_service(self):
        if self.strict_inference_mode:
            from app.inference.providers import selected, strict_registry

            return ModelRoutingService(
                providers=strict_registry(selected(self.strict_inference_mode, "STRUCTURED"))
            )
        return ModelRoutingService()

    correlation_id: str = "model-operation"
    communication_request_id: UUID | None = None
    communication_device: DeviceType = "DESKTOP"

    async def generate_structured(self, agent, payload):
        purpose = {"CONTEXT": "CONTEXT", "PLANNER": "PLANNING", "CRITIC": "CRITIQUE"}[agent]
        request = ModelRequest(
            task_id=payload.task_id,
            user_id=payload.user_id,
            trace_id=payload.trace_id,
            purpose=purpose,
            structured_input={"agent_input": payload.model_dump(mode="json")},
            required_capabilities=["STRUCTURED"],
            privacy_class="PERSONAL",
            complexity="REASONING" if agent == "CRITIC" else "MEDIUM",
            current_device=payload.current_device,
            max_output_tokens=4096,
        )
        result = await asyncio.to_thread(self.routing_service().run, request, self.correlation_id)
        if result.status != "DONE" or result.output is None:
            raise ValueError("Controlled model routing failure.")
        import json

        return ProviderResponse(
            provider_name=result.provider or "router",
            model_name=result.model or "router",
            source="DEMO_FIXTURE" if result.route_tier == "FIXTURE" else "MODEL_OUTPUT",
            payload_json=json.dumps(result.output),
        )

    async def generate_communication(self, payload, attendee):
        # Call outside the Phase 3 transaction; proactive defaults remain fixture.
        request = ModelRequest(
            request_id=self.communication_request_id or uuid4(),
            task_id=payload.task_id,
            user_id=current_user_id(),
            trace_id=payload.trace_id,
            purpose="COMMUNICATION",
            privacy_class="PERSONAL",
            complexity="LOW",
            current_device=self.communication_device,
            required_capabilities=["STRUCTURED"],
            structured_input={
                "communication": payload.model_dump(mode="json"),
                "attendee": attendee.model_dump(mode="json"),
            },
        )
        result = await asyncio.to_thread(self.routing_service().run, request, self.correlation_id)
        if result.status != "DONE" or result.output is None:
            raise ValueError("Controlled draft routing failure.")
        import json

        return ProviderResponse(
            provider_name=result.provider or "router",
            model_name=result.model or "router",
            source="DEMO_FIXTURE" if result.route_tier == "FIXTURE" else "MODEL_OUTPUT",
            payload_json=json.dumps(result.output),
        )


class PreparedDraftProvider(FixtureModelProvider):
    """A validated response handoff; no inference happens inside the action transaction."""

    provider_name: str = "NOVA ModelRouter / prepared draft"
    model_name: str = "recorded-model-call"
    prepared_input: CommunicationInput
    prepared_response: ProviderResponse

    async def generate_communication(self, payload, attendee):
        from app.proactive.contracts import CommunicationOutput

        output = CommunicationOutput.model_validate_json(self.prepared_response.payload_json)
        if payload != self.prepared_input or output.intent.recipient != attendee.recipient:
            raise ValueError("Prepared draft context changed; a new preparation is required.")
        return self.prepared_response
