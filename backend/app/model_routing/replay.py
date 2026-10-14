"""Explicit policy probes, not real model providers or inference benchmarks."""

from decimal import Decimal

from app.model_routing.contracts import Price, ProviderSpec
from app.model_routing.providers import InferenceProvider, ProviderFailure


class BudgetProbeProvider(InferenceProvider):
    spec = ProviderSpec(
        provider="test-priced-probe",
        model="HYPOTHETICAL_PRICE_FIXTURE",
        kind="TEST_POLICY",
        tiers=["SMALL"],
        capabilities=["TEXT", "STRUCTURED", "REASONING"],
        enabled=True,
        strength=8,
        priced_external=True,
        price=Price(
            input_cost_per_million=Decimal("1"),
            output_cost_per_million=Decimal("2"),
            effective_date="TEST_ONLY",
            source="Synthetic policy-test price; no commercial tariff",
        ),
    )

    async def generate(self, request):
        raise ProviderFailure("POLICY_BLOCKED")  # This probe never has a paid transport.


class FailureProbeProvider(InferenceProvider):
    spec = ProviderSpec(
        provider="test-failing-local",
        model="FAILURE_POLICY_FIXTURE",
        kind="LOCAL",
        tiers=["LOCAL"],
        capabilities=["TEXT", "STRUCTURED", "REASONING"],
        enabled=True,
        strength=9,
    )

    async def generate(self, request):
        raise ProviderFailure("UNAVAILABLE")
