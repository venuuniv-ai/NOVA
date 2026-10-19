"""Private server config only; metadata never exposes filesystem paths/endpoints."""

import hashlib
import os
import shutil
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field

from app.intelligence.contracts import Contract
from app.model_routing.providers import validate_local_url


class ModelConfig(Contract):
    model_id: str = Field(max_length=80, pattern=r"^[a-zA-Z0-9_.:-]+$")
    runtime: Literal["OPENAI_COMPATIBLE"] = "OPENAI_COMPATIBLE"
    base_url: str = "http://host.docker.internal:11434/v1"
    capabilities: list[Literal["TEXT", "STRUCTURED", "EMBED", "VISION"]] = Field(max_length=4)
    fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    artifact_path: str = ""
    license: str = Field(min_length=1, max_length=80)
    version: str = Field(max_length=40, pattern=r"^[a-zA-Z0-9_.-]+$")
    dimension: int | None = Field(default=None, ge=1, le=2000)
    context_window: int | None = Field(default=None, ge=128, le=131072)
    quantization: str | None = Field(default=None, max_length=40)
    estimated_memory_mib: int = Field(ge=1, le=2048)
    resource_approved: bool = False
    managed_residency: bool = False
    grounded_budget_profile: Literal["QWEN2_CHATML_0351"] | None = None
    grounded_generation_contract: Literal["EXTRACTIVE_V1", "SELECTION_V1"] = "EXTRACTIVE_V1"
    backend: str = Field(default="CPU", max_length=40)

    def public(self):
        return self.model_dump(
            exclude={
                "base_url",
                "artifact_path",
                "resource_approved",
                "managed_residency",
                "grounded_budget_profile",
                "grounded_generation_contract",
            }
        )


def configuration(capability=None):
    key = "INFERENCE_EMBEDDING_CONFIG_FILE" if capability == "EMBED" else "INFERENCE_CONFIG_FILE"
    location = os.environ.get(key, "")
    if not location:
        return None
    path = Path(location)
    if path.stat().st_size > 16000:
        raise ValueError("CONFIG_INVALID")
    spec = ModelConfig.model_validate_json(path.read_text())
    validate_local_url(spec.base_url)
    artifact = Path(spec.artifact_path)
    if not spec.artifact_path or not artifact.is_file() or artifact.is_symlink():
        raise ValueError("MODEL_MISSING")
    stat = artifact.stat()
    if (
        stat.st_size > 2 * 1024**3
        or verified_artifact(str(artifact), stat.st_size, stat.st_mtime_ns) != spec.fingerprint
    ):
        raise ValueError("ARTIFACT_MISMATCH")
    if any(x in spec.model_id.casefold() for x in [":cloud", "-cloud"]):
        raise ValueError("CONFIG_INVALID")
    return spec


@lru_cache(maxsize=4)
def verified_artifact(path, size, mtime_ns):
    # Read-only, bounded local artifact verification; no model loader or downloads.
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resource_gate():
    """Container checks plus explicit fresh host attestation; never guess host from cgroups."""
    disk = shutil.disk_usage(os.environ.get("INFERENCE_RESOURCE_PATH", "/tmp")).free
    # Operator records host preflight privately. Missing/stale attestation fails closed.
    import time

    attested = float(os.environ.get("INFERENCE_HOST_PREFLIGHT_AT", "0"))
    swap = float(os.environ.get("INFERENCE_HOST_SWAP_MIB", "inf"))
    host_disk = float(os.environ.get("INFERENCE_HOST_FREE_GIB", "0"))
    ready = time.time() - 3600 < attested <= time.time() and swap < 2048 and host_disk >= 5
    return {
        "state": "AVAILABLE" if ready and disk >= 5 * 1024**3 else "BLOCKED_BY_RESOURCES",
        "disk_free_bytes": disk,
        "host_preflight_fresh": time.time() - 3600 < attested <= time.time(),
        "policy": "host disk >=5GiB; swap <2GiB; attestation <=1h; one active call",
    }


def inventory():
    try:
        spec = configuration()
    except (ValueError, OSError):
        spec = None
    result = {
        "mode_default": "FIXTURE",
        "resources": resource_gate(),
        "models": [
            {
                "model_id": "fixture-token-hash-v1",
                "status": "AVAILABLE",
                "simulation": True,
                "evaluated": "FIXTURE_ONLY",
                "capabilities": ["TEXT", "STRUCTURED", "EMBED"],
                "loaded": False,
                "last_health_check": None,
            },
            {
                **(spec.public() if spec else {"model_id": "NOT_CONFIGURED", "capabilities": []}),
                "status": (
                    "CONFIGURED"
                    if resource_gate()["state"] == "AVAILABLE"
                    else "BLOCKED_BY_RESOURCES"
                )
                if spec
                else "NOT_INSTALLED",
                "configured": spec is not None,
                "loaded": False,
                "last_health_check": None,
                "evaluated": "NOT_EVALUATED",
                "simulation": False,
            },
        ],
        "downloads": {
            "automatic": False,
            "approval_required": True,
            "candidate": "BAAI/bge-small-en-v1.5",
            "license": "MIT",
            "estimated_disk_mib": 134,
            "estimated_memory_mib": [300, 1024],
            "source": "https://huggingface.co/BAAI/bge-small-en-v1.5",
        },
    }
    try:
        embedding = configuration("EMBED")
    except (ValueError, OSError):
        embedding = None
    if embedding and (not spec or embedding.model_id != spec.model_id):
        result["models"].append(
            {
                **embedding.public(),
                "status": "CONFIGURED"
                if resource_gate()["state"] == "AVAILABLE"
                else "BLOCKED_BY_RESOURCES",
                "configured": True,
                "loaded": False,
                "last_health_check": None,
                "evaluated": "NOT_EVALUATED",
                "simulation": False,
            }
        )
    return result
