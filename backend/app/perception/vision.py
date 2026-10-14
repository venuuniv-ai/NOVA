"""VLMs participate in the same ModelRouter, budget, privacy and call ledger."""

from abc import abstractmethod

from app.model_routing.contracts import ProviderResult, ProviderSpec
from app.model_routing.providers import InferenceProvider, ProviderFailure
from app.perception.contracts import VisionOutput, VisualOutput

INTERPRETATION = (
    "The simulated wearable observations are consistent with a meeting/work environment; "
    "this is an interpretation, not a verified physical location."
)


class VisionLanguageProvider(InferenceProvider):
    @abstractmethod
    async def generate(self, request): ...


class FixtureVisionLanguageProvider(VisionLanguageProvider):
    spec = ProviderSpec(
        provider="fixture-vlm",
        model="fixture-vlm-v1",
        kind="FIXTURE",
        tiers=["VISION"],
        capabilities=["VISION", "STRUCTURED"],
        enabled=True,
        strength=0,
    )

    async def generate(self, request):
        if not request.vision_simulation_allowed or not request.vision_fixture:
            raise ProviderFailure("POLICY_BLOCKED")
        output = VisionOutput(
            observations=[
                VisualOutput(
                    observation_type="TEXTUAL_INTERPRETATION",
                    label="meeting_work_interpretation",
                    description=INTERPRETATION,
                    processor="FIXTURE_VLM",
                    model=self.spec.model,
                    simulation=True,
                )
            ],
            interpretation=INTERPRETATION,
        )
        return ProviderResult(output=output.model_dump(mode="json"), finish_reason="fixture")
