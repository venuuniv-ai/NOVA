from app.config import settings
from app.model_routing.circuit import Circuit
from app.model_routing.providers import FixtureInferenceProvider, LocalOpenAICompatibleProvider
from app.perception.vision import FixtureVisionLanguageProvider


class ProviderRegistry:
    def __init__(self, providers=None):
        self.providers = (
            providers
            if providers is not None
            else [
                LocalOpenAICompatibleProvider(
                    enabled=settings.local_model_enabled,
                    base_url=settings.local_model_base_url,
                    model=settings.local_model_name,
                    timeout=settings.local_model_timeout_seconds,
                    capabilities=["TEXT", "STRUCTURED"]
                    + (["REASONING"] if settings.local_model_reasoning_capable else []),
                    api_key=settings.local_model_api_key.get_secret_value()
                    if settings.local_model_api_key
                    else None,
                ),
                FixtureInferenceProvider(),
                FixtureVisionLanguageProvider(),
            ]
        )
        if len({p.spec.provider for p in self.providers}) != len(self.providers):
            raise ValueError("Duplicate provider identities.")
        self.circuits = {p.spec.provider: Circuit() for p in self.providers}

    def describe(self):
        return [
            {
                "provider": p.spec.provider,
                "model": p.spec.model,
                "kind": p.spec.kind,
                "tiers": p.spec.tiers,
                "capabilities": p.spec.capabilities,
                "health": p.health(),
                "circuit": self.circuits[p.spec.provider].state(),
                "consecutive_failures": self.circuits[p.spec.provider].failures,
                "disclosure": "DETERMINISTIC / NOT AN LLM"
                if p.spec.kind == "FIXTURE"
                else "OPTIONAL LOCAL / EXECUTES ON DEVELOPER HOST",
            }
            for p in self.providers
        ]


registry = ProviderRegistry()
