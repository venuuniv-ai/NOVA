import asyncio
import json
import threading
import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from urllib.parse import urlparse

import httpx
from pydantic import ValidationError

from app.intelligence.contracts import AgentInput, ContextOutput, CriticOutput, PlanOutput
from app.intelligence.provider import FixtureModelProvider
from app.model_routing.contracts import ModelRequest, ProviderResult, ProviderSpec, TextOutput
from app.proactive.contracts import Attendee, CommunicationInput, CommunicationOutput


class ProviderFailure(Exception):
    def __init__(self, code):
        allowed = {
            "TIMEOUT",
            "UNAVAILABLE",
            "RATE_LIMITED",
            "INVALID_RESPONSE",
            "CONTEXT_LIMIT",
            "AUTH_ERROR",
            "BUDGET_BLOCKED",
            "POLICY_BLOCKED",
            "UNKNOWN_PROVIDER_ERROR",
        }
        self.code = code if code in allowed else "UNKNOWN_PROVIDER_ERROR"
        super().__init__(self.code)


def output_schema(purpose):
    if purpose == "VISUAL_CONTEXT":
        from app.perception.contracts import VisionOutput

        return VisionOutput
    return {
        "SUMMARY": TextOutput,
        "PLANNING": PlanOutput,
        "CRITIQUE": CriticOutput,
        "CONTEXT": ContextOutput,
        "COMMUNICATION": CommunicationOutput,
    }[purpose]


def validate_result(request, result, spec):
    result = ProviderResult.model_validate(result)
    if len(json.dumps(result.output).encode()) > 65536:
        raise ProviderFailure("INVALID_RESPONSE")
    validated = output_schema(request.purpose).model_validate(result.output)
    if result.input_tokens is not None and (
        result.input_tokens > spec.input_token_limit
        or result.output_tokens > request.max_output_tokens
    ):
        raise ProviderFailure("INVALID_RESPONSE")
    return result.model_copy(update={"output": validated.model_dump(mode="json")})


class InferenceProvider(ABC):
    spec: ProviderSpec

    @abstractmethod
    async def generate(self, request: ModelRequest) -> ProviderResult: ...

    def available(self):
        return self.spec.enabled

    def health(self):
        return {"state": "AVAILABLE" if self.available() else "DISABLED", "last_checked": None}


class FixtureInferenceProvider(InferenceProvider):
    spec = ProviderSpec(
        provider="fixture",
        model="nova-demo-v1",
        kind="FIXTURE",
        tiers=["FIXTURE"],
        capabilities=["TEXT", "STRUCTURED", "REASONING_REPLAY"],
        enabled=True,
        strength=0,
        latency_class="FAST",
    )

    async def generate(self, request):
        fixture = FixtureModelProvider()
        if request.purpose == "SUMMARY":
            reasoning = request.complexity == "REASONING"
            output = TextOutput(
                summary=(
                    "Deterministic replay: review meeting, travel and explicit "
                    "preference constraints; no real reasoning model was invoked."
                    if reasoning
                    else (
                        "Deterministic replay: tomorrow includes the synthetic Product Review, "
                        "4–5 PM, Downtown. No live calendar or LLM was used."
                    )
                )
            )
        elif request.purpose == "COMMUNICATION":
            payload = CommunicationInput.model_validate(request.structured_input["communication"])
            attendee = Attendee.model_validate(request.structured_input["attendee"])
            response = await fixture.generate_communication(payload, attendee)
            output = CommunicationOutput.model_validate_json(response.payload_json)
        else:
            payload = AgentInput.model_validate(request.structured_input["agent_input"])
            agent = {"PLANNING": "PLANNER", "CRITIQUE": "CRITIC", "CONTEXT": "CONTEXT"}[
                request.purpose
            ]
            response = await fixture.generate_structured(agent, payload)
            output = output_schema(request.purpose).model_validate_json(response.payload_json)
        return ProviderResult(output=output.model_dump(mode="json"), finish_reason="fixture")


def validate_local_url(url):
    parsed = urlparse(url)
    import ipaddress

    try:
        loopback = ipaddress.ip_address(parsed.hostname or "").is_loopback
    except ValueError:
        loopback = False
    if (
        parsed.scheme not in {"http", "https"}
        or not (loopback or parsed.hostname in {"localhost", "host.docker.internal"})
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path.rstrip("/") not in {"", "/v1"}
    ):
        raise ValueError(
            "Local endpoint must be server-configured loopback or Docker host "
            "/v1, without URL credentials."
        )
    _ = parsed.port
    return url.rstrip("/")


class LocalOpenAICompatibleProvider(InferenceProvider):
    def __init__(
        self,
        enabled=False,
        base_url="http://host.docker.internal:11434/v1",
        model="",
        capabilities=None,
        timeout=8,
        api_key=None,
        transport=None,
    ):
        self.url = validate_local_url(base_url)
        self.timeout, self.api_key, self.transport = timeout, api_key, transport
        if any(marker in model.casefold() for marker in [":cloud", "-cloud"]):
            raise ValueError("Cloud-backed model identifiers are not eligible local inference.")
        self.spec = ProviderSpec(
            provider="local",
            model=model or "NOT_CONFIGURED",
            kind="LOCAL",
            tiers=["LOCAL", "SMALL"],
            capabilities=capabilities or ["TEXT", "STRUCTURED"],
            enabled=enabled and bool(model),
            strength=5,
        )
        self._state = "DISABLED" if not self.spec.enabled else "UNAVAILABLE"
        self._checked = None
        self._next_check = 0.0
        self._lock = threading.Lock()

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def health(self):
        if not self.spec.enabled:
            return {"state": "DISABLED", "last_checked": None}
        with self._lock:
            if time.monotonic() >= self._next_check:
                self._next_check = time.monotonic() + 60
                self._checked = datetime.now(UTC).isoformat()
                try:
                    deadline = time.monotonic() + min(self.timeout, 2)
                    with httpx.Client(
                        timeout=min(self.timeout, 2),
                        trust_env=False,
                        follow_redirects=False,
                        transport=self.transport,
                    ) as client:
                        with client.stream(
                            "GET", self.url + "/models", headers=self._headers()
                        ) as response:
                            if response.status_code != 200:
                                raise ProviderFailure("UNAVAILABLE")
                            raw = read_bounded(response, deadline=deadline)
                    entries = json.loads(raw).get("data", [])
                    self._state = (
                        "AVAILABLE"
                        if any(item.get("id") == self.spec.model for item in entries)
                        else "UNAVAILABLE"
                    )
                except Exception:
                    self._state = "UNAVAILABLE"
        return {"state": self._state, "last_checked": self._checked}

    def available(self):
        return self.health()["state"] == "AVAILABLE"

    def invalidate_health(self):
        with self._lock:
            self._state = "DEGRADED"
            # Do not immediately probe a failed endpoint again.
            self._next_check = max(self._next_check, time.monotonic() + 30)

    async def generate(self, request):
        if not self.spec.enabled:
            raise ProviderFailure("UNAVAILABLE")
        schema = output_schema(request.purpose)
        body = {
            "model": self.spec.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return only JSON matching this application schema. "
                        "Do not add routing, privacy, approval, execution or pricing fields. "
                        "Schema: "
                    )
                    + json.dumps(schema.model_json_schema()),
                },
                {
                    "role": "user",
                    "content": json.dumps(request.structured_input, ensure_ascii=False),
                },
            ],
            "temperature": 0,
            "max_tokens": request.max_output_tokens,
            "stream": False,
            "response_format": {"type": "json_object"},
        }
        if len(json.dumps(body).encode()) > self.spec.input_token_limit:
            raise ProviderFailure("CONTEXT_LIMIT")
        try:
            # Use a bounded sync transport off the event loop; no vendor SDK or model install.
            def call():
                deadline = time.monotonic() + self.timeout
                with httpx.Client(
                    timeout=self.timeout,
                    trust_env=False,
                    follow_redirects=False,
                    transport=self.transport,
                ) as client:
                    with client.stream(
                        "POST", self.url + "/chat/completions", json=body, headers=self._headers()
                    ) as response:
                        if response.status_code != 200:
                            code = {
                                401: "AUTH_ERROR",
                                403: "AUTH_ERROR",
                                429: "RATE_LIMITED",
                                413: "CONTEXT_LIMIT",
                                503: "UNAVAILABLE",
                            }.get(response.status_code, "UNAVAILABLE")
                            raise ProviderFailure(code)
                        return read_bounded(response, deadline=deadline)

            data = json.loads(await asyncio.to_thread(call))
            if data.get("model") != self.spec.model:
                raise ProviderFailure("INVALID_RESPONSE")
            choices = data["choices"]
            if len(choices) != 1 or choices[0]["message"].get("role", "assistant") != "assistant":
                raise ProviderFailure("INVALID_RESPONSE")
            output = schema.model_validate_json(choices[0]["message"]["content"])
            usage = data.get("usage")
            result = ProviderResult(
                output=output.model_dump(mode="json"),
                finish_reason=choices[0]["finish_reason"],
                input_tokens=usage.get("prompt_tokens") if usage else None,
                output_tokens=usage.get("completion_tokens") if usage else None,
                usage_source="PROVIDER_REPORTED" if usage else "UNKNOWN",
            )
            if usage and usage.get("total_tokens") != result.input_tokens + result.output_tokens:
                raise ProviderFailure("INVALID_RESPONSE")
            return validate_result(request, result, self.spec)
        except httpx.TimeoutException:
            raise ProviderFailure("TIMEOUT") from None
        except ProviderFailure:
            raise
        except httpx.HTTPError:
            raise ProviderFailure("UNAVAILABLE") from None
        except (ValueError, KeyError, TypeError, ValidationError):
            raise ProviderFailure("INVALID_RESPONSE") from None
        except Exception:
            raise ProviderFailure("UNKNOWN_PROVIDER_ERROR") from None


def read_bounded(response, deadline=None):
    deadline = deadline if deadline is not None else time.monotonic() + 30
    if time.monotonic() >= deadline:
        raise ProviderFailure("TIMEOUT")
    chunks = bytearray()
    for chunk in response.iter_bytes():
        if time.monotonic() >= deadline:
            raise ProviderFailure("TIMEOUT")
        chunks.extend(chunk)
        if len(chunks) > 65536:
            raise ProviderFailure("INVALID_RESPONSE")
    return bytes(chunks)
