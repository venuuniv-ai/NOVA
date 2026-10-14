import hashlib
import json
import math
import re
import time
from abc import ABC, abstractmethod

import httpx

from app.config import settings
from app.memory.contracts import EmbeddingRequest, EmbeddingResult
from app.model_routing.providers import read_bounded, validate_local_url


class EmbeddingProvider(ABC):
    provider: str
    model: str
    dimension: int
    simulation: bool

    @abstractmethod
    def embed(self, request: EmbeddingRequest) -> EmbeddingResult: ...


class FixtureEmbeddingProvider(EmbeddingProvider):
    provider = "fixture-embedding"
    model = "fixture-token-hash-v1"
    dimension = 32
    simulation = True

    def embed(self, request):
        start = time.perf_counter()
        vector = [0.0] * self.dimension
        words = re.findall(r"[a-z0-9]+", request.text.casefold()) or ["empty"]
        for word in words:
            digest = hashlib.sha256(word.encode()).digest()
            vector[int.from_bytes(digest[:2], "big") % self.dimension] += 1.0
        norm = math.sqrt(sum(x * x for x in vector))
        return EmbeddingResult(
            provider=self.provider,
            model=self.model,
            dimension=self.dimension,
            vector=[x / norm for x in vector],
            simulation=True,
            latency_ms=(time.perf_counter() - start) * 1000,
        )


class LocalEmbeddingProvider(EmbeddingProvider):
    provider = "local-embedding"
    simulation = False

    def __init__(
        self,
        enabled=False,
        base_url="http://localhost:11434/v1",
        model="",
        dimension=32,
        transport=None,
    ):
        self.enabled, self.model, self.dimension, self.transport = (
            enabled,
            model,
            dimension,
            transport,
        )
        self.url = validate_local_url(base_url)
        if any(s in model.casefold() for s in [":cloud", "-cloud"]):
            raise ValueError("Cloud-backed embedding identifiers forbidden.")

    def embed(self, request):
        if not self.enabled or not self.model:
            raise ValueError("REAL EMBEDDING MODEL NOT CONFIGURED")
        start = time.perf_counter()
        with httpx.Client(
            timeout=8, trust_env=False, follow_redirects=False, transport=self.transport
        ) as client:
            with client.stream(
                "POST",
                self.url + "/embeddings",
                json={"model": self.model, "input": request.text, "dimensions": self.dimension},
            ) as response:
                if response.status_code != 200:
                    raise ValueError("EMBEDDING_UNAVAILABLE")
                data = json.loads(read_bounded(response, deadline=time.monotonic() + 8))
        if (
            data.get("model") != self.model
            or len(data.get("data", [])) != 1
            or data["data"][0].get("index") != 0
        ):
            raise ValueError("EMBEDDING_OUTPUT_INVALID")
        return EmbeddingResult(
            provider=self.provider,
            model=self.model,
            dimension=self.dimension,
            vector=data["data"][0]["embedding"],
            simulation=False,
            latency_ms=(time.perf_counter() - start) * 1000,
        )


def embedding_provider():
    if settings.memory_embeddings_enabled:
        return LocalEmbeddingProvider(
            True,
            settings.memory_embedding_base_url,
            settings.memory_embedding_model,
            settings.memory_embedding_dimension,
        )
    return FixtureEmbeddingProvider()
