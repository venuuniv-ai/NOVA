# NOVA Core

**NOVA v1.0 local MVP: READY on the prepared local host — FIXTURE AI default;
real inference disabled.** Phase 10 is checkpointed and Phase 11 offline qualification
passed. Startup, authentication, grounded fixture workflows, drafts/HITL, recovery
and shutdown were verified without additional real inference. Services are stopped
after validation. See the [local release guide](docs/local-release-guide.md) and
[test evidence](docs/local-release-test-evidence.md).

Earlier phase introductions below retain their historical scope.

**Phase 8 local infrastructure.**
The authenticated local overlay adds a Go gateway, server-owned RBAC/resource
ownership, revocable simulated device identities, an atomic PostgreSQL outbox,
real local Kafka consumers and draft-only proactive jobs. Open `/operations` for
actual owned delivery evidence and `/auth` for login. Approval and execution stay
inside FastAPI; execution remains SIMULATED / NOT SENT.

```sh
docker compose -f compose.yaml -f compose.phase8.yaml up --build -d --wait
docker compose exec -T backend python -m app.security.cli provision \
  --subject local-operator --output /app/security/operator.token
```

The base Compose stack is explicitly legacy local replay. The Phase 8 overlay
defaults to short-lived local JWT authentication; the additional compose.oidc.yaml
profile enables local Keycloak authorization-code/S256 PKCE. No credentials or
models are bundled. Required external spend remains $0. See the
[implementation reference](docs/phase-8-implementation-spec.md),
[architecture](docs/phase-8-architecture.md), [runbook](docs/phase-8-runbook.md) and
[actual final audit](docs/phase-8-final-audit.md) for verification boundaries,
including the Kubernetes rollout limitation. Phase 9 was not started.

**Phase 7 evaluation and experimentation.**
Open `/evals` for the versioned 104-scenario golden dataset, SMOKE/REGRESSION/FULL
runs, actual evidence and grader failures, explicit metric denominators,
regression gates, and paired offline A/B, SHADOW and CANARY simulations.
Fixture evaluation measures the documented local system, not production
reliability, real CV accuracy, real semantic quality or real-user usefulness.
REAL LLM JUDGE NOT CONFIGURED. Real embeddings/CLIP/DINOv2/SAM/VLM remain
unconfigured and unexercised. Required external spend remains $0.

```sh
docker compose up --build -d --wait
python3 scripts/acceptance_phase7.py
docker compose exec backend python -m app.evaluation.cli --suite REGRESSION
```

See [Phase 7 architecture](docs/phase-7-architecture.md) and
[final audit](docs/phase-7-final-audit.md). The deterministic CI command exits
nonzero on failed gates. The cautious-threshold candidate can lose useful fixture
suggestions; results are measured and reported without assuming a candidate win.
Phase 8 adds local security and event infrastructure; Phase 9 has not been started.

**Phase 6 controlled memory and personalization.**
Open `/memory` for explicit memories, pending visual candidates, confirmation,
correction/supersession/deletion, history and explainable hybrid retrieval.
Existing fixture preferences are now persisted with FIXTURE origin. User and
confirmed inferred memories retain distinct provenance in the real kernel agent
workflow. Memory never authorizes an action or changes human approval.

PostgreSQL 17 is extended locally with pgvector; its existing volume is preserved.
Exact structured, full-text and vector source ranks combine via RRF k=60.
Default 32-dimensional fixture embeddings prove infrastructure, **NOT REAL
SEMANTIC QUALITY**. No real embedding model/endpoint is configured, no model
weights or ML framework is downloaded, and no cloud embedding is enabled.

```sh
docker compose up --build -d --wait
python3 scripts/acceptance_phase6.py
python3 scripts/acceptance_phase6.py --verify-task TASK_ID
```

See [Phase 6 architecture](docs/phase-6-architecture.md),
[lifecycle/provenance ADR](docs/adr/0008-memory-lifecycle-and-provenance.md),
[retrieval ADR](docs/adr/0009-memory-hybrid-retrieval-and-pgvector.md), and
[final audit](docs/phase-6-final-audit.md).
Required external spend is $0; local compute/electricity is not priced.
Phase 7 adds fixture evaluation; Phase 8 adds local security and event infrastructure; Phase 9 has not been started.

**Phase 5 multimodal perception and visual context.**
Open `/perception` to attach NOVA's controlled wearable frame or upload a JPEG,
PNG or WEBP. Images are validated, orientation-normalized, stripped of metadata
and persisted as private sanitized PNGs. Fixture observations are explicit
simulation, not real visual inference. Optional CLIP/DINOv2/SAM adapters load
existing local model directories only; no ML stack or weights are downloaded.

Visual context reaches the existing Context/Planner/Critic workflow with media,
processor and simulation provenance. The existing ModelRouter records VISION;
visual evidence grants no authority, never becomes permanent memory and cannot
approve or execute a proposal. Phase 3 human approval remains required.

```sh
docker compose up --build -d --wait
python3 scripts/acceptance_phase5.py
python3 scripts/acceptance_phase5.py --verify-task TASK_ID
```

See [Phase 5 architecture](docs/phase-5-architecture.md),
[visual responsibility ADR](docs/adr/0006-multimodal-provenance-and-responsibility.md),
[media storage ADR](docs/adr/0007-media-privacy-and-local-storage.md), and
[Phase 5 final audit](docs/phase-5-final-audit.md).
REAL CLIP / DINOV2 / SAM / VLM are not configured by default. Required external
API/infrastructure spend is $0; local compute/electricity is not priced.
Phase 6 adds controlled persistent memory; Phase 7 adds fixture evaluation; Phase 8 adds local security and event infrastructure; Phase 9 has not been started.

**Phase 4 model intelligence and policy routing.**
Open `/models` for declared providers, health, explainable routes, UTC budget
exposure and actual persisted model-call/cache/usage records. Fixture is the
complete default and is **NOT AN LLM**. Optional generic local text inference
requires an explicitly configured, already-running compatibility endpoint.
No inference software or weights are installed/downloaded automatically.

Routing rechecks privacy, capability, budget and availability before fallback.
Sensitive-local-only never becomes cloud eligible. PostgreSQL reserves priced
exposure before invocation and enforces aggregate request and daily limits.
Redis caches scoped signed exact results with bounded TTL; it does not own
budgets, tasks, approvals or audit. ModelCall does not retain prompts or output.

Required external API/infrastructure spend is **$0**. Local inference has $0
external API spend; compute/electricity is not priced. No paid provider is
configured or implemented. Budget/failure demonstrations use labeled synthetic
POLICY_REPLAY probes, with no paid transport or fabricated model benchmark.
No local runtime is configured by default; application/tests do not require one.

See [Phase 4 architecture](docs/phase-4-architecture.md),
[routing/privacy ADR](docs/adr/0004-model-routing-and-privacy.md),
[budget/cache ADR](docs/adr/0005-model-budgets-cache-and-accounting.md), and
[Phase 4 final audit](docs/phase-4-final-audit.md).

```sh
docker compose up --build -d --wait
python3 scripts/acceptance_phase4.py
# After restarting backend/frontend, verify the printed task ID:
python3 scripts/acceptance_phase4.py --verify-task TASK_ID
```

Local configuration defaults are in `.env.example`; set `LOCAL_MODEL_ENABLED`,
`LOCAL_MODEL_BASE_URL` and `LOCAL_MODEL_NAME` only for an already-running local
runtime/model. No model download is implied. Default Phase 2/3 agent APIs remain
fixture-backed. Explicit `run-routed-agents` and `proactive/evaluate-routed`
paths demonstrate model abstraction while preserving the same approval policy:
models can draft, never approve or execute. The routed draft stays pending until
an explicit human decision; simulation still sends no external message.
Phase 5 adds the perception layer described above; Phase 6 adds controlled persistent memory; Phase 7 adds fixture evaluation; Phase 8 adds local security and event infrastructure; Phase 9 has not been started.

**Phase 3 proactive intelligence and human approval.**
Command Center receives a synthetic context event at fixture time 13:31:
Architecture Review at 14:00 requires 35 minutes of travel. NOVA computes
29 minutes available and six minutes of lateness risk, prepares a draft, and
requires explicit approval. `/approvals` supports edit, approve, reject, and a
separate **Execute simulation** step. **No external message is sent.**

Proposals, exact payload-bound approval, simulated receipt, and audit survive
refreshes, application restarts, and Desktop → Wearable → Mobile handoffs.
Redis provides bounded deduplication/cooldowns; outages suppress new suggestions.
All operation remains local and requires $0 paid API/infrastructure spend.
The clock is deliberately frozen for this demo; expiration is server-enforced
against the injected clock and tested with an advanced fixture clock.

See [Phase 3 architecture](docs/phase-3-architecture.md),
[approval ADR](docs/adr/0002-human-approval-boundary.md),
[Redis ADR](docs/adr/0003-redis-proactive-cooldowns.md), and
[Phase 3 final audit](docs/phase-3-final-audit.md).

```sh
docker compose up --build -d --wait
python3 scripts/acceptance_phase3.py
# After restarting backend/frontend, use the task ID printed above:
python3 scripts/acceptance_phase3.py --verify-task TASK_ID
```

Additional Phase 3 APIs are listed in the architecture document and FastAPI
OpenAPI at `http://localhost:8000/docs`. All earlier routes and tests remain.
No real calendar, travel, account, AI inference, or communication is connected.
Phase 4 adds the model intelligence described above. Phase 5 adds the perception layer described above; Phase 6 adds controlled persistent memory; Phase 7 adds fixture evaluation; Phase 8 adds local security and event infrastructure; Phase 9 has not been started.

**Phase 2 multi-agent core**, built on the verified
Phase 1 continuity foundation described below. Open **NOVA Intelligence** for
the persisted agent graph, plugin evidence, planner revisions, and final plan.
The provider is **FIXTURE / DETERMINISTIC**: it is not an LLM. All calendar,
preference, and location context is visibly synthetic demo data.

See [Phase 2 architecture](docs/phase-2-architecture.md),
[Semantic Kernel ADR](docs/adr/0001-semantic-kernel.md), and
[Phase 2 final audit](docs/phase-2-final-audit.md).

## Phase 2 intelligence

Five specialized agents implement Context, Planner, Calendar, Memory, and
Critic responsibilities. Semantic Kernel registers/discovers/invokes three
bounded native plugins and resolves the fixture provider service. NOVA owns
authorization, transactional execution claims, idempotency, persistence,
failure recovery, and deterministic policy enforcement.

For the dinner demonstration, six agent stages retrieve synthetic meeting and
explicit preference evidence, revise the plan, and obtain Critic PASS. Agent
records, tool calls, context, and plan remain attached to the same task through
Desktop → Wearable → Mobile. Agents unnecessary for a task are marked SKIPPED
without invocation. Restaurant discovery, booking, or message sending is not
implemented.

Additional endpoints:

```text
POST /api/v1/tasks/{id}/run-agents   {"idempotency_key":"your-request-key"}
GET  /api/v1/tasks/{id}/agent-runs
GET  /api/v1/tasks/{id}/agent-runs/{run_id}
GET  /api/v1/tasks/{id}/plan
```

Intelligence runs use validated typed contracts and real PostgreSQL execution
state. Exact-key retries reuse the original execution; competing new keys are
rejected while it is running. Fixture execution is synchronous in a FastAPI
worker thread; no broker or hosted worker is required. On application restart,
abandoned RUNNING executions are marked FAILED rather than portrayed as done.

The existing local startup command applies both migrations automatically.
Phase 2 requires no external API keys or paid services. Semantic Kernel's
mandatory SDK dependencies include commercial-client and telemetry packages;
NOVA does not configure those clients, credentials, exporters, or services.
The only registered model service is FixtureModelProvider.

```sh
python3 scripts/acceptance_phase2.py
docker compose restart backend frontend
docker compose up -d --wait
python3 scripts/acceptance_phase2.py --verify-task TASK_ID_FROM_PREVIOUS_OUTPUT
```

The complete backend and Playwright suites cover both phases, including
Phase 1 F-01 regressions and the Phase 2 adversarial races. Runtime dependencies
are constrained by `backend/requirements.lock.txt`; native Python installation
can use `pip install -r backend/requirements-dev.txt -c backend/requirements.lock.txt`.

NOVA is a research and portfolio project toward a proactive multimodal personal
AI operating system. Phase 1 implements its cross-device continuity foundation:
a task keeps the same identity and persisted context as it moves between
**Desktop → Wearable → Mobile**.

This phase uses real FastAPI and PostgreSQL state. The three devices are
explicitly simulated contexts. It performs no model execution, scheduling,
restaurant search, or hardware integration.

## Why continuity comes first

NOVA is designed around persistent tasks and their transitions rather than a
chat transcript. Phase 1 proves that a task can be created in one context,
continued in another, refreshed, and recovered after an application restart.
The dinner task is a deterministic example of work to continue; its text is
stored, not interpreted by an AI system.

## What Phase 1 includes

- One seeded demo user and exactly three simulated device types.
- Task creation on Desktop with an atomic `TASK_CREATED` event.
- Transactional Desktop → Wearable → Mobile handoffs of the **same task**.
- Idempotency keys, historical retries, conflicting-key detection, and
  PostgreSQL row locks for concurrent requests.
- Command center, device continuity, and task detail views backed by the API.
- Loading, empty, error, offline, and recovery states.
- PostgreSQL named-volume persistence and Alembic migrations.
- JSON backend request logs and correlation IDs.
- Redis configured locally without an invented application dependency.

## Architecture

```text
Browser → Next.js :3000 → same-origin /api/v1 gateway → FastAPI :8000
                                                       ↓
                                                SQLAlchemy + psycopg
                                                       ↓
                                                PostgreSQL :5432

Redis :6379 is available locally but is not used by Phase 1 application code.
```

Next.js uses the App Router and TypeScript. Its server gateway reads
`API_INTERNAL_URL` at runtime, so the same build works with a local backend or
the Compose `backend` service. Requests and responses are not cached. FastAPI
owns validation, task transitions, and persistence; the browser does not own
task state.

See [docs/architecture.md](docs/architecture.md) for schema, consistency,
idempotency, and design decisions.

## Local setup — $0 services

Prerequisite: Docker with Docker Compose. Native frontend checks also require
Node.js 24+ and npm. The backend container uses Python 3.12.

From the repository root:

```sh
cp .env.example .env
docker compose config --quiet
docker compose up --build -d
```

Open:

- Frontend: <http://localhost:3000>
- Interactive API documentation: <http://localhost:8000/docs>
- Liveness: <http://localhost:8000/health/live>
- Readiness: <http://localhost:8000/health/ready>

Backend startup applies migrations and seeds the demo user/devices
idempotently. It does not create example tasks automatically. Create the
pre-filled dinner task in the UI to start the demonstration.

```sh
docker compose ps
docker compose logs -f backend
docker compose restart backend frontend
docker compose down
```

Normal shutdown/restart preserves named database volumes. Avoid
`docker compose down --volumes` unless you intentionally want to erase local
database and Redis data.

Published ports bind to `127.0.0.1`. Override the documented port variables in
`.env` if needed. `DATABASE_URL` in `.env.example` is for native backend
development; Compose supplies its own container network URL. Use URL-safe
characters if changing the demonstration PostgreSQL password.

### Native development with local Docker databases

```sh
docker compose up -d postgres redis
python3.12 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements-dev.txt
cd backend
.venv/bin/alembic upgrade head
.venv/bin/python -m app.seed
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In another terminal:

```sh
cd frontend
npm ci
npm run dev
```

For native backend development, export `DATABASE_URL` when changing database
credentials or ports. Its defaults work with the unmodified Compose setup.
Set `API_INTERNAL_URL` for a non-default native backend URL. No external fonts,
API keys, model downloads, or hosted services are required.

## API

| Method | Path | Behavior |
| --- | --- | --- |
| POST | `/api/v1/tasks` | Create a Desktop task and its creation event; HTTP 201 |
| GET | `/api/v1/tasks` | List demo-user tasks, newest first; `limit` 1–200, `offset` ≥ 0 |
| GET | `/api/v1/tasks/{id}` | Read a persisted task |
| POST | `/api/v1/tasks/{id}/handoff` | Atomically move a task, or acknowledge an original retry |
| GET | `/api/v1/tasks/{id}/events` | Return events in ascending per-task sequence |
| GET | `/api/v1/devices` | List the three seeded device contexts in continuity order |
| GET | `/health/live` | Process liveness without querying the database |
| GET | `/health/ready` | Database, migrated task table, and seeded device readiness |

All task/device operations use the server-owned demo user. Caller-supplied
`user_id` fields are rejected on creation and handoff inputs.

Creation body:

```json
{
  "title": "Find somewhere for dinner with Sarah tomorrow after my meeting.",
  "description": "Continue this dinner planning task across devices.",
  "origin_device_id": "00000000-0000-4000-8000-000000000010"
}
```

Handoff body:

```json
{
  "source_device_id": "00000000-0000-4000-8000-000000000010",
  "target_device_id": "00000000-0000-4000-8000-000000000020",
  "idempotency_key": "desktop-wearable-example-001"
}
```

The response contains `task`, `event`, and `replayed`. An exact retry returns
the original event and the **current task state**, even after later handoffs.
It does not revert the task or alter `updated_at`. Reusing a key for a different
source/target returns HTTP 409. Keys are scoped to a task and accept 1–128
ASCII letters, digits, `.`, `_`, `:`, and `-`, starting with a letter or digit.

Validation errors and unknown devices return HTTP 422; unknown tasks return
HTTP 404; invalid transitions or stale sources return HTTP 409. Operational
database failures return HTTP 503. API errors contain `error.code`,
`error.message`, and `correlation_id`; schema errors also contain field details.
Responses echo or generate `X-Correlation-ID`.

## Tests and checks

The backend tests use **real PostgreSQL** in an isolated, ephemeral `nova_test`
database. They refuse to truncate any database whose name does not end in
`_test`. The application database is not used for test cleanup.

```sh
docker compose --profile test run --build --rm backend-tests
docker compose --profile test run --rm backend-tests ruff check .
docker compose --profile test run --rm backend-tests ruff format --check .
docker compose config --quiet
docker compose exec backend alembic check
docker compose exec backend alembic current
```

The pytest session applies the actual migration and checks model/schema drift.
Tests cover creation, database persistence, lifecycle recovery, events, task
identity, invalid devices/transitions, key validation, exact retries,
conflicting keys, task-scoped keys, and concurrent handoffs.

```sh
cd frontend
npm ci
npm run typecheck
npm run lint
npm run build
npm audit --audit-level=high
```

For browser acceptance tests, first start the complete Compose stack. Browser
tests create persistent demonstration tasks in the application database.
Fault-state browser tests explicitly intercept requests to exercise failure
handling; the continuity acceptance test uses the real API throughout.

```sh
cd frontend
npx playwright install chromium
npm run test:e2e
```

Screenshots and failure traces go to ignored `frontend/test-results/`.
Override `E2E_BASE_URL` if the frontend port differs.

### Acceptance flow

In the UI, create the pre-filled task on Desktop. Open Device continuity,
continue on Wearable, and refresh. Continue on Mobile and refresh again. Open
Task detail and retry the original Desktop → Wearable event. The task ID stays
constant and the event history contains exactly three events.

An additional reproducible REST acceptance script is available:

```sh
python3 scripts/acceptance.py
docker compose restart backend frontend
python3 scripts/acceptance.py --verify-task TASK_ID_FROM_PREVIOUS_OUTPUT
```

It creates one task, verifies both transitions and subsequent reads, and retries
the first handoff after the second. The second command pair verifies that the
completed task survives application service restarts. See
[docs/verification.md](docs/verification.md) for checks actually executed during
implementation.

## Security philosophy

Phase 1 is a local demonstration with a single demo user, not a public
multi-user service. It intentionally has no authentication or OAuth. Anyone
able to reach the API can operate on demo tasks. Keep it bound to localhost;
do not expose this stack publicly as-is.

Use validated UUIDs and bounded request fields, ORM parameter binding,
server-selected user ownership, explicit transition rules, transactional
updates, and database constraints. UI text is rendered as text rather than
HTML. The same-origin gateway forwards only the versioned API. Backend
containers and the frontend runtime run as non-root users. Logs avoid request
bodies, task text, credentials, and API keys. `.env` and generated artifacts
are ignored. The sample database password is for local development only.

Before a future public or multi-user deployment, add authentication,
authorization, request limits, origin/CSRF protections, secret management, and
deployment-specific hardening. These are not implemented in Phase 1.

## Costs and roadmap

Phase 1 requires no paid services and makes no model API calls. Dependency
installation and container image pulls require internet access; runtime task
operations use local services. Full cost rules live in [AGENTS.md](AGENTS.md).

Later phases may introduce optional small local models, additional provider
adapters, real tool integrations, budget-aware routing, clearly labeled replay
demos, and justified observability infrastructure. Kafka, RAG, VLMs, external
integrations, cloud deployments, and real hardware integrations remain
**planned only**. Phase 3 adds only the documented synthetic proactive/approval flow.


## Phase 9 local inference integration

**Phase 9 COMPLETE — bounded local acceptance and final qualification, October 19, 2026.**
Explicit FIXTURE / LOCAL_REAL / DISABLED modes, versioned embeddings, checkpointed
reindexing and owned grounding are implemented at `/inference`. Real BGE inference,
reindex/retrieval, Qwen structured generation and sequential residency were demonstrated.
The opt-in SELECTION_V1 contract passed both owner-authenticated positive grounding
and conditional insufficiency abstention; original UUID/quote and privacy checks passed.
Citations are attached by the application after independent answer verification.
Historical legacy abstention failures remain preserved in the audit.

Final qualification: 700 backend passes/one explicit real-model skip, 13 controller
passes, Go race/vet, frontend lint/typecheck/build, 56 browser cases across replay/
local-auth/OIDC profiles, baseline golden FULL 104/104, SMOKE 10/10, REGRESSION 25/25,
and local Kafka duplicate/forgery/HITL/outage recovery. These are finite local checks,
not general model quality, production capacity or security certification. The cautious
negative-control candidate remains 23/25 with gate FAIL.

SELECTION_V1 independently supports a narrow named-subject preference subset; unknown
question forms receive no asserted supporting context. Insufficiency acceptance used
empty selected evidence, not calibrated semantic rejection. General entailment,
vision inference and a real LLM judge remain unqualified. Phase 8 Kubernetes and
NetworkPolicy limitations remain unchanged. See [architecture](docs/phase-9-architecture.md)
and the [final audit](docs/phase-9-final-audit.md) for exact evidence and limits.

All qualification/model services are stopped and private real configurations disabled.
FIXTURE and legacy EXTRACTIVE_V1 remain defaults; real activation requires a new scoped
approval and fresh resource checks. No automatic downloads, paid services or external
messages. The [staging manifest](docs/phase-9-staging-manifest.md) is prepared for review;
nothing has been staged or committed. Phase 10 has not started.

## Phase 10 owned evidence drafts

Phase 9 was subsequently checkpointed locally at
`7765b33736c28ccc560fc8269bb5fc4b9b050518`; its audit remains historical evidence.
Phase 10 now extends existing jobs, proposals and Approval Center with explicitly
requested, owned preference drafts. Named cuisine/beverage questions can select
eligible owned memories automatically or use supplied memory references. Context
and source bindings, current authorization and conflicts are checked before
generation and before the atomic proposal/job commit. Cancellation, expiry,
rejection, duplicate delivery and interrupted processing are handled durably.

FIXTURE remains the default. Phase 10 drafts stop at PENDING_APPROVAL; approval,
editing and execution are disabled for this contract. No external action is sent.
The private managed SELECTION_V1 adapter passed the authorized R2 real case:
Qwen generated `noodles`, index 0; the application independently verified original
citation, source binding, current permissions/privacy and conflicts. One DONE job
created one PENDING_APPROVAL proposal, with no approval or execution. R1's earlier
swap failure remains historical. The Desktop registration stays enabled/version 1.

Final-source qualification passed: 750 backend tests/one explicit real-model skip,
17 controller tests, Go race/vet, frontend lint/typecheck/build, 58 browser cases
across four passing invocations, Kafka/recovery and golden baselines. This qualifies
the named-preference drafting subset, not general autonomous reasoning, semantic
entailment, model quality or production deployment. See the
[architecture](docs/phase-10-architecture.md),
[audit](docs/phase-10-implementation-audit.md) and
[R2 outcome](docs/phase-10-real-acceptance-proposal-r2.md).

Temporary credentials were revoked; scoped real settings disabled, attestations
closed and model/task services stopped. Data, vectors, artifacts and volumes are
preserved. The single authorized R2 attempt is consumed; no additional inference,
Git checkpoint, deployment or Phase 11 follows from completion.

## Phase 11 local reliability and operational qualification

Phase 11 adds bounded event/job pages to Local Operations, with owner-scoped
sequence cursors, a captured append boundary and metadata-only diagnostics.
The UI supports independent page continuation, refresh, safe errors and stale-task
response suppression. Draft authority and source/privacy checks remain unchanged.

Run `python3 scripts/qualify_phase11.py` for the staged local qualification, using
existing images and installed tools. It refuses competing containers/listeners,
unsafe resources, protected data mounts and real-provider settings. It creates a
fresh isolated project with collision-checked private subnets, preserves existing
network restrictions, records ignored per-stage evidence, and stops its own
services without deleting volumes. `--stages` supports focused checks; a subset
success is explicitly PARTIAL_PASS. No model generation is part of this command.

See the [Phase 11 architecture](docs/phase-11-architecture.md),
[audit](docs/phase-11-implementation-audit.md) and
[test evidence](docs/phase-11-test-evidence.md) for current acceptance and limits.
Phase 11 changes remain uncommitted pending separate checkpoint authorization.


## Launch the verified local candidate

```sh
./scripts/start-local.sh
python3 scripts/nova_local.py status
pbcopy < .secrets/release-v1/operator.token
# Open http://localhost:3000/auth and paste the private short-lived token.
# When finished:
./scripts/stop-local.sh
```

No package installation, image pull/build, cloud service, model load or external
action is performed by startup. Existing dependencies are required; the installed
native frontend is built only if needed. For smoke, credential refresh, recovery,
rollback and deferred P1/P2 items, use the release guide/checklist. The source
candidate is 1.0.0-local-rc1; working changes remain uncommitted and are protected
by the reviewed runtime source manifest. Phase 11 completion is bounded offline
qualification, not production or general model-quality sign-off.
