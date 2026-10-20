"""Staged fixture/auth/Kafka/browser qualification used only by qualify_phase11."""

import json
import secrets
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

from qualify_phase11 import ROOT


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


TERMINAL_SQL = """
SELECT json_build_object(
 'real_configuration_refusals', (SELECT count(*) FROM inference_runs WHERE
  metadata_snapshot->>'mode'='LOCAL_REAL' AND state='FAILED'
  AND metadata_snapshot->>'error'='MODEL_NOT_CONFIGURED'),
 'running_or_done_real_inference_rows', (SELECT count(*) FROM inference_runs WHERE
  metadata_snapshot->>'mode'='LOCAL_REAL' AND state IN ('RUNNING','DONE')),
 'unexpected_real_failures', (SELECT count(*) FROM inference_runs WHERE
  metadata_snapshot->>'mode'='LOCAL_REAL' AND state='FAILED'
  AND COALESCE(metadata_snapshot->>'error','') <> 'MODEL_NOT_CONFIGURED'),
 'non_fixture_invocations', (SELECT count(*) FROM model_calls c
  CROSS JOIN LATERAL jsonb_array_elements(c.attempts) a
  WHERE a->>'invoked'='true' AND NOT COALESCE(
   (a->>'provider'='fixture' AND a->>'model'='nova-demo-v1') OR
   (a->>'provider'='fixture-vlm' AND a->>'model'='fixture-vlm-v1') OR
   (a->>'provider'='test-failing-local' AND a->>'model'='FAILURE_POLICY_FIXTURE'),false)),
 'owned_draft_executions', (SELECT count(*) FROM action_executions e
  JOIN action_proposals p ON p.id=e.proposal_id WHERE p.policy_version='OWNED_CONTEXT_V1'),
 'evaluation_schemas', (SELECT count(*) FROM information_schema.schemata
  WHERE schema_name LIKE 'nova_eval_%')
)
"""


def verify_terminal(snapshot):
    required = [
        "running_or_done_real_inference_rows",
        "unexpected_real_failures",
        "non_fixture_invocations",
        "owned_draft_executions",
        "evaluation_schemas",
    ]
    if any(type(snapshot.get(k)) is not int or snapshot[k] != 0 for k in required):
        raise RuntimeError("TERMINAL_INVARIANT_FAILED")
    if (
        type(snapshot.get("real_configuration_refusals")) is not int
        or snapshot["real_configuration_refusals"] < 0
    ):
        raise RuntimeError("TERMINAL_MEASUREMENT_MISSING")


def qualify(r):
    c = r.c
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    grants, tokens = [], {}
    front = None

    def api(path, payload=None, token=None, expected=200):
        request = urllib.request.Request(
            "http://localhost:8080/api/v1" + path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={
                "Content-Type": "application/json",
                **({"Authorization": "Bearer " + token} if token else {}),
            },
        )
        try:
            with opener.open(request, timeout=20) as response:
                assert response.status == expected
                return json.load(response)
        except urllib.error.HTTPError as error:
            assert error.code == expected, (path, error.code, expected)
            raw = error.read()
            return json.loads(raw) if raw else None

    def start(*services):
        r.run(
            c + ["up", "-d", "--no-build", "--pull", "never", "--wait", *services],
            "start-" + services[-1],
            timeout=300,
        )

    def stopfront():
        nonlocal front
        if front:
            r.terminate(front)
        front = None

    def startfront(mode):
        nonlocal front
        stopfront()
        with (r.out / "frontend-server.log").open("a") as log:
            front = subprocess.Popen(
                ["npm", "run", "start", "--", "--hostname", "127.0.0.1"],
                cwd=ROOT / "frontend",
                env={
                    **r.env,
                    "API_INTERNAL_URL": "http://localhost:8080",
                    "NOVA_PUBLIC_ORIGIN": "http://localhost:3000",
                    "NOVA_AUTH_MODE": mode,
                    "OIDC_PUBLIC_ISSUER": "http://localhost:8180/realms/nova",
                    "OIDC_INTERNAL_ISSUER": "http://localhost:8180/realms/nova",
                    "OIDC_REDIRECT_URI": "http://localhost:3000/auth/oidc/callback",
                },
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        r.children.append(front)
        until = time.monotonic() + 45
        while time.monotonic() < until:
            r.gate()
            assert front.poll() is None, "FRONTEND_EXITED"
            try:
                with opener.open("http://localhost:3000/auth", timeout=1) as response:
                    if response.status == 200:
                        return
            except OSError:
                time.sleep(0.2)
        raise RuntimeError("FRONTEND_READINESS")

    def browser(name, files, extra=None):
        r.run(
            ["npm", "run", "test:e2e", "--", *files, "--trace", "off"],
            name,
            cwd=ROOT / "frontend",
            extra=extra,
        )

    def provision(label, uid):
        subject = r.project + "-" + label
        grants.append(("nova-local", subject))
        r.run(
            c
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
                uid,
                "--output",
                "/app/security/" + label + ".token",
            ],
            "provision-" + label,
        )
        raw = subprocess.check_output(
            c + ["exec", "-T", "backend", "cat", "/app/security/" + label + ".token"], env=r.env
        )
        target = r.private / (label + ".token")
        target.write_bytes(raw)
        target.chmod(0o600)
        tokens[label] = raw.decode().strip()

    def oidc():
        # Controlled local realm only. The admin password and test password never
        # enter command arguments, stdout, report metadata or the repository.
        until = time.monotonic() + 45
        while time.monotonic() < until:
            r.gate()
            try:
                with opener.open(
                    "http://localhost:8180/realms/nova/.well-known/openid-configuration", timeout=2
                ) as ready:
                    if ready.status == 200:
                        break
            except OSError:
                time.sleep(0.3)
        else:
            raise RuntimeError("OIDC_READINESS")
        password = subprocess.check_output(
            c + ["exec", "-T", "keycloak", "cat", "/opt/keycloak/data/operator.password"],
            env=r.env,
            text=True,
        ).strip()

        def request(path, payload=None, bearer=None, form=False, method=None):
            body = (
                urllib.parse.urlencode(payload).encode()
                if form
                else json.dumps(payload).encode()
                if payload is not None
                else None
            )
            headers = {
                "Content-Type": "application/x-www-form-urlencoded" if form else "application/json"
            }
            if bearer:
                headers["Authorization"] = "Bearer " + bearer
            with opener.open(
                urllib.request.Request(
                    "http://localhost:8180" + path, data=body, headers=headers, method=method
                ),
                timeout=10,
            ) as response:
                raw = response.read()
                return json.loads(raw) if raw else None

        admin = request(
            "/realms/master/protocol/openid-connect/token",
            {
                "grant_type": "password",
                "client_id": "admin-cli",
                "username": "admin",
                "password": password,
            },
            form=True,
        )["access_token"]
        profile = request("/admin/realms/nova/users/profile", bearer=admin)
        if not any(a.get("name") == "device_id" for a in profile["attributes"]):
            profile["attributes"].append(
                {
                    "name": "device_id",
                    "displayName": "Simulated device context",
                    "permissions": {"view": ["admin", "user"], "edit": ["admin"]},
                    "multivalued": False,
                    "validations": {"length": {"min": 36, "max": 36}},
                }
            )
            request("/admin/realms/nova/users/profile", profile, admin, method="PUT")
        request(
            "/admin/realms/nova/users",
            {
                "username": "nova-local-fixture",
                "enabled": True,
                "firstName": "Local",
                "lastName": "Fixture",
                "email": "fixture@localhost.invalid",
                "emailVerified": True,
                "attributes": {"device_id": ["00000000-0000-4000-8000-000000000010"]},
            },
            admin,
        )
        subject = request("/admin/realms/nova/users?username=nova-local-fixture", bearer=admin)[0][
            "id"
        ]
        pw = secrets.token_urlsafe(32)
        request(
            "/admin/realms/nova/users/" + subject + "/reset-password",
            {"type": "password", "temporary": False, "value": pw},
            admin,
            method="PUT",
        )
        grants.append(("http://localhost:8180/realms/nova", subject))
        r.run(
            c
            + [
                "exec",
                "-T",
                "backend",
                "python",
                "-m",
                "app.security.cli",
                "provision",
                "--issuer",
                "http://localhost:8180/realms/nova",
                "--subject",
                subject,
                "--user-id",
                "00000000-0000-4000-8000-000000000001",
                "--output",
                "/app/security/oidc-grant",
            ],
            "oidc-grant",
        )
        target = r.private / "oidc.password"
        target.write_text(pw)
        target.chmod(0o600)
        return pw

    try:
        start("postgres", "redis", "backend", "gateway")
        for command in ["current", "check"]:
            r.run(c + ["exec", "-T", "backend", "alembic", command], "alembic-" + command)
        startfront("demo")
        browser(
            "browser-replay-A",
            [
                "tests/continuity.spec.ts",
                "tests/evaluation.spec.ts",
                "tests/inference.spec.ts",
                "tests/intelligence.spec.ts",
                "tests/memory.spec.ts",
                "tests/models.spec.ts",
            ],
        )
        # One full gateway quota window; never change the quota or retry tests.
        for _ in range(31):
            r.gate()
            time.sleep(2)
        browser(
            "browser-replay-B",
            [
                "tests/operations.spec.ts",
                "tests/owned-drafts.spec.ts",
                "tests/perception.spec.ts",
                "tests/proactive.spec.ts",
                "tests/security.spec.ts",
            ],
        )
        stopfront()
        r.env["QUAL_AUTH_MODE"] = "local"
        start(
            "backend",
            "gateway",
            "kafka",
            "kafka-init",
            "publisher",
            "event-worker",
            "proactive-consumer",
            "audit-consumer",
            "proactive-worker",
        )
        provision("a", "00000000-0000-4000-8000-000000000001")
        provision("b", "a0000000-0000-4000-8000-000000000002")
        startfront("local")
        browser(
            "browser-local-auth",
            ["tests/security.spec.ts", "--grep", "authenticated local stack"],
            {"NOVA_TEST_BEARER": tokens["a"]},
        )
        extra = {"NOVA_TOKEN_A": tokens["a"], "NOVA_TOKEN_B": tokens["b"]}
        r.run(
            ["python3", "scripts/acceptance_phase10.py", "--inject-duplicates", "--recovery"],
            "phase10-events",
            extra=extra,
        )
        r.run(
            ["python3", "scripts/acceptance_phase8.py", "--inject-duplicates"],
            "phase8-events",
            extra=extra,
        )
        # Predeclared ten sequential fixture HTTP reads; no model/capacity claim.
        task = api(
            "/tasks",
            {
                "title": "Phase 11 fixture timing",
                "origin_device_id": "00000000-0000-4000-8000-000000000010",
            },
            tokens["a"],
            201,
        )
        samples = []
        for _ in range(10):
            before = time.perf_counter()
            assert api("/tasks/" + task["id"], token=tokens["a"])["id"] == task["id"]
            samples.append(round((time.perf_counter() - before) * 1000, 3))
        r.run(c + ["stop", "kafka"], "broker-outage")
        try:
            outage = api(
                "/tasks",
                {
                    "title": "Phase 11 broker outage",
                    "origin_device_id": "00000000-0000-4000-8000-000000000010",
                },
                tokens["a"],
                201,
            )
            before_recovery = api("/operations/tasks/" + outage["id"], token=tokens["a"])
            assert any(e["state"] == "PENDING" for e in before_recovery["events"])
        finally:
            started = time.perf_counter()
            start("kafka")
        until = time.monotonic() + 90
        while time.monotonic() < until:
            r.gate()
            records = api("/operations/tasks/" + outage["id"], token=tokens["a"])
            if all(
                e["state"] == "PUBLISHED"
                and set(e["consumers"]) == {"projection", "proactive", "audit"}
                for e in records["events"]
            ):
                break
            time.sleep(0.3)
        else:
            raise RuntimeError("BROKER_RECOVERY")
        measured = {
            "http_scope": "10 sequential authenticated fixture task reads through local gateway",
            "samples_ms": samples,
            "concurrency": 1,
            "warmups": 0,
            "recovery_task": outage["id"],
            "events": len(records["events"]),
            "recovery_seconds_from_restart": round(time.perf_counter() - started, 3),
            "hardware": "Apple M2 / 8 GiB RAM",
            "real_model_calls": 0,
        }
        (r.out / "measurements.json").write_text(json.dumps(measured, indent=2) + "\n")
        r.run(
            c
            + [
                "stop",
                "publisher",
                "event-worker",
                "proactive-consumer",
                "audit-consumer",
                "proactive-worker",
                "kafka",
            ],
            "kafka-stop",
        )
        for suite in ["FULL", "SMOKE", "REGRESSION"]:
            r.run(
                c
                + ["exec", "-T", "backend", "python", "-m", "app.evaluation.cli", "--suite", suite],
                "golden-" + suite,
            )
        r.run(
            c
            + [
                "exec",
                "-T",
                "backend",
                "python",
                "-m",
                "app.evaluation.cli",
                "--suite",
                "REGRESSION",
                "--configuration",
                "CAUTIOUS_THRESHOLD",
            ],
            "golden-negative-control",
            expected=1,
        )
        stopfront()
        r.env["QUAL_AUTH_MODE"] = "oidc"
        start("backend", "keycloak")
        pw = oidc()
        startfront("oidc")
        browser(
            "browser-oidc",
            ["tests/security.spec.ts", "--grep", "local OIDC provider"],
            {"NOVA_TEST_OIDC_PASSWORD": pw},
        )
        check = """
import json
from sqlalchemy import text
from app.database import SessionLocal
with SessionLocal() as session:
 session.execute(text('SET TRANSACTION READ ONLY'))
 result = session.scalar(text(SQL))
 print(json.dumps(result))
""".replace("SQL", repr(TERMINAL_SQL))
        raw = r.run(c + ["exec", "-T", "backend", "python", "-c", check], "terminal-invariants")
        verify_terminal(json.loads(raw.strip().splitlines()[-1]))

    finally:
        stopfront()
        closed = []
        for issuer, subject in grants:
            # Cleanup bypasses the work gate, so resource refusal cannot skip revocation.
            with (r.out / ("revoke-" + subject + ".log")).open("w") as log:
                result = subprocess.run(
                    c
                    + [
                        "exec",
                        "-T",
                        "backend",
                        "python",
                        "-m",
                        "app.security.cli",
                        "revoke",
                        "--issuer",
                        issuer,
                        "--subject",
                        subject,
                        "--output",
                        "/app/security/closed",
                    ],
                    env=r.env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=30,
                )
            closed.append(result.returncode == 0)
        r.report["temporary_grants_revoked"] = all(closed)
        if not all(closed):
            raise RuntimeError("CREDENTIAL_CLEANUP_FAILED")
