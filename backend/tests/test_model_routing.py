import asyncio
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import func, select

from app.config import settings
from app.database import SessionLocal
from app.intelligence.plugins import KernelRuntime
from app.model_routing.budget import BudgetPolicy
from app.model_routing.cache import ResultCache
from app.model_routing.circuit import Circuit
from app.model_routing.contracts import ModelRequest, Price, ProviderResult, ProviderSpec
from app.model_routing.kernel_provider import RoutedModelProvider
from app.model_routing.models import BudgetDay, ModelCall
from app.model_routing.policy import classify, upper_bound_cost
from app.model_routing.providers import (
    FixtureInferenceProvider,
    InferenceProvider,
    LocalOpenAICompatibleProvider,
    ProviderFailure,
    validate_local_url,
)
from app.model_routing.registry import ProviderRegistry
from app.model_routing.service import ModelRoutingService, recover_model_calls
from app.proactive.clock import FixtureClock
from app.proactive.communication import CommunicationAgent, register_communication
from app.proactive.contracts import CommunicationInput, ContextEventInput, Mutation
from app.proactive.models import ActionExecution, ApprovalDecision
from app.proactive.service import ProactiveService
from app.proactive.trigger import ProactiveTriggerEngine, RedisCooldown, demo_meeting
from app.seed import DEMO_USER_ID


class TestProvider(InferenceProvider):
    __test__ = False

    def __init__(self, kind="LOCAL", failure=None, price=None, capabilities=None, output=None):
        self.spec = ProviderSpec(
            provider="test-provider",
            model="test-model",
            kind=kind,
            tiers=["LOCAL" if kind == "LOCAL" else "SMALL"],
            enabled=True,
            strength=8,
            capabilities=capabilities or ["TEXT", "STRUCTURED", "REASONING"],
            priced_external=kind == "CLOUD",
            price=price,
        )
        self.calls = 0
        self.failure, self.output = failure, output

    async def generate(self, request):
        self.calls += 1
        if self.failure:
            raise ProviderFailure(self.failure)
        return (
            self.output
            if self.output is not None
            else ProviderResult(
                output={"summary": "Known test response"},
                finish_reason="stop",
                input_tokens=20,
                output_tokens=10,
                usage_source="PROVIDER_REPORTED",
            )
        )


def price():
    return Price(
        input_cost_per_million=1,
        output_cost_per_million=2,
        effective_date="TEST_ONLY",
        source="Manually configured synthetic test price",
    )


def req(task, **changes):
    fields = dict(
        task_id=task["id"],
        trace_id=uuid4(),
        user_id=DEMO_USER_ID,
        purpose="SUMMARY",
        structured_input={"instruction": "generic overview"},
        privacy_class="INTERNAL",
        current_device="DESKTOP",
    )
    fields.update(changes)
    return ModelRequest(**fields)


@pytest.fixture
def cache():
    return ResultCache(settings.redis_url, prefix=f"nova:test:model:{uuid4()}")


def service(cache, *providers, budget=None, allow=False):
    return ModelRoutingService(
        providers=ProviderRegistry(list(providers)),
        cache=cache,
        budget=budget,
        allow_personal_cloud=allow,
    )


def count(model):
    with SessionLocal() as session:
        return session.scalar(select(func.count()).select_from(model))


@pytest.mark.parametrize(
    "changes",
    [
        {"max_output_tokens": 0},
        {"max_output_tokens": 4097},
        {"base_url": "https://attacker.example"},
        {"approval": True},
        {"privacy_class": "FAKE"},
        {"required_capabilities": ["VISION"]},
        {"structured_input": {"x": "x" * 32001}},
    ],
)
def test_typed_request_rejects_invalid_or_oversized_input(task, changes):
    with pytest.raises(ValidationError):
        req(task, **changes)


@pytest.mark.parametrize(
    "changes",
    [
        {"input_tokens": -1},
        {"input_tokens": 1.5},
        {"input_tokens": True},
        {"estimated_cost_usd": 0},
        {"approval": True},
        {"privacy_class": "PUBLIC"},
        {"input_tokens": 10},
    ],
)
def test_provider_result_rejects_usage_and_policy_manipulation(changes):
    with pytest.raises(ValidationError):
        ProviderResult(output={"summary": "Test"}, finish_reason="stop", **changes)


def test_fixture_declarations_and_unknown_tokens(task, cache):
    fixture = FixtureInferenceProvider()
    assert fixture.spec.kind == "FIXTURE" and "REASONING_REPLAY" in fixture.spec.capabilities
    result = service(cache, fixture).run(req(task))
    assert result.status == "DONE" and result.provider == "fixture"
    assert result.total_tokens is None and result.usage_source == "UNKNOWN"
    assert result.estimated_cost_usd == 0 and result.cost_status == "FIXTURE_ZERO_API_SPEND"


def test_privacy_complexity_classification_never_downgrades(task):
    privacy, complexity, reason = classify(
        req(
            task,
            privacy_class="PUBLIC",
            structured_input={"instruction": "Review Sarah's meetings and travel constraints"},
        )
    )
    assert privacy == "PERSONAL" and complexity == "REASONING"
    assert reason == "CONSTRAINT_RECONCILIATION"
    assert classify(req(task, privacy_class="SENSITIVE_LOCAL_ONLY"))[0] == "SENSITIVE_LOCAL_ONLY"


@pytest.mark.parametrize(
    "device,complexity,expected",
    [
        ("DESKTOP", "LOW", "test-provider"),
        ("MOBILE", "LOW", "test-provider"),
        ("MOBILE", "REASONING", "fixture"),
        ("WEARABLE", "LOW", "fixture"),
    ],
)
def test_device_routing_is_explicit_policy(task, cache, device, complexity, expected):
    result = service(cache, TestProvider(), FixtureInferenceProvider()).run(
        req(task, current_device=device, complexity=complexity)
    )
    assert result.provider == expected
    assert result.decision.device_context == device
    if expected == "fixture":
        assert "DEVICE_LIMITED" in result.decision.reason_codes


def test_local_preference_latency_and_reasoning_requirement(task, cache):
    local = TestProvider(capabilities=["TEXT", "STRUCTURED"])
    result = service(cache, local, FixtureInferenceProvider()).run(req(task))
    assert result.provider == local.spec.provider
    result = service(cache, local, FixtureInferenceProvider()).run(
        req(task, complexity="REASONING")
    )
    assert (
        result.provider == "fixture"
        and "REASONING_REPLAY_LIMITATION" in result.decision.reason_codes
    )
    local.spec.latency_class = "SLOW"
    result = service(cache, local, FixtureInferenceProvider()).run(
        req(task, preferred_latency="FAST")
    )
    assert result.provider == "fixture" and "LATENCY_LIMIT" in result.decision.reason_codes


def test_cloud_never_eligible_local_only_even_after_failure(task, cache):
    local = TestProvider(failure="TIMEOUT")
    cloud = TestProvider(kind="CLOUD", price=price())
    cloud.spec.provider = "test-cloud"
    s = service(
        cache, local, cloud, FixtureInferenceProvider(), budget=BudgetPolicy(1, 1), allow=True
    )
    result = s.run(req(task, privacy_class="SENSITIVE_LOCAL_ONLY"))
    assert result.provider == "fixture" and cloud.calls == 0
    assert "PRIVACY_LOCAL_ONLY" in result.decision.reason_codes
    assert result.cache_status == "BYPASS" and result.fallback_used


def test_personal_cloud_requires_explicit_server_policy(task, cache):
    cloud = TestProvider(kind="CLOUD", price=price())
    result = service(cache, cloud, FixtureInferenceProvider(), budget=BudgetPolicy(1, 1)).run(
        req(task, privacy_class="PERSONAL")
    )
    assert cloud.calls == 0 and result.provider == "fixture"
    assert "PERSONAL_CLOUD_DISABLED" in result.decision.reason_codes


def test_no_eligible_provider_fails_controlled(task, cache):
    cloud = TestProvider(kind="CLOUD", price=price())
    result = service(cache, cloud, budget=BudgetPolicy(1, 1), allow=True).run(
        req(task, privacy_class="SENSITIVE_LOCAL_ONLY")
    )
    assert result.status == "FAILED" and result.safe_error == "POLICY_BLOCKED" and cloud.calls == 0


@pytest.mark.parametrize(
    "code",
    [
        "TIMEOUT",
        "UNAVAILABLE",
        "RATE_LIMITED",
        "INVALID_RESPONSE",
        "CONTEXT_LIMIT",
        "AUTH_ERROR",
        "UNKNOWN_PROVIDER_ERROR",
    ],
)
def test_error_taxonomy_and_bounded_fallback(task, cache, code):
    local = TestProvider(failure=code)
    result = service(cache, local, FixtureInferenceProvider()).run(req(task))
    assert result.status == "DONE" and result.provider == "fixture"
    with SessionLocal() as session:
        call = session.scalar(select(ModelCall))
        assert call.attempts[0]["error"] == code and len(call.attempts) == 2
        assert "FALLBACK_USED" in call.routing_decision["reason_codes"]


def test_unknown_error_cannot_persist_private_payload(task, cache):
    secret = "RAW_PROVIDER_SECRET_MUST_NOT_PERSIST"
    local = TestProvider(failure=secret)
    service(cache, local, FixtureInferenceProvider()).run(
        req(task, structured_input={"instruction": "PRIVATE_PROMPT_MUST_NOT_PERSIST"})
    )
    with SessionLocal() as session:
        call = session.scalar(select(ModelCall))
        serialized = str(call.__dict__)
        assert secret not in serialized and "PRIVATE_PROMPT_MUST_NOT_PERSIST" not in serialized
        assert call.attempts[0]["error"] == "UNKNOWN_PROVIDER_ERROR"
        assert call.response_metadata["output"] is None


@pytest.mark.parametrize(
    "output",
    [
        {"summary": "x", "approval": True},
        {"summary": "x", "privacy_class": "PUBLIC"},
        {"summary": "x", "provider": "cloud"},
        {"summary": "x" * 4001},
        {"unexpected": "schema"},
    ],
)
def test_untrusted_output_cannot_change_policy_or_schema(task, cache, output):
    local = TestProvider(output=ProviderResult(output=output, finish_reason="stop"))
    result = service(cache, local, FixtureInferenceProvider()).run(req(task))
    assert result.provider == "fixture"
    with SessionLocal() as session:
        assert session.scalar(select(ModelCall)).attempts[0]["error"] == "INVALID_RESPONSE"


def test_budget_per_request_and_missing_pricing_never_invoke(task, cache):
    provider = TestProvider(kind="CLOUD", price=price())
    result = service(
        cache,
        provider,
        FixtureInferenceProvider(),
        budget=BudgetPolicy(1, Decimal("0.001")),
        allow=True,
    ).run(req(task))
    assert provider.calls == 0 and "BUDGET_DOWNGRADE" in result.decision.reason_codes
    provider.spec.price = None
    assert upper_bound_cost(provider.spec, 512) is None
    result = service(
        cache, provider, FixtureInferenceProvider(), budget=BudgetPolicy(1, 1), allow=True
    ).run(req(task))
    assert provider.calls == 0 and "BUDGET_BLOCKED" in result.decision.reason_codes


def test_budget_daily_accounting_settlement_and_utc(task, cache):
    provider = TestProvider(kind="CLOUD", price=price())
    budget = BudgetPolicy(Decimal("0.03382"), Decimal("0.1"))
    s = service(cache, provider, FixtureInferenceProvider(), budget=budget, allow=True)
    first = s.run(req(task))
    assert first.provider == "test-provider" and first.cost_status == "CONFIGURED_ESTIMATE"
    assert first.estimated_cost_usd == Decimal("0.00004")
    second = s.run(req(task, structured_input={"instruction": "different request"}))
    assert second.provider == "fixture" and provider.calls == 1
    with SessionLocal() as session:
        row = session.get(BudgetDay, (DEMO_USER_ID, datetime.now(UTC).date()))
        assert row.consumed_usd == Decimal("0.00004") and row.reserved_usd == 0
    moment = datetime(2026, 10, 15, 1, 0, tzinfo=timezone(timedelta(hours=2)))
    assert moment.astimezone(UTC).date().isoformat() == "2026-10-14"


def test_budget_concurrency_reserves_before_provider_call(task, cache):
    entered, release = threading.Event(), threading.Event()

    class GatedProvider(TestProvider):
        async def generate(self, request):
            entered.set()
            assert release.wait(10)
            return await super().generate(request)

    provider = GatedProvider(kind="CLOUD", price=price())
    s = service(
        cache,
        provider,
        FixtureInferenceProvider(),
        budget=BudgetPolicy(Decimal("0.034"), Decimal("0.1")),
        allow=True,
    )
    with ThreadPoolExecutor(max_workers=4) as pool:
        primary = pool.submit(s.run, req(task, structured_input={"instruction": "primary"}))
        assert entered.wait(5)
        with SessionLocal() as session:
            budget = session.get(BudgetDay, (DEMO_USER_ID, datetime.now(UTC).date()))
            assert budget.reserved_usd == Decimal("0.033792")
        remaining = list(
            pool.map(
                lambda i: s.run(req(task, structured_input={"instruction": f"other-{i}"})), range(3)
            )
        )
        assert all(result.provider == "fixture" for result in remaining)
        release.set()
        assert primary.result().provider == "test-provider"
    assert provider.calls == 1


def test_unknown_usage_failure_conservatively_accounts_reservation(task, cache):
    provider = TestProvider(kind="CLOUD", price=price(), failure="TIMEOUT")
    s = service(cache, provider, FixtureInferenceProvider(), budget=BudgetPolicy(1, 1), allow=True)
    s.run(req(task))
    with SessionLocal() as session:
        row = session.get(BudgetDay, (DEMO_USER_ID, datetime.now(UTC).date()))
        assert row.reserved_usd == 0 and row.consumed_usd == Decimal("0.033792")


def test_local_compute_not_priced_and_reported_token_provenance(task, cache):
    result = service(cache, TestProvider()).run(req(task))
    assert result.cost_status == "LOCAL_COMPUTE_NOT_PRICED" and result.estimated_cost_usd is None
    assert result.total_tokens == 30 and result.usage_source == "PROVIDER_REPORTED"


def test_token_limit_manipulation_fails_before_accounting(task, cache):
    provider = TestProvider(
        kind="CLOUD",
        price=price(),
        output=ProviderResult(
            output={"summary": "test"},
            finish_reason="stop",
            input_tokens=999999,
            output_tokens=1,
            usage_source="PROVIDER_REPORTED",
        ),
    )
    result = service(
        cache, provider, FixtureInferenceProvider(), budget=BudgetPolicy(1, 1), allow=True
    ).run(req(task))
    assert result.provider == "fixture"
    with SessionLocal() as session:
        assert session.scalar(select(ModelCall)).attempts[0]["error"] == "INVALID_RESPONSE"


def test_cache_hit_miss_no_extra_invocation_and_user_isolation(task, cache):
    provider = TestProvider()
    s = service(cache, provider)
    first = s.run(req(task))
    second = s.run(req(task))
    assert first.cache_status == "MISS" and second.cache_status == "HIT" and provider.calls == 1
    assert (
        second.latency_ms is None and second.total_tokens is None and second.estimated_cost_usd == 0
    )
    a = req(task)
    b = a.model_copy(update={"user_id": uuid4()})
    assert cache.key(a, provider.spec) != cache.key(b, provider.spec)


def test_cache_sensitive_bypass_and_redis_outage(task, cache):
    provider = TestProvider()
    s = service(cache, provider)
    for _ in range(2):
        assert s.run(req(task, privacy_class="SENSITIVE_LOCAL_ONLY")).cache_status == "BYPASS"
    assert provider.calls == 2
    broken = ResultCache("redis://127.0.0.1:1/0")
    assert service(broken, provider).run(req(task)).cache_status == "ERROR"


def test_cache_ttl_and_signed_poisoning(task, cache):
    provider = TestProvider()
    request = req(task)
    key = cache.key(request, provider.spec)
    cache.ttl = 1
    result = asyncio.run(provider.generate(request))
    cache.put(key, result)
    assert cache.get(key)[1] == "HIT" and 0 <= cache.client.ttl(key) <= 1
    cache.client.set(
        key,
        json.dumps(
            {
                "body": json.dumps(
                    {"key": key, "expires": time.time() + 3600, "result": result.model_dump()}
                ),
                "signature": "forged",
            }
        ),
        ex=2,
    )
    assert cache.get(key)[1] == "ERROR"
    cache.put(key, result)
    cache.client.pexpire(key, 1)
    time.sleep(0.02)
    assert cache.get(key)[1] == "MISS"
    cache.client.set(key, b"{malformed", ex=2)
    assert cache.get(key)[1] == "ERROR"


def test_cache_stampede_and_duplicate_request_do_not_repeat_calls(task, cache):
    provider = TestProvider()
    s = service(cache, provider)
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda _: s.run(req(task)), range(6)))
    assert provider.calls == 1 and sum(r.cache_status == "HIT" for r in results) == 5
    request = req(task, structured_input={"instruction": "different"})
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda _: s.run(request), range(6)))
    assert sum(r.replayed for r in results) == 5
    assert count(ModelCall) == 7 and provider.calls == 2
    with pytest.raises(HTTPException) as conflict:
        s.run(request.model_copy(update={"structured_input": {"instruction": "changed"}}))
    assert conflict.value.status_code == 409


def test_circuit_open_half_open_race_and_cancel():
    now = [0.0]
    circuit = Circuit(threshold=2, cooldown=5, clock=lambda: now[0])
    circuit.failure()
    circuit.failure()
    assert circuit.state() == "OPEN" and not circuit.admit()
    now[0] = 5
    with ThreadPoolExecutor(max_workers=6) as pool:
        admitted = list(pool.map(lambda _: circuit.admit(), range(6)))
    assert sum(admitted) == 1 and circuit.state() == "HALF_OPEN"
    circuit.cancel()
    assert circuit.admit()
    circuit.success()
    assert circuit.state() == "CLOSED" and circuit.failures == 0


def test_known_failing_provider_is_not_hammered(task, cache):
    provider = TestProvider(failure="UNAVAILABLE")
    s = service(cache, provider, FixtureInferenceProvider())
    for i in range(5):
        s.run(req(task, structured_input={"instruction": f"unique-{i}"}))
    assert provider.calls == 3 and s.registry.circuits[provider.spec.provider].state() == "OPEN"


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/v1",
        "http://169.254.169.254/v1",
        "http://localhost.attacker.example/v1",
        "http://user:secret@localhost/v1",
        "http://localhost/v1?url=http://attacker",
        "file:///tmp/model",
        "http://localhost/redirect",
    ],
)
def test_local_url_restrictions_and_no_request_url_control(url):
    with pytest.raises(ValueError):
        validate_local_url(url)


def local_response(model="test-local", usage=None, output=None, status=200):
    return httpx.Response(
        status,
        json={
            "model": model,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(output or {"summary": "real-shaped local response"}),
                    },
                    "finish_reason": "stop",
                }
            ],
            **({"usage": usage} if usage is not None else {}),
        },
    )


def test_local_adapter_mapping_usage_health_and_no_install(task):
    observed = []

    def handler(request):
        observed.append(request)
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": [{"id": "test-local"}]})
        return local_response(
            usage={"prompt_tokens": 15, "completion_tokens": 10, "total_tokens": 25}
        )

    provider = LocalOpenAICompatibleProvider(
        True, "http://localhost:11434/v1", "test-local", transport=httpx.MockTransport(handler)
    )
    assert provider.available() and provider.health()["last_checked"]
    provider.health()
    assert len(observed) == 1
    result = asyncio.run(provider.generate(req(task)))
    body = json.loads(observed[-1].content)
    assert body["model"] == "test-local" and body["max_tokens"] == 512 and body["stream"] is False
    assert body["response_format"] == {"type": "json_object"}
    assert "authorization" not in observed[-1].headers
    assert result.usage_source == "PROVIDER_REPORTED" and result.input_tokens == 15
    provider.invalidate_health()
    assert provider.health()["state"] == "DEGRADED" and len(observed) == 2


def test_disabled_local_provider_never_constructs_http_client(monkeypatch, task):
    def forbidden(*args, **kwargs):
        raise AssertionError("Disabled provider attempted HTTP")

    monkeypatch.setattr(httpx, "Client", forbidden)
    provider = LocalOpenAICompatibleProvider()
    assert not provider.available() and provider.health()["state"] == "DISABLED"
    with pytest.raises(ProviderFailure):
        asyncio.run(provider.generate(req(task)))


@pytest.mark.parametrize(
    "kind,code",
    [
        ("timeout", "TIMEOUT"),
        ("badjson", "INVALID_RESPONSE"),
        ("wrongmodel", "INVALID_RESPONSE"),
        ("badtokens", "INVALID_RESPONSE"),
        ("huge", "INVALID_RESPONSE"),
        ("redirect", "UNAVAILABLE"),
        ("auth", "AUTH_ERROR"),
        ("ratelimit", "RATE_LIMITED"),
    ],
)
def test_local_provider_error_normalization(task, kind, code):
    def handler(request):
        if kind == "timeout":
            raise httpx.ReadTimeout("RAW PRIVATE ERROR", request=request)
        if kind == "badjson":
            return httpx.Response(200, content=b"{invalid")
        if kind == "wrongmodel":
            return local_response(model="wrong")
        if kind == "badtokens":
            return local_response(
                usage={"prompt_tokens": -1, "completion_tokens": 2, "total_tokens": 1}
            )
        if kind == "huge":
            return httpx.Response(200, content=b"x" * 65537)
        if kind == "redirect":
            return httpx.Response(302, headers={"location": "https://attacker.example"})
        if kind == "auth":
            return httpx.Response(401)
        return httpx.Response(429)

    provider = LocalOpenAICompatibleProvider(
        True, "http://localhost:11434/v1", "test-local", transport=httpx.MockTransport(handler)
    )
    with pytest.raises(ProviderFailure) as error:
        asyncio.run(provider.generate(req(task)))
    assert error.value.code == code and "PRIVATE" not in str(error.value)


def test_missing_local_usage_is_unknown_not_fabricated(task):
    provider = LocalOpenAICompatibleProvider(
        True,
        "http://localhost/v1",
        "test-local",
        transport=httpx.MockTransport(lambda _: local_response()),
    )
    result = asyncio.run(provider.generate(req(task)))
    assert (
        result.input_tokens is None
        and result.output_tokens is None
        and result.usage_source == "UNKNOWN"
    )


def test_kernel_routed_agents_preserve_workflow_and_trace(client, task):
    response = client.post(
        f"/api/v1/tasks/{task['id']}/run-routed-agents",
        json={"idempotency_key": "routed-agent-test"},
    )
    assert response.status_code == 201, response.text
    execution = response.json()["execution"]
    assert execution["status"] == "DONE"
    plan = client.get(f"/api/v1/tasks/{task['id']}/plan").json()
    assert len(plan["agent_runs"]) == 6 and plan["critic"]["verdict"] == "PASS"
    assert KernelRuntime(RoutedModelProvider()).provider.service_id == "routed"
    calls = client.get(f"/api/v1/tasks/{task['id']}/model-calls").json()
    assert len(calls) == 4 and all(call["trace_id"] == execution["trace_id"] for call in calls)
    assert all(call["response"]["output"] is None for call in calls)
    assert {call["purpose"] for call in calls} == {"CONTEXT", "PLANNING", "CRITIQUE"}


def test_model_assisted_draft_still_requires_hitl(task):
    clock = FixtureClock()
    situation, _ = ProactiveTriggerEngine(clock).analyze(demo_meeting(clock, str(task["id"])))
    # Capture the routed draft outside the Phase 3 SQL authorization transaction.
    captured = {}

    class CapturingProvider(RoutedModelProvider):
        async def generate_communication(self, payload, attendee):
            response = await super().generate_communication(payload, attendee)
            captured["response"] = response
            return response

    payload = CommunicationInput(task_id=task["id"], trace_id=uuid4(), situation=situation)
    runtime = KernelRuntime(CapturingProvider())
    register_communication(runtime)
    result = asyncio.run(CommunicationAgent().execute(payload, runtime, uuid4()))
    assert result.intent.source_agent == "COMMUNICATION" and not hasattr(runtime, "executor")
    # Replay the routed semantic draft against the server-owned situation; rebuild ownership fields.
    from app.intelligence.provider import FixtureModelProvider
    from app.proactive.contracts import CommunicationOutput

    class SemanticDraftProvider(FixtureModelProvider):
        async def generate_communication(self, owned, attendee):
            response = await super().generate_communication(owned, attendee)
            output = CommunicationOutput.model_validate_json(response.payload_json)
            output.intent.content = result.intent.content
            return response.model_copy(update={"payload_json": output.model_dump_json()})

    service = ProactiveService(
        provider=SemanticDraftProvider(),
        cooldown=RedisCooldown(settings.redis_url, prefix=f"nova:test:{uuid4()}"),
    )
    evaluated = service.evaluate(
        ContextEventInput(task_id=task["id"], idempotency_key=str(uuid4())), "model-hitl"
    )
    item = evaluated.proposal
    assert item.status == "PENDING_APPROVAL" and item.policy_decision == "REQUIRE_APPROVAL"
    assert count(ApprovalDecision) == count(ActionExecution) == 0
    with pytest.raises(HTTPException):
        service.mutate(item.id, "execute", Mutation(idempotency_key=str(uuid4())), "test")
    assert count(ActionExecution) == 0


def test_api_no_endpoints_secrets_or_policy_injection(client, task):
    for extra in [
        {"base_url": "https://attacker.example"},
        {"api_key": "secret"},
        {"provider": "cloud"},
        {"approval": True},
    ]:
        response = client.post(
            "/api/v1/model-router/evaluate", json={"task_id": task["id"], **extra}
        )
        assert response.status_code == 422
    for scenario in ["SIMPLE", "REASONING", "PRIVACY", "BUDGET", "FAILURE"]:
        response = client.post(
            "/api/v1/model-router/evaluate", json={"task_id": task["id"], "scenario": scenario}
        )
        assert response.status_code == 200, response.text
        result = response.json()
        assert result["status"] == "DONE" and result["provider"] == "fixture"
        assert response.headers["X-Trace-ID"] == result["trace_id"]
        if scenario == "PRIVACY":
            assert result["cache_status"] == "BYPASS"
        if scenario == "BUDGET":
            assert "BUDGET_DOWNGRADE" in result["decision"]["reason_codes"]
        if scenario == "FAILURE":
            assert "FALLBACK_USED" in result["decision"]["reason_codes"]
    providers = client.get("/api/v1/model-router/providers").json()
    assert providers["local_runtime"] == "LOCAL RUNTIME NOT CONFIGURED"
    assert "base_url" not in json.dumps(providers) and "api_key" not in json.dumps(providers)
    assert client.get("/api/v1/model-router/budget").json()["paid_providers_enabled"] is False
    assert len(client.get(f"/api/v1/tasks/{task['id']}/model-calls").json()) == 5
    assert client.get(f"/api/v1/tasks/{uuid4()}/model-calls").status_code == 404


def test_model_call_startup_recovery_preserves_accounting(task):
    from app.model_routing.router import ModelRouter

    request = req(task)
    provider = TestProvider(kind="CLOUD", price=price())
    budget = BudgetPolicy(1, 1)
    owned, decision, _ = ModelRouter(budget, True).choose(
        request, [provider], {"test-provider": Circuit()}
    )
    with SessionLocal.begin() as session:
        call = ModelCall(
            user_id=DEMO_USER_ID,
            task_id=UUID(task["id"]),
            trace_id=request.trace_id,
            request_id=request.request_id,
            request_hash="0" * 64,
            purpose="SUMMARY",
            privacy_class="INTERNAL",
            complexity="LOW",
            status="RUNNING",
            routing_decision=decision.model_dump(mode="json"),
            attempts=[],
            started_at=datetime.now(UTC),
            reserved_cost_usd=0,
        )
        session.add(call)
        session.flush()
        assert budget.reserve(session, call, provider.spec, owned, datetime.now(UTC))
    recover_model_calls()
    with SessionLocal() as session:
        call = session.scalar(select(ModelCall))
        assert call.status == "FAILED" and call.safe_error == "APPLICATION_RESTARTED"
        day = session.get(BudgetDay, (DEMO_USER_ID, datetime.now(UTC).date()))
        assert day.reserved_usd == 0 and day.consumed_usd == Decimal("0.033792")


def test_request_budget_includes_failed_fallback_attempts(task, cache):
    first = TestProvider(kind="CLOUD", price=price(), failure="TIMEOUT")
    second = TestProvider(kind="CLOUD", price=price())
    second.spec.provider = "second-priced-provider"
    second.spec.strength = 7
    result = service(
        cache,
        first,
        second,
        FixtureInferenceProvider(),
        budget=BudgetPolicy(1, Decimal("0.05")),
        allow=True,
    ).run(req(task))
    assert first.calls == 1 and second.calls == 0 and result.provider == "fixture"
    assert "BUDGET_DOWNGRADE" in result.decision.reason_codes
    with SessionLocal() as session:
        call = session.scalar(select(ModelCall))
        assert call.accounted_cost_usd == Decimal("0.033792")
        assert call.attempts[1]["error"] == "BUDGET_BLOCKED"


def test_malformed_cache_envelope_is_error_not_server_failure(task, cache):
    provider = TestProvider()
    request = req(task)
    key = cache.key(request, provider.spec)
    cache.client.set(key, json.dumps({"body": None, "signature": "invalid"}), ex=20)
    result = service(cache, provider).run(request)
    assert result.status == "DONE" and result.cache_status == "ERROR" and provider.calls == 1


def test_provider_input_mutation_cannot_escape_fallback_privacy(task, cache):
    class MutatingProvider(TestProvider):
        async def generate(self, request):
            request.privacy_class = "PUBLIC"
            request.structured_input["instruction"] = "model asks for cloud"
            raise ProviderFailure("TIMEOUT")

    local = MutatingProvider()
    cloud = TestProvider(kind="CLOUD", price=price())
    cloud.spec.provider = "tempting-cloud"
    result = service(
        cache, local, cloud, FixtureInferenceProvider(), budget=BudgetPolicy(1, 1), allow=True
    ).run(req(task, privacy_class="SENSITIVE_LOCAL_ONLY"))
    assert result.provider == "fixture" and result.decision.privacy_class == "SENSITIVE_LOCAL_ONLY"
    assert cloud.calls == 0 and result.cache_status == "BYPASS"


def test_model_request_acknowledgment_after_handoff_preserves_original_device(
    client, task, devices
):
    payload = {"task_id": task["id"], "request_id": str(uuid4()), "scenario": "SIMPLE"}
    first = client.post("/api/v1/model-router/evaluate", json=payload).json()
    assert first["status"] == "DONE"
    client.post(
        f"/api/v1/tasks/{task['id']}/handoff",
        json={
            "source_device_id": devices["DESKTOP"],
            "target_device_id": devices["WEARABLE"],
            "idempotency_key": str(uuid4()),
        },
    )
    replay = client.post("/api/v1/model-router/evaluate", json=payload)
    assert replay.status_code == 200 and replay.json()["replayed"]
    assert replay.json()["decision"]["device_context"] == "DESKTOP"
    assert replay.json()["trace_id"] == first["trace_id"] and count(ModelCall) == 1


def test_budget_denial_without_fallback_has_correct_failure_category(task, cache):
    priced = TestProvider(kind="CLOUD", price=price())
    result = service(cache, priced, budget=BudgetPolicy(0, 0), allow=True).run(req(task))
    assert result.status == "FAILED" and result.safe_error == "BUDGET_BLOCKED" and priced.calls == 0
    assert result.estimated_cost_usd is None and result.cost_status == "COST_UNKNOWN"
    with SessionLocal() as session:
        assert session.scalar(select(ModelCall)).safe_error == "BUDGET_BLOCKED"


def test_explicit_sensitive_markers_and_text_only_modality(task):
    assert (
        classify(
            req(
                task,
                privacy_class="PUBLIC",
                structured_input={"instruction": "Summarize a medical record"},
            )
        )[0]
        == "SENSITIVE_LOCAL_ONLY"
    )
    with pytest.raises(ValidationError):
        req(task, modality="VISION")


def test_routed_proactive_api_shares_trace_and_cannot_authorize(client, task):
    payload = {"task_id": task["id"], "idempotency_key": "routed-proactive-acceptance"}
    response = client.post("/api/v1/proactive/evaluate-routed", json=payload)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["status"] == "SURFACED"
    item = result["proposal"]
    assert item["status"] == "PENDING_APPROVAL"
    assert (
        item["policy_decision"] == "REQUIRE_APPROVAL"
        and count(ApprovalDecision) == count(ActionExecution) == 0
    )
    calls = client.get(f"/api/v1/tasks/{task['id']}/model-calls").json()
    assert len(calls) == 1 and calls[0]["purpose"] == "COMMUNICATION"
    assert calls[0]["trace_id"] == item["trace_id"] == response.headers["X-Trace-ID"]
    assert (
        client.post(
            f"/api/v1/proposals/{item['id']}/execute", json={"idempotency_key": "not-approved"}
        ).status_code
        == 409
    )
    again = client.post("/api/v1/proactive/evaluate-routed", json=payload).json()
    assert again["proposal"]["id"] == item["id"] and count(ModelCall) == 1
    approved = client.post(
        f"/api/v1/proposals/{item['id']}/approve", json={"idempotency_key": "human-decision"}
    ).json()
    assert approved["approval"]["payload_hash"] == item["payload_hash"]
    receipt = client.post(
        f"/api/v1/proposals/{item['id']}/execute", json={"idempotency_key": "simulation"}
    ).json()
    assert receipt["execution"]["receipt"]["external_message_sent"] is False


@pytest.mark.parametrize("configured_price", [None, price()])
def test_cloud_cannot_disable_budget_with_priced_flag(task, cache, configured_price):
    cloud = TestProvider(kind="CLOUD", price=configured_price)
    cloud.spec.priced_external = False
    result = service(
        cache, cloud, FixtureInferenceProvider(), budget=BudgetPolicy(0, 0), allow=True
    ).run(req(task))
    assert cloud.calls == 0 and result.provider == "fixture"
    assert "BUDGET_BLOCKED" in result.decision.reason_codes
    if configured_price is None:
        assert "COST_UNKNOWN" in result.decision.reason_codes


def test_fixture_reasoning_fallback_requires_declared_replay_capability(task, cache):
    fixture = FixtureInferenceProvider()
    result = service(cache, fixture).run(req(task, required_capabilities=["TEXT", "REASONING"]))
    assert result.decision.complexity == "REASONING"
    assert "REASONING_REPLAY_LIMITATION" in result.decision.reason_codes
    text_only = TestProvider(kind="FIXTURE", capabilities=["TEXT"])
    denied = service(cache, text_only).run(req(task, required_capabilities=["TEXT", "REASONING"]))
    assert denied.status == "FAILED" and text_only.calls == 0
    assert "CAPABILITY_UNSUPPORTED" in denied.decision.reason_codes


def test_local_body_deadline_blocks_slow_trickle_without_sleep(monkeypatch):
    from types import SimpleNamespace

    from app.model_routing import providers

    clock = [0.0]
    monkeypatch.setattr(providers, "time", SimpleNamespace(monotonic=lambda: clock[0]))

    class Trickle:
        def iter_bytes(self):
            yield b"{"
            clock[0] = 6.0
            yield b"continued bytes despite elapsed deadline"

    with pytest.raises(ProviderFailure) as error:
        providers.read_bounded(Trickle(), deadline=5)
    assert error.value.code == "TIMEOUT"
