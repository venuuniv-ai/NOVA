"""Explicit local operator residency controller; no model downloads or application authority."""

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import signal
import socket
import subprocess
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

QWEN_OUTPUT_LIMITS = {"nova-qwen-phase9": 32, "nova-qwen-phase9-rag96": 96}


def generation_port(body):
    """Only the two operator-approved immutable text profiles; no runtime overrides."""
    limit = QWEN_OUTPUT_LIMITS.get(body.get("model"))
    allowed = {"model", "messages", "temperature", "max_tokens", "stream", "response_format"}
    if (
        limit is None
        or set(body) - allowed
        or type(body.get("max_tokens")) is not int
        or not 16 <= body["max_tokens"] <= limit
        or type(body.get("temperature")) not in {int, float}
        or body["temperature"] != 0
        or body.get("stream") is not False
    ):
        raise ValueError("GENERATION_LIMIT")
    return 11434


class Residency:
    def __init__(self, start, stop, resource, clock=time.monotonic):
        self.start, self.stop, self.resource, self.clock = start, stop, resource, clock
        self.lock = threading.Lock()
        self.inference_lock = threading.Lock()
        self.model = self.token = None
        self.expires = 0
        self.poisoned = False

    def acquire(self, model):
        if not self.lock.acquire(blocking=False):
            raise RuntimeError("BUSY")
        if self.poisoned or self.model or self.inference_lock.locked():
            self.lock.release()
            raise RuntimeError("RESIDENCY_UNAVAILABLE")
        try:
            self.resource()
            self.model = model
            self.expires = self.clock() + 60
            self.start(model)
            self.token = secrets.token_hex(32)
            return self.token
        except BaseException:
            self._stop()
            raise
        finally:
            self.lock.release()

    def _stop(self):
        try:
            self.stop()
        except BaseException:
            self.poisoned = True
            raise
        finally:
            self.model = self.token = None
            self.expires = 0

    def release(self, token):
        with self.lock:
            if self.token and not hmac.compare_digest(self.token, token):
                raise RuntimeError("LEASE_INVALID")
            self._stop()

    def check(self, token, model):
        if (
            self.poisoned
            or not self.token
            or self.model != model
            or not hmac.compare_digest(self.token, token)
            or self.clock() >= self.expires
        ):
            raise RuntimeError("LEASE_INVALID")

    def reap(self):
        if self.lock.acquire(blocking=False):
            try:
                if self.model and self.clock() >= self.expires:
                    self._stop()
            finally:
                self.lock.release()

    def infer(self, token, model, invoke):
        # A duplicated private lease cannot enqueue a second request at the runtime.
        if not self.inference_lock.acquire(blocking=False):
            raise RuntimeError("BUSY")
        try:
            with self.lock:
                self.check(token, model)
                try:
                    self.resource()
                except Exception:
                    self._stop()
                    raise
            result = invoke()
            with self.lock:
                self.check(token, model)
            return result
        finally:
            self.inference_lock.release()


def processes(root):
    rows = [
        tuple(map(int, x.split()))
        for x in subprocess.check_output(["ps", "-axo", "pid=,ppid=,rss="], text=True).splitlines()
    ]
    ids = {root}
    while True:
        found = ids | {pid for pid, parent, _ in rows if parent in ids}
        if found == ids:
            return ids, sum(rss * 1024 for pid, _, rss in rows if pid in ids)
        ids = found


class Runtime:
    def __init__(self, root, evidence):
        self.root, self.evidence = root, evidence
        self.process = None
        self.ids = set()
        self.model = None
        self.peak = None
        self.records = []
        self.failed = None
        self.request_deadline = None
        self.last_resources = None
        self.record_lock = threading.Lock()
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def persist(self):
        # Write transitions before/after inference, not only after successful unload.
        with self.record_lock:
            target = self.evidence / "residency.json"
            temporary = target.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(self.records, indent=2))
            temporary.replace(target)

    def resources(self):
        import shutil

        swap = float(
            re.search(
                r"used = ([\d.]+)M", subprocess.check_output(["sysctl", "vm.swapusage"], text=True)
            )[1]
        )
        free = shutil.disk_usage(self.root).free
        self.last_resources = {
            "swap_mib": swap,
            "free_disk_bytes": free,
            "measured_at": time.time(),
        }
        if swap >= 2048 or free < 5 * 1024**3:
            raise RuntimeError("RESOURCE_GATE")
        return self.last_resources

    def request(self, port, path, body=None, timeout=1):
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}" + path,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Content-Type": "application/json"},
        )
        with self.opener.open(req, timeout=timeout) as response:
            data = response.read(65537)
            if len(data) > 65536:
                raise RuntimeError("RESPONSE_LIMIT")
            return json.loads(data)

    def start(self, model):
        if model != "bge-small-en-v1.5" and model not in QWEN_OUTPUT_LIMITS:
            raise RuntimeError("MODEL_INVALID")
        self.failed = None
        for port in (11434, 11435):
            with socket.socket() as sock:
                if sock.connect_ex(("127.0.0.1", port)) == 0:
                    raise RuntimeError("UNOWNED_RUNTIME_PRESENT")
        self.model, self.peak = model, None
        before = self.resources()
        self.records.append(
            {"model": model, "before": before, "started_at": time.time(), "state": "STARTING"}
        )
        self.persist()
        artifact = (
            self.root / ".local/phase9/models/bge-small-en-v1.5/model.safetensors"
            if model == "bge-small-en-v1.5"
            else Path.home()
            / ".ollama/models/blobs"
            / "sha256-183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4"
        )
        expected = (
            "3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad"
            if model == "bge-small-en-v1.5"
            else "183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4"
        )
        with artifact.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != expected:
                raise RuntimeError("ARTIFACT_MISMATCH")
        if model in QWEN_OUTPUT_LIMITS:
            manifest = json.loads(
                (
                    Path.home()
                    / f".ollama/models/manifests/registry.ollama.ai/library/{model}/latest"
                ).read_text()
            )
            if not any(layer.get("digest") == "sha256:" + expected for layer in manifest["layers"]):
                raise RuntimeError("ALIAS_ARTIFACT_MISMATCH")
        env = {
            **os.environ,
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "HF_HUB_DISABLE_TELEMETRY": "1",
            "TOKENIZERS_PARALLELISM": "false",
            "OMP_NUM_THREADS": "2",
            "VECLIB_MAXIMUM_THREADS": "2",
            "OLLAMA_HOST": "127.0.0.1:11434",
            "OLLAMA_NO_CLOUD": "1",
            "OLLAMA_MAX_LOADED_MODELS": "1",
            "OLLAMA_NUM_PARALLEL": "1",
            "OLLAMA_MAX_QUEUE": "1",
            "OLLAMA_KEEP_ALIVE": "0",
        }
        command = ["ollama", "serve"]
        if model == "bge-small-en-v1.5":
            command = [
                str(self.root / ".local/phase9/embedding-venv/bin/python"),
                "-u",
                str(self.root / "scripts/phase9_embedding_bridge.py"),
                "--model-dir",
                str(artifact.parent),
            ]
        log = open(self.evidence / (model + ".log"), "a")
        try:
            self.process = subprocess.Popen(
                ["sandbox-exec", "-f", str(self.root / ".local/phase9/loopback-only.sb"), *command],
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        finally:
            log.close()
        started = time.monotonic()
        while time.monotonic() - started < 30:
            self.monitor()
            if self.process.poll() is not None:
                raise RuntimeError("RUNTIME_EXIT")
            try:
                if model == "bge-small-en-v1.5":
                    data = self.request(11435, "/v1/models")
                    if data["data"][0]["id"] != model:
                        raise RuntimeError("MODEL_MISMATCH")
                else:
                    self.request(11434, "/api/version")
                    show = self.request(11434, "/api/show", {"model": model})
                    for key, value in {
                        "num_ctx": 512,
                        "num_predict": QWEN_OUTPUT_LIMITS[model],
                        "num_thread": 2,
                        "num_gpu": 0,
                        "temperature": 0,
                    }.items():
                        match = re.search(r"^" + key + r"\s+([\d.]+)\s*$", show["parameters"], re.M)
                        if not match or float(match[1]) != value:
                            raise RuntimeError("RUNTIME_LIMIT_INVALID")
                self.records[-1].update(
                    state="READY", ready_at=time.time(), load_seconds=time.monotonic() - started
                )
            except (OSError, TimeoutError):
                time.sleep(0.05)
                continue
            self.persist()
            return
        raise RuntimeError("STARTUP_TIMEOUT")

    def monitor(self):
        try:
            self.resources()
        except RuntimeError:
            if self.records:
                self.records[-1].update(
                    resource_refused_at=time.time(), last_resources=self.last_resources
                )
                self.persist()
            raise
        if self.request_deadline is not None and time.monotonic() >= self.request_deadline:
            raise RuntimeError("INFERENCE_DEADLINE")
        if self.failed:
            raise RuntimeError(self.failed)
        if self.process:
            ids, rss = processes(self.process.pid)
            self.ids.update(ids)
            self.peak = max(self.peak or 0, rss)
            limit = 1024 if self.model == "bge-small-en-v1.5" else 2048
            if rss > limit * 1024**2:
                raise RuntimeError("MEMORY_LIMIT")

    def stop(self):
        self.request_deadline = None
        if not self.process:
            return
        started = time.monotonic()
        # Native Qwen keep_alive=0 plus server/descendant termination; never delete models.
        if self.model in QWEN_OUTPUT_LIMITS and self.process.poll() is None:
            try:
                self.request(
                    11434,
                    "/api/generate",
                    {"model": self.model, "keep_alive": 0, "stream": False},
                    timeout=1,
                )
            except (OSError, TimeoutError):
                pass
        self.ids.update(processes(self.process.pid)[0])
        for pid in self.ids:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        try:
            self.process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            os.killpg(self.process.pid, signal.SIGKILL)
            self.process.wait(timeout=1)
        for pid in self.ids:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 1
        remaining = set(self.ids)
        while remaining and time.monotonic() < deadline:
            live = {
                int(line.split()[0])
                for line in subprocess.check_output(
                    ["ps", "-axo", "pid=,stat="], text=True
                ).splitlines()
                if "Z" not in line.split()[1]
            }
            remaining &= live
            if remaining:
                time.sleep(0.05)
        listeners = []
        for port in (11434, 11435):
            with socket.socket() as sock:
                if sock.connect_ex(("127.0.0.1", port)) == 0:
                    listeners.append(port)
        resource_error = None
        try:
            after = self.resources()
        except Exception as error:
            # Unsafe/missing measurements must not skip cleanup or erase evidence.
            resource_error, after = error, self.last_resources
        self.records[-1].update(
            peak_rss_bytes=self.peak,
            stopped=not remaining and not listeners,
            shutdown_seconds=time.monotonic() - started,
            stopped_at=time.time(),
            after=after,
            after_resource_error="RESOURCE_CHECK_FAILED" if resource_error else None,
        )
        try:
            self.persist()
        finally:
            self.process, self.model, self.ids = None, None, set()
        if remaining or listeners:
            raise RuntimeError("TERMINATION_UNVERIFIED")
        if resource_error:
            raise resource_error


def serve(root, key_path, evidence=None):
    evidence = evidence or root / ".local/phase9/integration"
    evidence.mkdir(parents=True, exist_ok=True)
    runtime = Runtime(root, evidence)
    coordinator = Residency(runtime.start, runtime.stop, runtime.resources)
    key = key_path.read_text().strip()
    if len(key) < 32:
        raise RuntimeError("PRIVATE_KEY_REQUIRED")
    finished = threading.Event()

    def watchdog():
        while not finished.wait(0.1):
            try:
                if runtime.process:
                    runtime.monitor()
                coordinator.reap()
            except Exception:
                runtime.failed = "WATCHDOG_REFUSAL"
                try:
                    coordinator.release(coordinator.token or "")
                except Exception:
                    coordinator.poisoned = True

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def reply(self, code, data):
            raw = json.dumps(data).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_POST(self):
            self.connection.settimeout(8)
            if not hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + key):
                return self.reply(401, {"error": "UNAUTHORIZED"})
            try:
                n = int(self.headers.get("Content-Length", "0"))
                if not 0 < n <= 32768 or self.headers.get("Transfer-Encoding"):
                    raise ValueError("BODY_LIMIT")
                body = json.loads(self.rfile.read(n))
                if self.path == "/acquire":
                    token = coordinator.acquire(body["model"])
                    try:
                        return self.reply(200, {"lease": token})
                    except (OSError, TimeoutError):
                        coordinator.release(token)
                        raise
                if self.path == "/release":
                    coordinator.release(body["lease"])
                    return self.reply(200, {"stopped": True})
                model = body.get("model")
                if self.path == "/v1/embeddings" and model == "bge-small-en-v1.5":
                    port = 11435
                elif self.path == "/v1/chat/completions":
                    port = generation_port(body)
                else:
                    raise ValueError("ROUTE_INVALID")

                def invoke():
                    runtime.monitor()  # Refuse changed resources before transport/loading.
                    runtime.request_deadline = time.monotonic() + 8
                    try:
                        started = time.monotonic()
                        runtime.records[-1]["inference_started_at"] = time.time()
                        runtime.persist()
                        result = runtime.request(port, self.path, body, timeout=8)
                        record = runtime.records[-1]
                        record["inference_seconds"] = time.monotonic() - started
                        record["inference_finished_at"] = time.time()
                        usage = result.get("usage", {})
                        record["reported_usage"] = {
                            k: usage[k]
                            for k in ("prompt_tokens", "completion_tokens", "total_tokens")
                            if type(usage.get(k)) is int and 0 <= usage[k] <= 131072
                        }
                        runtime.persist()
                        return result
                    finally:
                        runtime.request_deadline = None

                data = coordinator.infer(self.headers.get("X-Nova-Lease", ""), model, invoke)
                return self.reply(200, data)
            except Exception:
                # Fixed error only; never expose paths, keys or provider body.
                return self.reply(409, {"error": "RESIDENCY_REFUSED"})

        def do_GET(self):
            if not hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + key):
                return self.reply(401, {"error": "UNAUTHORIZED"})
            if self.path != "/v1/models":
                return self.reply(404, {"error": "NOT_FOUND"})
            return self.reply(
                200, {"data": [{"id": x} for x in ["bge-small-en-v1.5", *QWEN_OUTPUT_LIMITS]]}
            )

    thread = threading.Thread(target=watchdog, daemon=True)
    server = ThreadingHTTPServer(("127.0.0.1", 11436), Handler)
    thread.start()

    def terminate(*_args):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, terminate)
    try:
        server.serve_forever(poll_interval=0.1)
    finally:
        finished.set()
        coordinator.release(coordinator.token or "")
        server.server_close()
        thread.join(timeout=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key-file", type=Path, required=True)
    parser.add_argument("--evidence-directory", type=Path)
    args = parser.parse_args()
    serve(Path(__file__).resolve().parents[1], args.key_file, args.evidence_directory)
