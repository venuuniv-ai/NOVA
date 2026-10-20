"""NOVA v1.0 local MVP lifecycle. Existing dependencies only; models stay disabled.

Commands: start, status, token, smoke, recover, stop. No build/pull of container
images, dependency install, volume deletion or external action. Native frontend
build uses installed packages. Runtime state is ignored; credentials are private.
"""

import argparse
import fcntl
import hashlib
import json
import os
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from qualify_phase11 import ROOT, allocate_subnets, enforce, occupied_subnets, resource_sample

PROJECT = "nova-v1-local"
SERVICES = [
    "postgres",
    "redis",
    "backend",
    "gateway",
    "kafka",
    "kafka-init",
    "publisher",
    "event-worker",
    "proactive-consumer",
    "audit-consumer",
    "proactive-worker",
]
PORTS = [3000, 5432, 6379, 8000, 8080, 11434, 11435, 11436]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def atomic(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def process_record(process):
    return {
        "pid": process.pid,
        "birth": subprocess.check_output(
            ["ps", "-p", str(process.pid), "-o", "lstart="], text=True
        ).strip(),
    }


def alive(record):
    if not record:
        return False
    result = subprocess.run(
        ["ps", "-p", str(record["pid"]), "-o", "lstart="], text=True, capture_output=True
    )
    return result.returncode == 0 and result.stdout.strip() == record["birth"]


def stop_process(record):
    if not alive(record):
        return
    os.killpg(record["pid"], signal.SIGTERM)
    until = time.monotonic() + 5
    while alive(record) and time.monotonic() < until:
        time.sleep(0.1)
    if alive(record):
        os.killpg(record["pid"], signal.SIGKILL)


def frontend_digest():
    files = []
    for directory in ["app", "components", "lib", "public"]:
        files.extend(p for p in (ROOT / "frontend" / directory).rglob("*") if p.is_file())
    files.extend(
        ROOT / "frontend" / name
        for name in ["package.json", "package-lock.json", "next.config.ts", "tsconfig.json"]
    )
    digest = hashlib.sha256()
    for path in sorted(files):
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def source_files(root=ROOT):
    paths = set()
    for folder in [
        "backend/app",
        "backend/migrations",
        "frontend/app",
        "frontend/components",
        "frontend/lib",
        "frontend/public",
        "scripts",
    ]:
        for path in (root / folder).rglob("*"):
            if (
                path.is_file()
                and "__pycache__" not in path.parts
                and ".ruff_cache" not in path.parts
            ):
                if folder == "frontend/public" or path.suffix in {
                    ".py",
                    ".ts",
                    ".tsx",
                    ".css",
                    ".sh",
                }:
                    if path.is_symlink():
                        raise RuntimeError("SOURCE_SYMLINK_REFUSED")
                    paths.add(str(path.relative_to(root)))
    for name in [
        "compose.yaml",
        "compose.phase8.yaml",
        "backend/Dockerfile",
        "backend/pyproject.toml",
        "backend/requirements.txt",
        "backend/requirements-dev.txt",
        "backend/requirements.lock.txt",
        "frontend/package.json",
        "frontend/package-lock.json",
        "frontend/next.config.ts",
        "frontend/tsconfig.json",
    ]:
        paths.add(name)
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in sorted(paths)}


def verify_sources(root=ROOT):
    manifest = root / "release/local-v1.0.json"
    if not manifest.exists():
        raise RuntimeError("RELEASE_MANIFEST_REQUIRED")
    expected = json.loads(manifest.read_text())["source_sha256"]
    if expected != source_files(root):
        raise RuntimeError("SOURCE_DRIFT; review and requalify the local release candidate")


def validate(config):
    allowed = {
        str(ROOT / p)
        for p in [
            "backend/app",
            "backend/migrations",
            "infrastructure/observability/collector.yaml",
            "infrastructure/observability/grafana",
            "infrastructure/observability/prometheus.yaml",
            "infrastructure/observability/tempo.yaml",
        ]
    }
    for volume in config.get("volumes", {}).values():
        if volume.get("external") or not volume.get("name", "").startswith(PROJECT + "_"):
            raise RuntimeError("PROTECTED_VOLUME_REFUSED")
    for name, service in config["services"].items():
        for mount in service.get("volumes", []):
            if mount["type"] == "bind" and (
                mount["source"] not in allowed or not mount.get("read_only")
            ):
                raise RuntimeError("UNREVIEWED_BIND_MOUNT")
        if name in SERVICES and name not in {"postgres", "redis", "gateway", "kafka", "kafka-init"}:
            env = service.get("environment", {})
            if (
                env.get("OWNED_DRAFT_MODE") != "FIXTURE"
                or env.get("INFERENCE_CONFIG_FILE")
                or env.get("INFERENCE_EMBEDDING_CONFIG_FILE")
            ):
                raise RuntimeError("REAL_CONFIGURATION_REFUSED")
    for name in ["application", "state", "telemetry"]:
        if not config["networks"].get(name, {}).get("internal"):
            raise RuntimeError("INTERNAL_NETWORK_REQUIRED")


class Release:
    def __init__(self):
        self.state = ROOT / ".local/release-v1"
        self.private = ROOT / ".secrets/release-v1"
        self.state.mkdir(parents=True, exist_ok=True)
        self.private.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.runtime_file = self.state / "runtime.json"
        self.runtime = (
            json.loads(self.runtime_file.read_text()) if self.runtime_file.exists() else {}
        )
        db = self.private / "database.json"
        if not db.exists():
            with db.open("x") as stream:
                db.chmod(0o600)
                json.dump({"password": secrets.token_urlsafe(32)}, stream)
        self.env = {
            **os.environ,
            "COMPOSE_PROJECT_NAME": PROJECT,
            "AUTH_MODE": "local",
            "POSTGRES_USER": "nova",
            "POSTGRES_DB": "nova",
            "POSTGRES_PASSWORD": json.loads(db.read_text())["password"],
            "POSTGRES_PORT": "5432",
            "REDIS_PORT": "6379",
            "BACKEND_PORT": "8000",
            "ENABLE_EXTERNAL_MODEL_TESTS": "false",
            "OWNED_DRAFT_MODE": "FIXTURE",
            "NEXT_TELEMETRY_DISABLED": "1",
            "NODE_OPTIONS": "--max-old-space-size=512",
        }
        self.env["COMPOSE_FILE"] = ":".join(
            str(ROOT / p)
            for p in ["compose.yaml", "compose.phase8.yaml", ".local/release-v1/overlay.json"]
        )
        self.c = ["docker", "compose"]
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def gate(self):
        row = resource_sample()
        with (self.state / "resources.jsonl").open("a") as log:
            log.write(json.dumps(row) + "\n")
        enforce(row)
        return row

    def command(self, args, name, check=True, monitor=True):
        with (self.state / (name + ".log")).open("a") as log:
            child = subprocess.Popen(
                args,
                cwd=ROOT,
                env=self.env,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            deadline = time.monotonic() + 300
            try:
                while child.poll() is None:
                    if monitor:
                        self.gate()
                    if time.monotonic() >= deadline:
                        raise RuntimeError(name + " timed out")
                    time.sleep(0.5)
                code = child.returncode
            finally:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGTERM)
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGKILL)
                        child.wait(timeout=5)
        if check and code:
            raise RuntimeError(name + " failed; see ignored log")
        return code

    def api(self, path, body=None, expected=200, credential=True):
        token = (self.private / "operator.token").read_text().strip() if credential else None
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = "Bearer " + token
        req = urllib.request.Request(
            "http://localhost:8080/api/v1" + path,
            data=json.dumps(body).encode() if body is not None else None,
            headers=headers,
        )
        try:
            with self.opener.open(req, timeout=15) as response:
                if response.status != expected:
                    raise RuntimeError("UNEXPECTED_HTTP_STATUS")
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code != expected:
                raise RuntimeError("API_REFUSED_" + str(error.code)) from None
            raw = error.read()
            return json.loads(raw) if raw else None

    def prepare(self):
        verify_sources()
        self.gate()
        info = json.loads(
            subprocess.check_output(["docker", "info", "--format", "{{json .}}"], text=True)
        )
        if info["MemTotal"] != 4106604544:
            raise RuntimeError("DOCKER_ALLOCATION_CHANGED")
        for port in PORTS:
            with socket.socket() as sock:
                if sock.connect_ex(("127.0.0.1", port)) == 0:
                    raise RuntimeError("COMPETING_LISTENER_" + str(port))
        if subprocess.check_output(["docker", "ps", "-q"]).strip():
            raise RuntimeError("COMPETING_CONTAINERS")
        safe = {
            "AUTH_MODE": "local",
            "OWNED_DRAFT_MODE": "FIXTURE",
            "OTEL_SDK_DISABLED": "true",
            "INFERENCE_CONFIG_FILE": "",
            "INFERENCE_EMBEDDING_CONFIG_FILE": "",
            "INFERENCE_MODEL_CONFIG": "",
            "INFERENCE_EMBEDDING_CONFIG": "",
            "INFERENCE_RESIDENCY_KEY_FILE": "",
            "LOCAL_MODEL_ENABLED": "false",
            "MEMORY_EMBEDDINGS_ENABLED": "false",
            "ENABLE_EXTERNAL_MODEL_TESTS": "false",
            "REAL_MODEL_TESTS": "0",
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "VISION_CLIP_ENABLED": "false",
            "VISION_DINO_ENABLED": "false",
            "VISION_SAM_ENABLED": "false",
        }
        source = str(ROOT / "backend")
        worker = {
            "mem_limit": "384m",
            "cpus": 1,
            "environment": safe,
            "volumes": [source + "/app:/app/app:ro"],
        }
        services = {
            "postgres": {"mem_limit": "192m", "cpus": 1},
            "redis": {"mem_limit": "64m"},
            "backend": {
                "image": "nova-backend:latest",
                "mem_limit": "384m",
                "cpus": 2,
                "environment": safe,
                "volumes": [source + "/app:/app/app:ro", source + "/migrations:/app/migrations:ro"],
            },
            "gateway": {"mem_limit": "64m"},
            "kafka": {"mem_limit": "768m", "cpus": 2},
        }
        for name in [
            "publisher",
            "event-worker",
            "proactive-consumer",
            "audit-consumer",
            "proactive-worker",
        ]:
            services[name] = worker
        overlay = self.state / "overlay.json"
        if overlay.exists():
            networks = json.loads(overlay.read_text())["networks"]
        else:
            names = [
                "default",
                "edge",
                "application",
                "state",
                "telemetry",
                "identity",
                "backend_host",
                "telemetry_host",
            ]
            networks = {
                name: {"ipam": {"config": [{"subnet": subnet}]}}
                for name, subnet in zip(
                    names, allocate_subnets(occupied_subnets(), len(names)), strict=True
                )
            }
        atomic(overlay, {"services": services, "networks": networks})
        config = json.loads(
            subprocess.check_output(self.c + ["config", "--format", "json"], env=self.env)
        )
        validate(config)
        for name in SERVICES:
            subprocess.run(
                ["docker", "image", "inspect", config["services"][name]["image"]],
                stdout=subprocess.DEVNULL,
                check=True,
            )
        if not (ROOT / "frontend/node_modules").is_dir():
            raise RuntimeError("EXISTING_FRONTEND_DEPENDENCIES_REQUIRED")
        digest = frontend_digest()
        previous = self.state / "frontend.sha256"
        if (
            not previous.exists()
            or previous.read_text() != digest
            or not (ROOT / "frontend/.next/standalone/server.js").exists()
        ):
            self.env["NODE_OPTIONS"] = "--max-old-space-size=768"
            self.command(["npm", "--prefix", "frontend", "run", "build"], "frontend-build")
            self.env["NODE_OPTIONS"] = "--max-old-space-size=512"
            previous.write_text(digest)
        for src, dst in [
            (ROOT / "frontend/public", ROOT / "frontend/.next/standalone/public"),
            (ROOT / "frontend/.next/static", ROOT / "frontend/.next/standalone/.next/static"),
        ]:
            if src.exists():
                shutil.copytree(src, dst, dirs_exist_ok=True)

    def token(self):
        subject = "nova-v1-operator"
        self.command(
            self.c
            + [
                "exec",
                "-T",
                "backend",
                "python",
                "-m",
                "app.security.cli",
                "provision",
                "--subject",
                subject,
                "--user-id",
                "00000000-0000-4000-8000-000000000001",
                "--output",
                "/app/security/release.token",
            ],
            "credential-provision",
        )
        value = subprocess.check_output(
            self.c + ["exec", "-T", "backend", "cat", "/app/security/release.token"], env=self.env
        )
        target = self.private / "operator.token"
        target.write_bytes(value)
        target.chmod(0o600)
        atomic(self.state / "credential-state.json", {"issued": True, "revoked": False})
        devices = self.api("/auth/devices")
        desktop = next(d for d in devices if d["type"] == "DESKTOP")
        if not desktop["enabled"]:
            raise RuntimeError("DEVICE_REVOKED")
        if desktop["version"] == 0:
            self.api("/auth/devices/register", {"device_id": desktop["device_id"]})
            # Registration invalidates enrollment credentials; mint the bound version.
            self.token()
        return str(target.relative_to(ROOT))

    def status(self):
        try:
            self.gate()
            self.api("/auth/me")
            with self.opener.open("http://localhost:8000/health/ready", timeout=3) as response:
                ready = response.status == 200
            with self.opener.open("http://localhost:3000/auth", timeout=3) as response:
                ready = ready and response.status == 200
            ids = subprocess.check_output(
                ["docker", "ps", "-q", "--filter", "label=com.docker.compose.project=" + PROJECT],
                text=True,
            ).split()
            inspected = (
                json.loads(subprocess.check_output(["docker", "inspect", *ids])) if ids else []
            )
            rows = {
                item["Config"]["Labels"].get("com.docker.compose.service"): item
                for item in inspected
            }
            ready = ready and set(SERVICES) - {"kafka-init"} <= set(rows)
            ready = ready and all(
                item["State"].get("Health", {}).get("Status", "healthy") == "healthy"
                for item in inspected
            )
            return {
                "status": "READY"
                if ready
                and alive(self.runtime.get("frontend"))
                and alive(self.runtime.get("watcher"))
                else "BLOCKED",
                "url": "http://localhost:3000/auth",
                "mode": "FIXTURE / REAL INFERENCE DISABLED",
            }
        except Exception as error:
            return {"status": "BLOCKED", "reason": str(error)}

    def start(self):
        if (
            alive(self.runtime.get("frontend"))
            or subprocess.check_output(
                ["docker", "ps", "-q", "--filter", "label=com.docker.compose.project=" + PROJECT]
            ).strip()
        ):
            if self.status()["status"] == "READY":
                return self.status()
            raise RuntimeError("PARTIAL_RELEASE_STATE; use recover")
        self.prepare()
        try:
            self.command(
                self.c
                + [
                    "up",
                    "-d",
                    "--no-build",
                    "--pull",
                    "never",
                    "--wait",
                    "postgres",
                    "redis",
                    "backend",
                    "gateway",
                ],
                "app-start",
            )
            self.gate()
            self.token()
            self.command(
                self.c
                + [
                    "up",
                    "-d",
                    "--no-build",
                    "--pull",
                    "never",
                    "--wait",
                    "kafka",
                    "kafka-init",
                    "publisher",
                    "event-worker",
                    "proactive-consumer",
                    "audit-consumer",
                    "proactive-worker",
                ],
                "queue-start",
            )
            self.gate()
            with (self.state / "frontend.log").open("a") as log:
                process = subprocess.Popen(
                    ["node", str(ROOT / "frontend/.next/standalone/server.js")],
                    cwd=ROOT / "frontend",
                    env={
                        **self.env,
                        "HOSTNAME": "127.0.0.1",
                        "PORT": "3000",
                        "API_INTERNAL_URL": "http://localhost:8080",
                        "NOVA_PUBLIC_ORIGIN": "http://localhost:3000",
                        "NOVA_AUTH_MODE": "local",
                    },
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            self.runtime = {"frontend": process_record(process)}
            atomic(self.runtime_file, self.runtime)
            until = time.monotonic() + 30
            while time.monotonic() < until:
                self.gate()
                if process.poll() is not None:
                    raise RuntimeError("FRONTEND_EXITED")
                try:
                    with self.opener.open("http://localhost:3000/auth", timeout=1) as response:
                        if response.status == 200:
                            break
                except OSError:
                    time.sleep(0.2)
            else:
                raise RuntimeError("FRONTEND_NOT_READY")
            with (self.state / "watcher.log").open("a") as log:
                watcher = subprocess.Popen(
                    [sys.executable, str(Path(__file__).resolve()), "watch"],
                    cwd=ROOT,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            self.runtime["watcher"] = process_record(watcher)
            atomic(self.runtime_file, self.runtime)
            self.gate()
            result = self.status()
            if result["status"] != "READY":
                raise RuntimeError("FINAL_HEALTH_FAILED")
            return result
        except BaseException:
            self.stop()
            raise

    def stop(self, from_watch=False):
        self.runtime = (
            json.loads(self.runtime_file.read_text()) if self.runtime_file.exists() else {}
        )
        if not from_watch:
            stop_process(self.runtime.get("watcher"))
        stop_process(self.runtime.get("frontend"))
        credential_state = self.state / "credential-state.json"
        previous = (
            json.loads(credential_state.read_text())
            if credential_state.exists()
            else {"issued": False}
        )
        closed = not previous.get("issued") or previous.get("revoked", False)
        if not closed:
            closed = (
                self.command(
                    self.c
                    + [
                        "exec",
                        "-T",
                        "backend",
                        "python",
                        "-m",
                        "app.security.cli",
                        "revoke",
                        "--subject",
                        "nova-v1-operator",
                        "--output",
                        "/app/security/closed",
                    ],
                    "credential-revoke",
                    check=False,
                    monitor=False,
                )
                == 0
            )
        if closed:
            atomic(credential_state, {"issued": previous.get("issued", False), "revoked": True})
        self.command(self.c + ["stop"], "services-stop", monitor=False)
        running = subprocess.check_output(
            ["docker", "ps", "-q", "--filter", "label=com.docker.compose.project=" + PROJECT]
        ).strip()
        atomic(
            self.state / "shutdown.json",
            {
                "services_stopped": not bool(running),
                "credential_revoked": closed,
                "models_activated": False,
                "volumes_preserved": True,
            },
        )
        if self.runtime_file.exists():
            self.runtime_file.unlink()  # Only ephemeral PID state, never application data.
        return {
            "status": "STOPPED" if not running and closed else "BLOCKED",
            "credential_revoked": closed,
        }

    def watch(self):
        done = False

        def finish(signum, frame):
            nonlocal done
            done = True

        signal.signal(signal.SIGTERM, finish)
        while not done:
            time.sleep(2)
            if done:
                break
            try:
                self.gate()
            except Exception:
                atomic(
                    self.state / "resource-stop.json",
                    {"reason": "RESOURCE_GATE_OR_MEASUREMENT_FAILED", "at": time.time()},
                )
                self.stop(from_watch=True)
                return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["start", "status", "token", "smoke", "stop", "recover", "watch"]
    )
    args = parser.parse_args()
    release = Release()
    if args.command == "watch":
        release.watch()
        return
    with (release.state / "operation.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.command == "start":
            result = release.start()
        elif args.command == "stop":
            result = release.stop()
        elif args.command == "status":
            result = release.status()
        elif args.command == "token":
            result = {
                "token_file": release.token(),
                "notice": "Prior sessions/draft grants are invalidated",
            }
        elif args.command == "recover":
            release.stop()
            result = release.start()
        else:
            from smoke_local_release import smoke

            result = smoke(release)
        print(json.dumps(result, indent=2))
        if result.get("status") == "BLOCKED":
            raise SystemExit(1)


if __name__ == "__main__":
    main()
