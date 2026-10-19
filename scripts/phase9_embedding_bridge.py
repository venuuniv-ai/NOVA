"""Explicit operator-run CPU bridge; never downloads or starts on application import."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODEL = "bge-small-en-v1.5"
FINGERPRINT = "3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad"


def validate_request(body):
    if not isinstance(body, dict) or set(body) - {"model", "input", "dimensions"}:
        raise ValueError("INVALID_INPUT")
    texts = body.get("input")
    texts = [texts] if isinstance(texts, str) else texts
    if (
        body.get("model") != MODEL
        or body.get("dimensions", 384) != 384
        or not isinstance(texts, list)
        or len(texts) != 1
        or not isinstance(texts[0], str)
        or not texts[0].strip()
        or len(texts[0].encode()) > 1000
    ):
        raise ValueError("INVALID_INPUT")
    return texts


def serve(model_dir):
    # Offline flags are mandatory even when the operator supplies a local directory.
    for key in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_HUB_DISABLE_TELEMETRY"):
        if os.environ.get(key) != "1":
            raise RuntimeError("OFFLINE_FLAGS_REQUIRED")
    artifact = model_dir / "model.safetensors"
    if artifact.is_symlink():
        raise RuntimeError("ARTIFACT_MISMATCH")
    with artifact.open("rb") as stream:
        fingerprint = hashlib.file_digest(stream, "sha256").hexdigest()
    if fingerprint != FINGERPRINT:
        raise RuntimeError("ARTIFACT_MISMATCH")
    start = time.monotonic()
    import torch
    from transformers import AutoModel, AutoTokenizer

    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True, trust_remote_code=False)
    model = AutoModel.from_pretrained(
        model_dir, local_files_only=True, trust_remote_code=False, use_safetensors=True
    ).to(device="cpu", dtype=torch.float32).eval()
    if model.config.hidden_size != 384 or torch.get_num_threads() != 2:
        raise RuntimeError("RUNTIME_LIMIT_MISMATCH")
    slot = threading.BoundedSemaphore(1)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def setup(self):
            super().setup()
            self.connection.settimeout(8)

        def reply(self, status, data):
            raw = json.dumps(data, allow_nan=False).encode()
            if len(raw) > 65536:
                raise ValueError("OUTPUT_LIMIT")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            if self.path == "/v1/models":
                self.reply(200, {"data": [{"id": MODEL}]})
            else:
                self.reply(404, {"error": "NOT_FOUND"})

        def do_POST(self):
            if self.path != "/v1/embeddings":
                return self.reply(404, {"error": "NOT_FOUND"})
            if not slot.acquire(blocking=False):
                return self.reply(429, {"error": "BUSY"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if self.headers.get("Transfer-Encoding") or not 0 < length <= 32768:
                    raise ValueError("INPUT_LIMIT")
                texts = validate_request(json.loads(self.rfile.read(length)))
                encoded = tokenizer(texts, return_tensors="pt", truncation=False)
                if encoded["input_ids"].shape[1] > 128:
                    raise ValueError("TOKEN_LIMIT")
                with torch.inference_mode():
                    vector = torch.nn.functional.normalize(
                        model(**encoded).last_hidden_state[:, 0], p=2, dim=1
                    )[0]
                if vector.shape != (384,) or not torch.isfinite(vector).all() or vector.norm() <= 0:
                    raise ValueError("VECTOR_INVALID")
                self.reply(200, {"model": MODEL, "data": [{"index": 0, "embedding": vector.tolist()}]})
            except (ValueError, TypeError, KeyError):
                self.reply(422, {"error": "INVALID_INPUT"})
            finally:
                slot.release()

    server = ThreadingHTTPServer(("127.0.0.1", 11435), Handler)
    server.daemon_threads = True
    print(
        json.dumps(
            {
                "state": "READY",
                "load_seconds": time.monotonic() - start,
                "torch": torch.__version__,
                "cpu_threads": torch.get_num_threads(),
                "dimension": 384,
                "backend": "CPU_FLOAT32",
            }
        ),
        flush=True,
    )
    server.serve_forever(poll_interval=0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    args = parser.parse_args()
    serve(args.model_dir.resolve(strict=True))
