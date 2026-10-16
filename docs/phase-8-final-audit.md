# NOVA Phase 8 final audit

Report finalized: October 16, 2026 (America/New_York).
The later bounded deployment verification is recorded at the end of this report;
it stopped at resource preflight and did not resolve Kubernetes sign-off.
Validation measurements below were collected October 15, 2026.

**Disposition: local Compose functionality and deterministic regression checks
pass. Deployment sign-off remains qualified: an actual local Kubernetes backend
rollout timed out under host resource pressure. Full Kubernetes rollout and
NetworkPolicy enforcement are not verified.** Do not interpret configuration
validation as a successful cluster deployment. Phase 9 was not started.

**REAL EMBEDDING MODEL NOT CONFIGURED.** Fixture embeddings test persistence,
isolation and ranking infrastructure; they are **not a real semantic model**.
Real CLIP, DINOv2, SAM and VLM inference remain unconfigured and unexercised.
**REAL LLM JUDGE NOT CONFIGURED.** The 104/104 result evaluates deterministic
local fixture behavior, not production reliability or general model quality.

## Baseline and implementation scope

Work continues from Phase 7 checkpoint
`6fb2e803c9c2a1422bfdc45d2352efdbd2b84872`, branch main. All seven Phase 1–7
checkpoint commits remain unchanged. No staging, commit, amendment, push, remote
configuration, cloud provisioning or model download was performed.

The conversation's approved requirements were captured in
[implementation reference](phase-8-implementation-spec.md), then implemented in
security → gateway → events → observability → deployment/reliability order.
See [architecture](phase-8-architecture.md) and [runbook](phase-8-runbook.md).
Working local components include authentication and owned resources, real Go
routing, PostgreSQL outbox/inboxes, a real Kafka broker and three consumer groups,
proactive draft jobs, local OIDC login, Collector/Tempo/Prometheus/Grafana and an
Operations UI. Deployment artifacts are included with the limitations below.

## Authentication, authorization and ownership

FastAPI validates credentials independently of the gateway. Local credentials
use a generated private-volume signing key. Optional local Keycloak uses actual
RS256 OIDC access tokens, issuer/audience/JWKS validation, authorization code and
S256 PKCE. Algorithms are fixed; issuer, subject, audience, expiry and issuance
are validated. OIDC nbf is optional and validated when present; local nbf is
required. Bounded JWKS retrieval has a trusted configured endpoint and cache.
No commercial identity service or real external account is required.

Server-owned identity grants map issuer/subject to a User UUID and enabled roles.
JWT role claims and identity headers cannot grant privileges. Viewer reads,
owner mutations, approver approval/simulation and operator evaluation/operations
are checked by FastAPI. Queries and service constructors now use the captured
owner rather than a hard-coded demo owner. Existing task UUIDs, memory IDs,
fixture provenance and canonical approval hashes remain compatible.

Owned device registration/revocation preserves the three simulated contexts and
historical rows. Disabled identities/devices are refused. Local token versions
prevent old credentials reviving after reenrollment. OIDC credentials must be
issued strictly after the device registration epoch; same-second reenrollment
requires a newly issued token in a later second. This is simulated device
identity, not hardware attestation.

The application default is fail-closed local authentication. Base Compose
explicitly selects legacy `AUTH_MODE=demo` for retained fixture/replay use; the
Phase 8 overlay defaults to local mode. Neither mode is a public production
deployment. Internal fixture/evaluation operations retain their explicit demo
principal outside HTTP; untrusted HTTP requests cannot select that authority.

Next.js provides /auth, an HttpOnly SameSite session cookie, canonical-origin
checks on cookie-authenticated mutations, and bounded token/session input.
The OIDC callback checks state/verifier, uses a fixed canonical redirect and
clears its private PKCE cookie. Credentials are absent from URLs, browser
localStorage, source and committed artifacts. Local Keycloak runs start-dev on
loopback HTTP, with its bootstrap password inside a private volume. Its fixture
password file is ignored. Production TLS/issuer/secret management is not claimed.

## Gateway and event invariants

The Go gateway routes only to the configured FastAPI upstream, restricts paths
and methods, caps request/header sizes, enforces timeouts and bounded process-local
IP/identity/device rate limits, and strips forged identity headers. It validates
identity through FastAPI and forwards the original bearer credential. FastAPI
then independently revalidates authentication, ownership and policy. The gateway
does not mint approval authority or accept model-selected upstreams.

Scoped SQLAlchemy mapper hooks insert outbox metadata on the **same PostgreSQL
connection and transaction** as supported task, event, execution, proposal,
approval, memory and perception lifecycle writes. Rollback removes both business
write and outbox event. This is scoped lifecycle instrumentation, not universal
CDC. Evaluation temporary-schema writes are excluded.

The publisher locks pending rows, preserves per-task sequence, uses task UUID as
Kafka key, awaits broker acknowledgment and only afterward commits PUBLISHED.
A crash after broker acknowledgment can redeliver. Kafka delivery is deliberately
at least once. Three groups implement projection, proactive scheduling and audit.
Each verifies bounded envelopes against the authoritative committed outbox,
commits its unique consumer/event inbox claim with its business effect, then
commits the Kafka offset. Old projection sequences cannot overwrite newer ones.
Duplicate delivery cannot create a second draft job or change task identity.

Publication retries are bounded to eight attempts with backoff; failed rows can
be inspected/retried through owned operator routes. Malformed/forged Kafka data
becomes a bounded reason/fingerprint dead letter, without raw payload retention.
Transient database failure leaves offsets uncommitted. Draft jobs use bounded
five-attempt retry, an advisory lock and the original event-derived domain key.
Crash-after-domain-commit recovery replays the original result.

An explicit owned task subscription enables fixture proactive draft preparation
for Desktop → Wearable. Workers have owner authority only. **Events and model
outputs cannot approve or execute.** FastAPI's payload/hash-bound human approval
and existing simulation service remain authoritative; communication is NOT SENT.
No Kafka event is interpreted as a human approval or execution command.

Migrations 0008_security_outbox, 0009_device_registration and
0010_event_retry_bounds add the identity/device and event persistence/constraints.
Application head is `0010_event_retry_bounds`; Alembic reports no schema drift.
New routes cover auth/me, device registration/revocation, owned operations event
history, task subscriptions/status and event/job retry. Existing API routes are
retained. /operations shows actual database receipts/jobs and allows explicit
subscription; /auth supports private local tokens or configured OIDC login.

## Observability and local infrastructure

Actual HTTP and worker spans propagate W3C context through the outbox and Kafka.
Structured logs distinguish correlation IDs, domain execution trace IDs and OTel
trace IDs. Metrics use route templates/method/status and elapsed HTTP durations;
attributes exclude request bodies, credentials and memory text.

A real Tempo query for trace `b235c91666c2413802c071959fa1ff6f` returned FastAPI
and three event-worker batches. At the capture point Prometheus returned 476
scraped HTTP requests; Grafana reported database health ok. The Collector exports
locally to Tempo and Prometheus; Grafana panels use actual HTTP rate/P95 data.
These observations prove local data flow, not a comprehensive monitoring SLO.
Raw traces/screenshots remain outside the source change set.

Compose separates edge, application, internal state, telemetry and identity
networks, with dedicated loopback diagnostic bridges. An actual frontend-container
TCP probe to PostgreSQL's state-network address was blocked. This proves that
specific network boundary, not a universal outbound firewall. Runtime images
use non-root users and relevant read-only/capability/privilege restrictions.
Kafka is a single KRaft broker with three partitions and replication factor one.
All required services are local open-source components; required external spend
is **$0**. Host compute/electricity is unpriced.

Kubernetes manifests include the application, Kafka, workers, observability,
configuration, PVCs, resource limits, restricted pods and explicit network edges.
Kustomize rendering passed. Terraform uses only a local kind Kubernetes provider,
defaults to namespace-only and requires opt-in for stack objects. Init, formatting
and validation passed. A validation invocation that mounted only the Terraform
folder could not resolve sibling manifests; mounting infrastructure as a unit
corrected the invocation. No Terraform plan/apply or cloud provider was used.

An actual disposable kind cluster was created, core images loaded and core
manifests applied. Backend rollout timed out while Docker/host disk and memory
were constrained. The task-owned cluster was removed; application volumes were
preserved. The subsequently completed full pipeline manifest was rendered, not
rolled out. **Full cluster readiness and CNI NetworkPolicy enforcement remain
unverified.** No production deployment or Kubernetes reliability claim is made.
The deterministic GitHub Actions workflow exists but was not executed on hosted
CI. Its checks disable external model tests and require no paid inference.

## Actual validation

| Executed check | Actual result / boundary |
| --- | --- |
| PostgreSQL-backed full backend suite | **495 passed**: 470 retained + 25 Phase 8; final rebuilt-image run 92.85 seconds; security-default run also passed |
| Backend ruff check / format --check | Passed; 107 Python files formatted |
| Backend pip check | No broken requirements |
| Isolated migration downgrade to 0007 / upgrade head / check | Passed; application database was never downgraded |
| Application Alembic current / check | 0010_event_retry_bounds; no new upgrade operations |
| pgvector version / completed evaluation namespace inspection | 0.8.7; zero leftover nova_eval schemas |
| Go formatting / go test -race ./... / go vet ./... | Passed; race tests also execute during gateway build |
| Frontend lint / typecheck / native production build | Passed; /auth and /operations included |
| npm audit --audit-level=high | Zero reported vulnerabilities |
| Backend / backend-tests / frontend / gateway Docker builds | Passed |
| Compose configuration, including OIDC overlay | Passed |
| Retained entire browser suite, retries=0 | **48 passed**, five profile-specific cases explicitly skipped |
| Strict local-auth browser profile | **3 passed**, 13.4 seconds |
| Real local Keycloak OIDC browser profile | **2 passed**, 4.1 seconds |
| CLI REGRESSION baseline / cautious candidate | 25/25, exit 0 / 23/25, expected exit 1 |
| Direct FastAPI and Go forged-header probe without bearer | Both refused with HTTP 401 |
| Final-source FULL golden evaluation | **104/104**, critical violations 0, gate PASS |
| AB / SHADOW / CANARY comparisons | Baseline 25/25 versus cautious 23/25; candidate gates FAIL as expected |
| Actual Kafka duplicate/forgery acceptance | Passed; three duplicate deliveries, three forged-message dead letters, no duplicate effects |
| Local load and broker outage/recovery | Passed; measurements below |
| Backend/frontend/PostgreSQL/Kafka/worker restart verification | Passed for Phase 8 and representative Phases 1–7 |
| Collector / Tempo / Prometheus / Grafana data flow | Actual trace, scrape and health responses verified |
| Compose frontend → PostgreSQL isolation probe | Connection blocked |
| Kubernetes rendering | Passed; actual rollout timed out, full deployment not verified |
| Terraform init / fmt / validate | Passed; plan/apply not executed |
| Hosted CI, penetration test, Python/container advisory scans | Not executed |
| Git whitespace and candidate secret/artifact review | Passed; no staging/commit |

Final rebuilt-image backend/migration/CLI validation ran against isolated test
PostgreSQL, not the application database:

```sh
docker compose --profile test run --rm backend-tests sh -c \
  'alembic upgrade head && alembic downgrade 0007_evaluation_experimentation && alembic upgrade head && alembic check && pytest -q && ruff check . && ruff format --check . && pip check && python -m app.evaluation.cli --suite REGRESSION'
# The separate cautious CLI invocation returned the expected exit 1:
docker compose --profile test run --rm backend-tests \
  python -m app.evaluation.cli --suite REGRESSION --configuration CAUTIOUS_THRESHOLD
```

The final validation wrapper explicitly asserted that cautious exit status 1 was
the expected regression result. Scenario failure-path tests emit execution_failed
logs deliberately; these are not an unreported failed final test command.

Browser coverage is **53 cases across three profiles**, not one claimed 53-pass
invocation. Security tests disable trace capture to avoid retaining credentials.
Held-response tests use real backend results. Fixtures do not make network model
calls. Historical measured baseline/dataset and previous audit files are unchanged.

The 25 added backend cases exercise signature/issuer/claim/role boundaries,
resource ownership, revocation/reenrollment, forged identity headers, atomic
rollback, publication failure/crash acknowledgment, duplicate/concurrent/out-of-order
consumption, malformed event dead letters, draft-job crash recovery and refusal
to approve, plus standalone-process evaluator model registration.

## Actual acceptance, reliability and persistence

Phase 8 acceptance task: `dbe37ef4-1e9f-4c89-9075-2bc14cb87d67`.
It retains the same UUID on Mobile, nine outbox events, three consumer groups,
one proactive job and proposal `8ad53b70-698a-4e59-ba08-50ce1767d3b9`.
Human approval is payload/hash-bound; execution is SIMULATED / NOT SENT.
Three injected duplicate Kafka deliveries did not duplicate business effects.
A forged approval-like envelope was refused by all three consumers and produced
three dead letters. Restart verification retained the same task/job/proposal and
approval evidence. No external message was sent.

The sequential local continuity load created 20 tasks and measured 61 HTTP
requests: P50 **20.915 ms**, P95 **60.124 ms**, workflow requests **1.607 s**,
and all consumers caught up after **2.123 s**. Each task kept its UUID and exactly
three continuity events. This is a one-client fixture probe, not a throughput,
concurrent-user, saturation, long-duration or production benchmark.

During an actual stopped-broker probe, task
`a1e6e54d-df65-4ec4-8c55-55bc39a3ca7e` committed with pending outbox state.
After broker restart, its two events reached consumers in **31.731 s** measured
from the restart command. Its UUID and business state persisted. This tests a
broker process outage, not broker disk destruction, replica failover or database
backup restore.

Final-source golden run: `8740ab2f-9be6-4658-8892-a04b0b99d6bb`.
AB `b817ca64-6908-42b1-9499-655ff3bd251a`, SHADOW
`cd1bb0e0-895c-4c05-8376-f7807473590f`, CANARY
`7f3d10ea-c869-406b-8410-64dc9a6a02d8` preserve truthful candidate regressions.
Python source fingerprint:
`cdf322d6dc7a2c9e41c8668ae3527ebc077bd23c75ba638e86db626f161e5249`.
The final application image contains this source. Earlier completed run
`60c015c9-7f9e-47f3-bbcb-d678a496ae0c` and its experiment assignments were
reverified after restart; a final security-default configuration change was then
checked by the fresh 104-case run above. No scores or historical baseline were
edited to obtain a pass. The cautious candidate remains 25/25 → 23/25.

Representative restart records passed:

| Phase | Task | Preserved evidence |
| --- | --- | --- |
| 6 | 4cfcb0e7-91ee-48a3-bde2-d5addc4cbc6d | Fresh post-browser memory acceptance: lifecycle, embeddings, history, plan, media and unapproved proposal |
| 5 | 85f85ceb-9129-4ea3-942e-29f34fe4516f | Media/hash, fixture perception, plan, VISION call, pending proposal, Mobile |
| 4 | 8b85f8dd-cdf7-470f-a7f6-7880cd0a39c8 | Seven routing records/traces/decisions and pending proposal |
| 3 | 2efed4f2-1ecf-4e4f-8b56-eca91c910ec0 | Approval/execution hashes, NOT SENT receipt, audits, Mobile |
| 2 | 495411fd-b1ad-4890-90e3-0c679b7078e8 | Six runs, five tools, Critic PASS, plan, Mobile |
| 1 | 0251cb6e-c92c-4aee-acfa-9ecf7fd4a80e | Same UUID, Mobile, three original continuity events |

## Findings, corrections and unresolved limits

- Initial outbox insertion ran before the task FK existed. Moved insertion to
  mapper after-insert/update using the original connection; atomic rollback and
  actual creation/consumer tests pass.
- Local Keycloak initially omitted its custom device claim. Added an explicitly
  admin-managed profile attribute and audience mapper. Real PKCE login passed.
- Initial OIDC validation required nbf although Keycloak valid access tokens omit
  it. Made it optional only for OIDC, still validated when present; local tokens
  retain the required claim. Invalid claim regressions pass.
- Next callback/Origin logic initially used an internal container origin. Added
  a fixed canonical public origin; actual login/callback/cookie tests pass.
- An intermediate retained browser run passed 47/48 and exposed missing model
  registration in a standalone evaluator process. Centralized complete model
  registration before schema cloning and added a fresh-process regression.
  The final retained suite passes 48/48 without retries.
- Early lint, fixture assertions, new test selectors and Playwright trace-setting
  placement were corrected. One fresh golden invocation was started while Compose
  recreated the backend and lost its HTTP connection; after readiness completed,
  the fresh run above passed. These earlier failures are not counted as passes.
- Docker stalled under simultaneous cluster/build workload and low host disk.
  Docker was restarted, only the disposable cluster and unused build cache were
  removed, and validation was batched. Application volumes were never deleted.
  Kubernetes rollout remains the explicit unresolved deployment verification gap.

Remaining boundaries: single-user-style local operation with owned additional
users, no production tenancy/security certification; local HTTP OIDC and trusted
operator provisioning; simulated devices; process-local rate limits, circuit and
startup recovery; single application process and broker; no distributed durable
job platform or HA guarantees. Outbox instrumentation covers named lifecycle
models rather than every possible SQL write. Consumer inboxes and domain keys
protect supported effects, not arbitrary future integrations.

Telemetry/diagnostic services are local and are not an encrypted retention or
production access-control system. Kubernetes policies need a suitable CNI and
an actual successful full rollout. Terraform plan/apply, hosted CI, penetration
testing, vulnerability certification, sustained/high-concurrency load and disaster
restore remain unverified. Required paid services remain zero. No Phase 9 work.

## Files, Git and local operation

83 changed/new text files: **29 modified and 54 added**, including this audit.
The largest candidate is the approximately 52 KB Kubernetes pipeline configuration.
All candidates are UTF-8 text; no binary, actual .env, private key/token, personal
image, runtime memory/media/database, model weight, dependency directory, cache,
screenshot, browser trace or build output is included. A credential-pattern match
in the Kubernetes README is an environment-variable placeholder, not a credential.
Terraform's dependency lock file is intended configuration; .terraform is ignored.
Private operator tokens/passwords remain in ignored files or named volumes.

```text
.env.example
.github/workflows/local-regression.yml
.gitignore
README.md
backend/Dockerfile
backend/app/config.py
backend/app/database.py
backend/app/evaluation/api.py
backend/app/evaluation/experiments.py
backend/app/evaluation/isolation.py
backend/app/evaluation/runner.py
backend/app/events/__init__.py
backend/app/events/api.py
backend/app/events/models.py
backend/app/events/outbox.py
backend/app/events/pipeline.py
backend/app/events/worker.py
backend/app/logging.py
backend/app/main.py
backend/app/memory/plugin.py
backend/app/memory/service.py
backend/app/model_registry.py
backend/app/model_routing/api.py
backend/app/model_routing/kernel_provider.py
backend/app/perception/api.py
backend/app/perception/media.py
backend/app/proactive/api.py
backend/app/proactive/service.py
backend/app/security/__init__.py
backend/app/security/api.py
backend/app/security/auth.py
backend/app/security/bootstrap.py
backend/app/security/cli.py
backend/app/security/identity.py
backend/app/security/models.py
backend/app/service.py
backend/app/telemetry.py
backend/migrations/env.py
backend/migrations/versions/0008_security_outbox_security_outbox.py
backend/migrations/versions/0009_device_registration.py
backend/migrations/versions/0010_event_retry_bounds_event_retry_bounds.py
backend/requirements.lock.txt
backend/requirements.txt
backend/tests/conftest.py
backend/tests/test_phase8.py
compose.oidc.yaml
compose.phase8.yaml
compose.yaml
docs/architecture.md
docs/phase-8-architecture.md
docs/phase-8-final-audit.md
docs/phase-8-implementation-spec.md
docs/phase-8-runbook.md
frontend/app/api/[...path]/route.ts
frontend/app/auth/oidc/callback/route.ts
frontend/app/auth/oidc/route.ts
frontend/app/auth/page.tsx
frontend/app/auth/session/route.ts
frontend/app/operations/page.tsx
frontend/components/nova-workspace.tsx
frontend/tests/security.spec.ts
gateway/Dockerfile
gateway/go.mod
gateway/main.go
gateway/main_test.go
infrastructure/kubernetes/README.md
infrastructure/kubernetes/application.yaml
infrastructure/kubernetes/kustomization.yaml
infrastructure/kubernetes/namespace.yaml
infrastructure/kubernetes/network-policy.yaml
infrastructure/kubernetes/pipeline.yaml
infrastructure/observability/collector.yaml
infrastructure/observability/grafana/dashboards/nova.json
infrastructure/observability/grafana/dashboards/provider.yaml
infrastructure/observability/grafana/datasources/local.yaml
infrastructure/observability/prometheus.yaml
infrastructure/observability/tempo.yaml
infrastructure/oidc/realm.json
infrastructure/terraform/.terraform.lock.hcl
infrastructure/terraform/main.tf
scripts/acceptance_phase8.py
scripts/provision_oidc.py
scripts/reliability_phase8.py
```

Branch main; HEAD remains `6fb2e803c9c2a1422bfdc45d2352efdbd2b84872`.
The index is empty. All Phase 8 changes are unstaged/untracked for review. All
seven earlier checkpoints remain unchanged. No commit, push or remote was made.
Validation containers are stopped after checks with PostgreSQL/media/Redis/Kafka/
auth/identity volumes preserved. No application volume was deleted or flushed.

```sh
docker compose -f compose.yaml -f compose.phase8.yaml up --build -d --wait
docker compose exec -T backend python -m app.security.cli provision \
  --subject local-operator --output /app/security/operator.token
# Open http://localhost:3000/auth and use the private operator-issued token.
# Optional local OIDC:
docker compose -f compose.yaml -f compose.phase8.yaml -f compose.oidc.yaml up --build -d --wait
python3 scripts/provision_oidc.py
```

The runbook describes private credential handling, acceptance/outage probes,
subscription/retry operations, diagnostics and safe shutdown. **Final result:
working local Phase 8 implementation and deterministic regression evidence;
Kubernetes deployment sign-off remains unresolved. No real inference, paid
service, commit or Phase 9 implementation.**

## Bounded final deployment verification — October 16, 2026

**Result: BLOCKED AT RESOURCE PREFLIGHT. No new cluster was created. Kubernetes
readiness, NetworkPolicy enforcement, security acceptance and regression remain
unverified.** Earlier Compose results above are not Kubernetes results. This is
the single bounded verification requested after the implementation audit; there
was no cluster retry or Docker restart in this verification.

### Resources, previous bottleneck and protection

Read-only inspection measured:

| Resource | Actual observation |
| --- | --- |
| Host physical memory | 8,589,934,592 bytes (8 GiB) |
| Docker Desktop memory allocation | 4,106,604,544 bytes (3.825 GiB) |
| Docker logical CPUs | 8 |
| Host data volume | 228 GiB total, 197 GiB used, **3.7 GiB available**, 99% capacity |
| Host swap | 6,144 MiB total, **5,534.44 MiB used**, 609.56 MiB free |
| macOS memory_pressure | 34% reported system-wide free percentage; substantial compression/swap, not a guarantee of available container RAM |
| Docker images | 16, reported 7.522 GB total |
| Docker build cache | 8.046 GB, reported 6.385 GB reclaimable; no cache was deleted |
| Docker volumes | 17, reported 2.511 GB; no volume was deleted |
| Active containers / kind clusters | None / none |

The previous safe rollout log contains `Waiting for deployment spec update to be
observed...` followed by `error: timed out waiting for the condition`. The earlier
application log confirms five core deployments and network policies were applied.
No retained pod-event/OOM/eviction diagnostics establish a more specific cause.
The original audit reported host resource pressure; today's limited disk, small
Docker memory allocation and swap pressure substantiate the capacity concern,
but **do not prove a historical pod-level root cause**.

Protected existing volumes were inspected by name and creation metadata before
and after this verification: nova_postgres_data, nova_media_data, nova_redis_data,
nova_kafka_data, nova_auth_data and nova_keycloak_data. Metadata remained identical.
Their containers remain stopped. No mounts, writes, pruning, volume removal,
application migration or data reset was performed. The existing PostgreSQL volume
was never attached to a disposable cluster.

### Fixed budget and stop decision

The bounded budget was one local attempt, at most 12 minutes, no Docker restart,
no resource-allocation increase, no image build, no cloud resource and no cleanup
of existing images, caches or volumes. A prospective cluster would have one
control-plane node, no worker nodes, an isolated kubeconfig/context, disabled
kind default CNI and an explicitly installed policy-enforcing CNI. The node would
be capped at 2 CPUs / 3 GiB; the attempt would stop rather than exceed the current
Docker allocation. **These are proposed bounds, not an actual created cluster
configuration. No Kubernetes version, CNI version or CNI health was verified.**

A hard pre-creation requirement was **at least 8 GiB host free disk**. This is an
operator safety threshold, not a Kubernetes vendor minimum. The existing unique
core application/database/cache/broker images report roughly 2.4 GB of image
size, observability images roughly another 1.9 GB, and the cached kind node image
roughly 1.3 GB. Importing images into the nested node store, unpacking a CNI,
creating writable layers/PVCs and retaining a host reserve can require additional
space even when Docker already has source images. Reported image sizes are not
an exact incremental-disk forecast. With only 3.7 GiB available, proceeding would
risk the same host-wide pressure and persistent Docker storage. The gate failed
before any cluster create, pull, load or deployment mutation. No additional
attempt was made. No claim is made that a larger allocation alone would resolve
all deployment issues.

Read-only commands actually executed included:

```sh
sysctl hw.memsize
sysctl vm.swapusage
memory_pressure
df -h / /System/Volumes/Data
docker info --format '{{json .}}'
docker system df
docker volume ls
docker volume inspect nova_postgres_data nova_media_data nova_redis_data nova_kafka_data nova_auth_data nova_keycloak_data
docker ps --format '{{.Names}}'
/tmp/nova-kind get clusters
cat /tmp/nova-phase8-kube-apply.log
cat /tmp/nova-phase8-kube-rollout.log
```

Existing Kubernetes manifests, resource declarations, architecture, runbook and
local deployment README were read. Safe inventory/diagnostic captures are in
`/tmp/nova-phase8-deployment-verification`, outside the repository; they contain
resource/volume metadata, not credentials or business data. There are no new pod
events to capture because no cluster/pods were created. `kind create`, CNI install,
`kind load`, `kubectl apply`, port-forward and authenticated acceptance commands
were **not executed** in this attempt.

### Actual verification matrix

| Required verification | This Kubernetes attempt |
| --- | --- |
| Disposable cluster / active enforcing CNI health | Not executed; disk preflight failed |
| Apply existing Phase 8 configuration | Not executed |
| Migration / backend readiness | Not executed; no Kubernetes migration status |
| Gateway / frontend readiness | Not executed; no ready application pods |
| Kafka / publisher / consumer connectivity | Not executed |
| Collector / Tempo / Prometheus / Grafana readiness | Not executed |
| Authorized gateway → backend allowed | Not tested |
| Unauthorized pod → backend denied | Not tested |
| Authorized backend → PostgreSQL allowed | Not tested |
| Frontend → PostgreSQL denied | Not tested |
| Independent FastAPI credentials / ownership | Not tested against Kubernetes |
| Events cannot authorize / payload-bound approval | Not tested against Kubernetes |
| Targeted authenticated acceptance | Not executed |
| Representative Phase 7 regression | Not executed |

**No NetworkPolicy enforcement claim is made.** No active enforcing CNI existed
in this verification. Historical Compose security/event/approval results remain
separate evidence. No workload, model or message adapter was invoked, and no real
external message was sent.

Remaining blocker: insufficient safe local disk headroom, alongside constrained
Docker memory and host swap pressure. The prior unresolved Kubernetes deployment
limitation is preserved. Resumption requires adequate host resources and another
explicitly requested bounded attempt, followed by actual policy-enforcing CNI,
readiness, connectivity, authenticated security and regression checks. No passing
Kubernetes result or closure is inferred from a rendered manifest or Compose.

Only this audit documentation was changed during this final deployment
verification. HEAD remains `6fb2e803c9c2a1422bfdc45d2352efdbd2b84872`, branch
main; index empty, all seven checkpoint commits unchanged, no remote configured,
no commit/push, no Phase 9. Required external spend for this attempt: $0.
