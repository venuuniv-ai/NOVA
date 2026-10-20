"""Local, offline Phase 11 qualification. Existing images/dependencies only.

Default runs every stage. Reports/logs stay in ignored .local/phase11; private
credentials in ignored .secrets. Never starts models or deletes volumes. Partial
stage success is not full qualification. Run python3 scripts/qualify_phase11.py.
"""

import argparse
import ipaddress
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = ("host", "backend", "static", "integration")


def resource_sample(root=ROOT):
    swap = subprocess.check_output(["sysctl", "vm.swapusage"], text=True)
    match = re.search(r"used = ([\d.]+)M", swap)
    if not match:
        raise RuntimeError("RESOURCE_MEASUREMENT_UNAVAILABLE")
    return {
        "at": time.time(),
        "swap_mib": float(match[1]),
        "free_disk_bytes": shutil.disk_usage(root).free,
    }


def enforce(sample):
    if sample["swap_mib"] >= 2048 or sample["free_disk_bytes"] < 5 * 1024**3:
        raise RuntimeError("RESOURCE_GATE")


def validate_config(config, project, root=ROOT):
    """Reject protected data targeting and any inherited real provider settings."""
    if not re.fullmatch(r"nova-phase11-q-[a-f0-9]{12}", project):
        raise ValueError("ISOLATED_PROJECT_REQUIRED")
    if any(v.get("external") for v in config.get("volumes", {}).values()):
        raise ValueError("EXTERNAL_VOLUME_REFUSED")
    for volume in config.get("volumes", {}).values():
        if not volume.get("name", "").startswith(project + "_"):
            raise ValueError("PROTECTED_VOLUME_REFUSED")
    permitted = {
        str(root / p)
        for p in [
            "backend/app",
            "backend/tests",
            "backend/migrations",
            "backend/pyproject.toml",
            "infrastructure/oidc/realm.json",
            "infrastructure/observability/collector.yaml",
            "infrastructure/observability/grafana",
            "infrastructure/observability/prometheus.yaml",
            "infrastructure/observability/tempo.yaml",
        ]
    }
    for name, service in config["services"].items():
        if name in {
            "backend",
            "backend-tests",
            "publisher",
            "event-worker",
            "proactive-consumer",
            "audit-consumer",
            "proactive-worker",
        }:
            env = service.get("environment", {})
            for key in [
                "INFERENCE_CONFIG_FILE",
                "INFERENCE_EMBEDDING_CONFIG_FILE",
                "INFERENCE_MODEL_CONFIG",
                "INFERENCE_EMBEDDING_CONFIG",
                "INFERENCE_RESIDENCY_KEY_FILE",
            ]:
                if env.get(key):
                    raise ValueError("REAL_CONFIGURATION_REFUSED")
            if str(env.get("OWNED_DRAFT_MODE", "FIXTURE")) != "FIXTURE":
                raise ValueError("REAL_CONFIGURATION_REFUSED")
            if str(env.get("ENABLE_EXTERNAL_MODEL_TESTS", "false")).lower() != "false":
                raise ValueError("EXTERNAL_TESTS_REFUSED")
        for mount in service.get("volumes", []):
            if mount["type"] == "bind" and (
                mount["source"] not in permitted or not mount.get("read_only")
            ):
                raise ValueError("UNREVIEWED_BIND_MOUNT")


def allocate_subnets(occupied, count):
    blocked = [ipaddress.ip_network(value, strict=False) for value in occupied]
    chosen = []
    for subnet in ipaddress.ip_network("10.240.0.0/16").subnets(new_prefix=24):
        if not any(subnet.overlaps(other) for other in blocked if other.version == 4):
            chosen.append(str(subnet))
            if len(chosen) == count:
                return chosen
    raise RuntimeError("NO_ISOLATED_NETWORK_SPACE")


def occupied_subnets():
    ids = subprocess.check_output(["docker", "network", "ls", "-q"], text=True).split()
    existing = json.loads(subprocess.check_output(["docker", "network", "inspect", *ids]))
    occupied = [
        item["Subnet"]
        for network in existing
        for item in (network.get("IPAM", {}).get("Config") or [])
        if "Subnet" in item
    ]
    routes = subprocess.check_output(["netstat", "-rn", "-f", "inet"], text=True)
    for line in routes.splitlines():
        parts = line.split()
        if not parts or not re.fullmatch(r"[0-9./]+", parts[0]):
            continue
        address, *prefix = parts[0].split("/")
        octets = address.split(".")
        if len(octets) > 4:
            raise RuntimeError("UNRECOGNIZED_HOST_ROUTE")
        network = ".".join(octets + ["0"] * (4 - len(octets)))
        occupied.append(network + "/" + (prefix[0] if prefix else str(8 * len(octets))))
    return occupied


class Runner:
    def __init__(self, stages):
        import uuid

        self.project = "nova-phase11-q-" + uuid.uuid4().hex[:12]
        self.out = ROOT / ".local/phase11" / self.project
        self.private = ROOT / ".secrets" / self.project
        self.out.mkdir(parents=True, exist_ok=False)
        self.private.mkdir(mode=0o700, parents=True, exist_ok=False)
        self.stages = stages
        self.records = []
        self.children = []
        self.stop_watch = threading.Event()
        self.unsafe = threading.Event()
        self.env = {
            **os.environ,
            "COMPOSE_PROJECT_NAME": self.project,
            "ENABLE_EXTERNAL_MODEL_TESTS": "false",
            "NEXT_TELEMETRY_DISABLED": "1",
            "NODE_OPTIONS": "--max-old-space-size=512",
            "QUAL_AUTH_MODE": "demo",
            "POSTGRES_USER": "nova",
            "POSTGRES_PASSWORD": "nova_local_only",
            "POSTGRES_DB": "nova",
            "OWNED_DRAFT_MODE": "FIXTURE",
        }
        self.c = ["docker", "compose", "--profile", "test"]
        self.env.pop("COMPOSE_FILE", None)
        self.owned = False
        self.report = {
            "status": "RUNNING",
            "stages": stages,
            "real_calls": 0,
            "model_scope": "DISABLED",
            "project": self.project,
        }

    def gate(self):
        row = resource_sample()
        with (self.out / "resources.jsonl").open("a") as stream:
            stream.write(json.dumps(row) + "\n")
        enforce(row)
        if self.unsafe.is_set():
            raise RuntimeError("RESOURCE_STOP")
        return row

    def watch(self):
        while not self.stop_watch.wait(2):
            try:
                self.gate()
            except Exception:
                self.unsafe.set()
                for process in self.children:
                    self.terminate(process)
                return

    @staticmethod
    def terminate(process):
        if process.poll() is not None:
            return
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
        except ProcessLookupError:
            pass

    def run(self, args, name, cwd=ROOT, extra=None, expected=0, timeout=600):
        self.gate()
        started = time.monotonic()
        failure, code = None, None
        with (self.out / (name + ".log")).open("w") as log:
            try:
                child = subprocess.Popen(
                    args,
                    cwd=cwd,
                    env={**self.env, **(extra or {})},
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                self.children.append(child)
                try:
                    code = child.wait(timeout=timeout)
                finally:
                    self.terminate(child)
            except BaseException as error:
                failure = type(error).__name__
        row = {
            "stage": name,
            "exit_code": code,
            "expected_exit": expected,
            "failure": failure,
            "seconds": round(time.monotonic() - started, 3),
        }
        self.records.append(row)
        (self.out / "commands.json").write_text(json.dumps(self.records, indent=2) + "\n")
        if failure or code != expected or self.unsafe.is_set():
            raise RuntimeError(name + " FAILED")
        return (self.out / (name + ".log")).read_text()

    def setup(self):
        self.gate()
        info = json.loads(
            subprocess.check_output(["docker", "info", "--format", "{{json .}}"], text=True)
        )
        if info["MemTotal"] != 4106604544:
            raise RuntimeError("DOCKER_ALLOCATION_CHANGED")
        self.report["docker_memory_bytes"] = info["MemTotal"]
        if subprocess.check_output(["docker", "ps", "-q"]).strip():
            raise RuntimeError("COMPETING_CONTAINERS")
        for port in [3000, 8000, 8080, 8180, 5432, 6379, 11434, 11435, 11436]:
            with socket.socket() as sock:
                if sock.connect_ex(("127.0.0.1", port)) == 0:
                    raise RuntimeError("COMPETING_LISTENER")
        source = str(ROOT / "backend")
        safe = {
            "OWNED_DRAFT_MODE": "FIXTURE",
            "INFERENCE_CONFIG_FILE": "",
            "INFERENCE_EMBEDDING_CONFIG_FILE": "",
            "INFERENCE_RESIDENCY_KEY_FILE": "",
            "INFERENCE_MODEL_CONFIG": "",
            "INFERENCE_EMBEDDING_CONFIG": "",
            "LOCAL_MODEL_ENABLED": "false",
            "MEMORY_EMBEDDINGS_ENABLED": "false",
            "ENABLE_EXTERNAL_MODEL_TESTS": "false",
            "REAL_MODEL_TESTS": "0",
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "OTEL_SDK_DISABLED": "true",
        }
        app = {
            "image": "nova-backend:latest",
            "mem_limit": "384m",
            "cpus": 2,
            "environment": {**safe, "AUTH_MODE": "${QUAL_AUTH_MODE:-demo}"},
            "volumes": [source + "/app:/app/app:ro", source + "/migrations:/app/migrations:ro"],
        }
        worker = {
            "mem_limit": "384m",
            "cpus": 1,
            "environment": safe,
            "volumes": [source + "/app:/app/app:ro"],
        }
        services = {
            "backend": app,
            "postgres": {"mem_limit": "192m", "cpus": 1},
            "redis": {"mem_limit": "64m"},
            "gateway": {"mem_limit": "64m"},
            "kafka": {"mem_limit": "768m", "cpus": 2},
            "keycloak": {"mem_limit": "768m", "cpus": 1},
            "test-db": {
                "mem_limit": "512m",
                "cpus": 1,
                "command": [
                    "postgres",
                    "-c",
                    "shared_buffers=32MB",
                    "-c",
                    "max_wal_size=64MB",
                    "-c",
                    "min_wal_size=32MB",
                ],
            },
            "test-redis": {"mem_limit": "48m"},
            "backend-tests": {
                "image": "nova-backend-tests:latest",
                "mem_limit": "512m",
                "cpus": 2,
                "environment": safe,
                "volumes": [
                    source + "/" + p + ":/app/" + p + ":ro"
                    for p in ["app", "tests", "migrations", "pyproject.toml"]
                ],
            },
        }
        for name in [
            "publisher",
            "event-worker",
            "proactive-consumer",
            "audit-consumer",
            "proactive-worker",
        ]:
            services[name] = worker
        overlay = self.out / "overlay.json"
        networks = [
            "default",
            "edge",
            "application",
            "state",
            "telemetry",
            "identity",
            "backend_host",
            "telemetry_host",
            "identity_host",
        ]
        occupied = occupied_subnets()
        plan = dict(zip(networks, allocate_subnets(occupied, len(networks)), strict=True))
        (self.out / "network-plan.json").write_text(
            json.dumps({"occupied": occupied, "assigned": plan}, indent=2) + "\n"
        )
        overlay.write_text(
            json.dumps(
                {
                    "services": services,
                    "networks": {
                        name: {"ipam": {"config": [{"subnet": subnet}]}}
                        for name, subnet in plan.items()
                    },
                },
                indent=2,
            )
            + "\n"
        )
        self.env["COMPOSE_FILE"] = (
            ":".join(
                str(ROOT / p) for p in ["compose.yaml", "compose.phase8.yaml", "compose.oidc.yaml"]
            )
            + ":"
            + str(overlay)
        )
        config = json.loads(
            subprocess.check_output(self.c + ["config", "--format", "json"], env=self.env)
        )
        # The unused container frontend has its own source-free image; no bind mounts.
        validate_config(config, self.project)
        self.owned = True
        for name in [
            "backend",
            "backend-tests",
            "postgres",
            "redis",
            "gateway",
            "kafka",
            "keycloak",
        ]:
            subprocess.run(
                ["docker", "image", "inspect", config["services"][name]["image"]],
                check=True,
                stdout=subprocess.DEVNULL,
            )
        (self.out / "baseline.json").write_text(
            json.dumps(
                {
                    "head": subprocess.check_output(
                        ["git", "rev-parse", "HEAD"], text=True
                    ).strip(),
                    "stages": self.stages,
                    "workload": {
                        "http_samples": 10,
                        "concurrency": 1,
                        "warmups": 0,
                        "broker_recovery_tasks": 1,
                    },
                    "swap_limit_mib_exclusive": 2048,
                    "disk_min_bytes": 5 * 1024**3,
                },
                indent=2,
            )
            + "\n"
        )

    def cleanup(self):
        """Stop only this generated project, including detached one-off test runners."""
        try:
            with (self.out / "stop.log").open("w") as log:
                stopped = (
                    subprocess.run(
                        self.c + ["stop"],
                        cwd=ROOT,
                        env=self.env,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        timeout=60,
                    ).returncode
                    == 0
                )
                own = [
                    "docker",
                    "ps",
                    "-q",
                    "--filter",
                    "label=com.docker.compose.project=" + self.project,
                ]
                remaining = subprocess.check_output(own, text=True).split()
                if remaining:
                    stopped = (
                        subprocess.run(
                            ["docker", "stop", "--time", "10", *remaining],
                            stdout=log,
                            stderr=subprocess.STDOUT,
                            timeout=45,
                        ).returncode
                        == 0
                        and stopped
                    )
                return stopped and not subprocess.check_output(own).strip()
        except Exception:
            return False

    def execute(self):
        watcher = None
        try:
            self.setup()
            watcher = threading.Thread(target=self.watch, daemon=True)
            watcher.start()
            if "host" in self.stages:
                for name in ["test_phase9_residency", "test_phase11_qualification"]:
                    self.run(["python3", "scripts/" + name + ".py"], name)
            if "backend" in self.stages:
                self.run(
                    self.c
                    + [
                        "run",
                        "--rm",
                        "--pull",
                        "never",
                        "backend-tests",
                        "sh",
                        "-c",
                        "pytest -q && ruff check app tests && "
                        "ruff format --check app tests && pip check",
                    ],
                    "backend",
                )
                self.run(self.c + ["stop", "test-db", "test-redis"], "test-stop")
            if "static" in self.stages:
                self.run(
                    [
                        "docker",
                        "run",
                        "--rm",
                        "--pull",
                        "never",
                        "--network",
                        "none",
                        "--memory",
                        "384m",
                        "--cpus",
                        "2",
                        "-v",
                        str(ROOT / "gateway") + ":/src:ro",
                        "-w",
                        "/src",
                        "-e",
                        "GOPROXY=off",
                        "-e",
                        "GOTOOLCHAIN=local",
                        "nova-gateway-compiler:local",
                        "sh",
                        "-c",
                        "go test -race -count=1 ./... && go vet ./...",
                    ],
                    "go",
                )
                for cmd in ["lint", "typecheck", "build"]:
                    self.run(
                        ["npm", "run", cmd],
                        "frontend-" + cmd,
                        cwd=ROOT / "frontend",
                        extra={"NODE_OPTIONS": "--max-old-space-size=768"},
                    )
            if "integration" in self.stages:
                from phase11_integration import qualify

                qualify(self)
            self.report["status"] = "PASS" if set(self.stages) == set(STAGES) else "PARTIAL_PASS"
        except BaseException as error:
            self.report.update(status="FAIL", error=type(error).__name__ + ": " + str(error))
        finally:
            self.stop_watch.set()
            if watcher:
                watcher.join(timeout=5)
            for child in self.children:
                self.terminate(child)
            if self.owned:
                self.report["services_stopped"] = self.cleanup()
                if not self.report["services_stopped"]:
                    self.report["status"] = "FAIL"
            self.report["commands"] = self.records
            (self.out / "report.json").write_text(json.dumps(self.report, indent=2) + "\n")
            print(
                json.dumps(
                    {"report": str(self.out / "report.json"), "status": self.report["status"]}
                )
            )
        return self.report["status"] in {"PASS", "PARTIAL_PASS"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stages", nargs="+", choices=STAGES, default=list(STAGES))
    args = parser.parse_args()

    def interrupted(signum, frame):
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(0 if Runner(args.stages).execute() else 1)


if __name__ == "__main__":
    main()
