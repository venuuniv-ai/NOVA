# NOVA local operations runbook

Never run cleanup, probes or deployment commands against an unrelated/shared
installation. Application data uses named PostgreSQL/media/Redis/Kafka/auth volumes.
Do not use `down -v`, delete volumes or downgrade the application database.

## Start and authentication

```sh
docker compose -f compose.yaml -f compose.phase8.yaml up --build -d --wait
docker compose exec -T backend python -m app.security.cli provision \
  --subject local-operator --output /app/security/operator.token
```

The overlay defaults to local JWT mode; base Compose is explicit legacy fixture
replay and is unsuitable for public exposure. Open /auth and use the private
operator-issued token (expires within one hour). Keys are generated inside the
private auth volume. Tokens never belong in source, URLs or browser localStorage.
/auth/session uses an HttpOnly SameSite cookie and checks Origin on mutations.
The backend's signature, issuer, audience, expiry, local grants, enabled identity
and device checks remain mandatory even when bypassing the Go gateway.

Provision a second subject without --user-id to create an isolated local user
and three simulated device contexts. Bind an existing user's UUID only as an
operator. Roles are owner, viewer, approver and operator, stored server-side.
`python -m app.security.cli revoke --subject SUBJECT --output /tmp/unused` disables
a subject and invalidates its tokens. Reprovisioning increments local token version.

GET /api/v1/auth/devices lists the caller's contexts. POST /auth/devices/register
with an owned device_id registers/re-enrolls it; POST /auth/devices/{id}/revoke
immediately refuses its credentials and new handoffs using it. Local registration
epochs require a freshly issued token (`--device-type MOBILE`, for example).
These are simulated identities, not hardware attestation or real wearable pairing.
Revocation does not erase task/device history. Revoking your last context requires
operator recovery; never remove historical device rows to work around it.

## Optional real local OIDC

```sh
docker compose -f compose.yaml -f compose.phase8.yaml -f compose.oidc.yaml up --build -d --wait
# Wait for http://localhost:8180/realms/nova/.well-known/openid-configuration
python3 scripts/provision_oidc.py
```

Open /auth/oidc. The Keycloak realm uses authorization code + S256 PKCE, a bounded
HttpOnly state/verifier cookie, a fixed redirect and short-lived RS256 access JWTs.
FastAPI checks the configured issuer/audience/JWKS, local subject grant and signed
owned device claim. The browser never supplies role authority. The provisioner
creates only a controlled local fixture account; its private password is saved in
ignored .secrets. Keycloak's generated bootstrap password stays in its own volume.
No paid/external identity account is used. This is start-dev, localhost HTTP; it is
not an internet OIDC deployment. A production issuer/TLS/secret manager requires
separate deployment work and authorization. JWKS refresh is bounded and cached
for 60 seconds; provision trusted key rotation deliberately.

## Events and failures

POST /api/v1/operations/tasks/{id}/subscribe explicitly enables fixture proactive
review for future Desktop→Wearable handoffs. Consumers cannot approve or execute.
The job calls the existing draft service with its original event-derived key.
Human approval and simulation use the existing canonical payload/hash policy.

GET /operations/tasks/{id} shows owned outbox status, sequence, attempts, consumer
receipts and draft jobs. POST /operations/events/{id}/retry resets only a DEAD
owned publication; POST /operations/jobs/{id}/retry resets a DEAD owned draft job.
Neither changes payloads, task IDs or approval rights. Domain-recorded failures
remain recorded; correcting a deterministic failed scenario may require a new
explicit event, not repeatedly retrying a known rejected input.

Publication awaits a broker acknowledgment before marking PUBLISHED. A crash
between broker acknowledgment and DB commit can redeliver. Consumer inbox claims
and projection/job effects commit together; Kafka offsets commit afterward.
Untrusted/malformed messages are recorded as bounded fingerprints/reasons in
PostgreSQL dead letters, never raw content. Unexpected DB failures leave offsets
uncommitted and workers restart. This is not exactly-once Kafka delivery.
Per-task unpublished/dead predecessors block later outbox events until recovery.
Publication and draft retries are bounded/backed off. Draft jobs use a DB advisory
lock and an idempotent domain key to recover an interrupted RUNNING job.

```sh
# Explicit operator fault probe; local broker stops and is restarted in finally.
NOVA_TOKEN_A='runtime-token' python3 scripts/reliability_phase8.py --tasks 20 --outage
# Do not put the actual token into shell history; prefer an environment populated
# from the private file using a local operator wrapper.
```

If Kafka is unavailable, business writes still commit with pending outbox rows.
Fix the broker, observe backlog drain, and inspect DEAD rows before replay. Do not
clear inboxes or change event IDs to suppress evidence of duplicate delivery.
A single broker/replication factor 1 is a local demonstration, not HA or zero loss
under disk destruction. Back up application database/media separately.

## Observability and health

Gateway 8080, frontend 3000, API 8000, Keycloak 8180 and diagnostics bind only to
loopback. Prometheus is at 9090, Tempo at 3200 and local Grafana at 3001. Grafana's
anonymous Viewer is deliberately local. Backend/worker spans export through the
Collector; event envelopes propagate trace context, not authorization. Attributes
use route templates/method/status, never request bodies, tokens or memory text.
These traces and logs are metadata, not encrypted personal-data storage.

Internal application/state/telemetry/identity networks separate clients from
storage. Dedicated host-facing diagnostic bridges allow published loopback ports;
this does not establish a general outbound firewall for every process.
Gateway limits are process-local, with bounded identity/IP buckets and timeouts.
FastAPI /health/live reports process liveness and /health/ready verifies the DB and
seed. A running worker or observability container alone is not proof of healthy
end-to-end delivery; use actual receipts, scrape samples and trace queries.

## Deployment and safe shutdown

See infrastructure/kubernetes/README.md for the local kind target, and
infrastructure/terraform for a kind-context-only provider with no cloud resources.
Terraform defaults to namespace-only; deploy_local_stack is an explicit opt-in.
A policy-enforcing CNI is needed to prove Kubernetes NetworkPolicy enforcement.
The audit distinguishes rendering/validation from actual rollout results.
CI is deterministic and disables external model tests; its hosted execution is
not implied by a local workflow file.

```sh
docker compose -f compose.yaml -f compose.phase8.yaml -f compose.oidc.yaml stop
```

Stop preserves volumes. Monitor free host disk and Docker memory before loading
another cluster or building images; generated build cache can consume substantial
space. Remove only disposable task-owned clusters/cache, never application volumes.
