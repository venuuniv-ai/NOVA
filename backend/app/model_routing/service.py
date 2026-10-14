import asyncio
import hashlib
import json
import logging
import time
from datetime import UTC, datetime
from decimal import Decimal

from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine
from app.model_routing.budget import BudgetPolicy
from app.model_routing.cache import ResultCache
from app.model_routing.contracts import ModelResponse
from app.model_routing.models import BudgetDay, ModelCall
from app.model_routing.policy import eligibility, requires_budget
from app.model_routing.providers import ProviderFailure, validate_result
from app.model_routing.registry import registry
from app.model_routing.router import ModelRouter
from app.models import Task
from app.service import fail

logger = logging.getLogger("nova.models")


def request_digest(request):
    return hashlib.sha256(
        json.dumps(
            request.model_dump(mode="json", exclude={"request_id", "trace_id"}),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()


class ModelRoutingService:
    def __init__(self, providers=None, cache=None, budget=None, allow_personal_cloud=None):
        self.registry = providers or registry
        self.cache = cache or ResultCache(settings.redis_url, settings.model_cache_ttl_seconds)
        self.budget = budget or BudgetPolicy(
            settings.daily_ai_budget_usd, settings.max_request_cost_usd
        )
        self.router = ModelRouter(
            self.budget,
            settings.allow_personal_cloud if allow_personal_cloud is None else allow_personal_cloud,
        )

    def _blank(self, request, decision, **updates):
        return ModelResponse(
            request_id=request.request_id,
            task_id=request.task_id,
            trace_id=request.trace_id,
            provider=decision.selected_provider,
            model=decision.selected_model,
            route_tier=decision.selected_tier,
            output=None,
            finish_reason=None,
            input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            latency_ms=None,
            usage_source="UNKNOWN",
            estimated_cost_usd=None,
            cost_status="COST_UNKNOWN",
            cache_status="BYPASS",
            fallback_used="FIXTURE_FALLBACK" in decision.reason_codes,
            status="FAILED",
            safe_error=None,
            decision=decision,
            mode=request.mode,
            **updates,
        )

    def run(self, request, correlation_id="model-operation"):
        # Dedicated connection keeps the advisory request lock across short commits/provider I/O.
        key = int.from_bytes(
            hashlib.sha256(f"{request.user_id}:{request.request_id}".encode()).digest()[:8], "big"
        ) % (2**63)
        with (
            engine.connect() as connection,
            Session(bind=connection, expire_on_commit=False) as session,
        ):
            session.execute(text("SELECT pg_advisory_lock(:key)"), {"key": key})
            session.commit()
            cache_guard = -1 - (
                int.from_bytes(
                    hashlib.sha256(("exact:" + request_digest(request)).encode()).digest()[:8],
                    "big",
                )
                % (2**63)
            )
            session.execute(text("SELECT pg_advisory_lock(:key)"), {"key": cache_guard})
            session.commit()
            try:
                return self._run_owned(session, request, correlation_id)
            finally:
                session.rollback()
                session.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": cache_guard})
                session.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": key})
                session.commit()

    def _run_owned(self, session, request, correlation_id):
        task = session.scalar(
            select(Task).where(Task.id == request.task_id, Task.user_id == request.user_id)
        )
        if task is None:
            fail(404, "TASK_NOT_FOUND", "Task was not found.")
        digest = request_digest(request)
        existing = session.scalar(
            select(ModelCall).where(
                ModelCall.user_id == request.user_id, ModelCall.request_id == request.request_id
            )
        )
        if existing:
            if existing.request_hash != digest:
                fail(409, "IDEMPOTENCY_CONFLICT", "Model request ID belongs to another input.")
            if existing.response_metadata:
                response = ModelResponse.model_validate(existing.response_metadata)
                return response.model_copy(update={"replayed": True})
            fail(
                409,
                "MODEL_REQUEST_INTERRUPTED",
                "Model request has no completed result; use a new request ID.",
            )
        session.execute(
            insert(BudgetDay)
            .values(
                user_id=request.user_id,
                day=datetime.now(UTC).date(),
                consumed_usd=0,
                reserved_usd=0,
            )
            .on_conflict_do_nothing()
        )
        session.commit()
        owned, decision, candidates = self.router.choose(
            request, self.registry.providers, self.registry.circuits
        )
        call = ModelCall(
            user_id=request.user_id,
            task_id=request.task_id,
            trace_id=request.trace_id,
            request_id=request.request_id,
            request_hash=digest,
            provider=decision.selected_provider,
            model=decision.selected_model,
            tier=decision.selected_tier,
            purpose=request.purpose,
            privacy_class=owned.privacy_class,
            complexity=owned.complexity,
            status="RUNNING",
            routing_decision=decision.model_dump(mode="json"),
            attempts=[],
            started_at=datetime.now(UTC),
            reserved_cost_usd=Decimal(0),
            accounted_cost_usd=Decimal(0),
        )
        session.add(call)
        session.commit()
        response = self._blank(owned, decision)
        attempted = []
        for provider in candidates:
            spec = provider.spec
            circuit = self.registry.circuits[spec.provider]
            # Recheck every fallback using the authoritative request, never provider-mutated input.
            blocked = eligibility(
                owned, spec, provider.available(), self.router.allow_personal_cloud
            )
            if blocked:
                attempted.append(
                    {"provider": spec.provider, "error": "POLICY_BLOCKED", "invoked": False}
                )
                continue
            cache_status = "BYPASS"
            cached = None
            cache_key = self.cache.key(owned, spec)
            if decision.cache_eligible:
                cached, cache_status = self.cache.get(cache_key)
            if cached is not None:
                try:
                    cached = validate_result(owned, cached, spec)
                except (ValidationError, ProviderFailure, ValueError):
                    cached, cache_status = None, "ERROR"
            if cached:
                result = cached.model_copy(
                    update={"input_tokens": None, "output_tokens": None, "usage_source": "UNKNOWN"}
                )
                latency, cost, cost_status = None, Decimal(0), "CACHE_NO_API_SPEND"
            else:
                if not circuit.admit():
                    attempted.append(
                        {
                            "provider": spec.provider,
                            "error": "UNAVAILABLE",
                            "invoked": False,
                            "reason": "CIRCUIT_OPEN",
                        }
                    )
                    continue
                if not self.budget.reserve(session, call, spec, owned, datetime.now(UTC)):
                    circuit.cancel()
                    attempted.append(
                        {"provider": spec.provider, "error": "BUDGET_BLOCKED", "invoked": False}
                    )
                    if "BUDGET_DOWNGRADE" not in decision.reason_codes:
                        decision.reason_codes.append("BUDGET_DOWNGRADE")
                    decision.budget_decision = "DOWNGRADE"
                    session.commit()
                    continue
                session.commit()  # Reservation is durable before the provider can incur spend.
                start = time.perf_counter()
                try:
                    result = asyncio.run(provider.generate(owned.model_copy(deep=True)))
                    result = validate_result(owned, result, spec)
                    latency = round((time.perf_counter() - start) * 1000, 3)
                    if spec.kind == "FIXTURE":
                        cost, cost_status = Decimal(0), "FIXTURE_ZERO_API_SPEND"
                    elif not requires_budget(spec):
                        cost, cost_status = None, "LOCAL_COMPUTE_NOT_PRICED"
                    elif spec.price and result.input_tokens is not None:
                        cost = (
                            Decimal(result.input_tokens) * spec.price.input_cost_per_million
                            + Decimal(result.output_tokens) * spec.price.output_cost_per_million
                        ) / Decimal(1_000_000)
                        cost_status = "CONFIGURED_ESTIMATE"
                    else:
                        cost, cost_status = None, "COST_UNKNOWN"
                    self.budget.settle(session, call, cost)
                    session.commit()
                    circuit.success()
                except Exception as error:
                    code = (
                        error.code
                        if isinstance(error, ProviderFailure)
                        else "INVALID_RESPONSE"
                        if isinstance(error, (ValidationError, ValueError))
                        else "UNKNOWN_PROVIDER_ERROR"
                    )
                    attempted.append(
                        {
                            "provider": spec.provider,
                            "model": spec.model,
                            "error": code,
                            "invoked": True,
                            "latency_ms": round((time.perf_counter() - start) * 1000, 3),
                        }
                    )
                    self.budget.settle(session, call)
                    call.attempts = list(attempted)
                    session.commit()
                    circuit.failure()
                    if hasattr(provider, "invalidate_health"):
                        provider.invalidate_health()
                    continue
                if decision.cache_eligible and not self.cache.put(cache_key, result):
                    cache_status = "ERROR"
            decision.selected_provider, decision.selected_model = spec.provider, spec.model
            decision.selected_tier = (
                "FIXTURE"
                if spec.kind == "FIXTURE"
                else "REASONING"
                if owned.complexity == "REASONING"
                else spec.tiers[0]
            )
            fallback = bool(attempted) or "FIXTURE_FALLBACK" in decision.reason_codes
            if attempted:
                decision.reason_codes.append("FALLBACK_USED")
            if cache_status == "HIT":
                decision.reason_codes.append("CACHE_HIT")
            response = ModelResponse(
                request_id=owned.request_id,
                task_id=owned.task_id,
                trace_id=owned.trace_id,
                provider=spec.provider,
                model=spec.model,
                route_tier=decision.selected_tier,
                output=result.output,
                finish_reason=result.finish_reason,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                total_tokens=(result.input_tokens + result.output_tokens)
                if result.input_tokens is not None
                else None,
                latency_ms=latency,
                usage_source=result.usage_source,
                estimated_cost_usd=cost,
                cost_status=cost_status,
                cache_status=cache_status,
                fallback_used=fallback,
                status="DONE",
                safe_error=None,
                decision=decision,
                mode=owned.mode,
            )
            attempted.append(
                {
                    "provider": spec.provider,
                    "model": spec.model,
                    "status": "DONE",
                    "invoked": cache_status != "HIT",
                    "cache": cache_status,
                }
            )
            break
        else:
            response.safe_error = (
                "BUDGET_BLOCKED"
                if any(a.get("error") == "BUDGET_BLOCKED" for a in attempted)
                or "BUDGET_BLOCKED" in decision.reason_codes
                else "POLICY_BLOCKED"
                if not candidates
                else "UNAVAILABLE"
            )
        call.status = response.status
        call.provider, call.model, call.tier = (
            response.provider,
            response.model,
            response.route_tier,
        )
        call.routing_decision = decision.model_dump(mode="json")
        call.attempts = attempted
        # Store accounting/decision only; not prompts or generated content. Cache is transient.
        call.response_metadata = response.model_copy(update={"output": None}).model_dump(
            mode="json"
        )
        call.safe_error, call.completed_at = response.safe_error, datetime.now(UTC)
        session.commit()
        logger.info(
            "model_request_complete",
            extra={
                "trace_id": str(request.trace_id),
                "task_id": str(request.task_id),
                "correlation_id": correlation_id,
            },
        )
        return response


def recover_model_calls():
    from app.database import SessionLocal

    with SessionLocal.begin() as session:
        calls = session.scalars(
            select(ModelCall).where(ModelCall.status == "RUNNING").with_for_update()
        ).all()
        for call in calls:
            BudgetPolicy().settle(session, call)
            call.status, call.safe_error = "FAILED", "APPLICATION_RESTARTED"
            call.completed_at = datetime.now(UTC)
