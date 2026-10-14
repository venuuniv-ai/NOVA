# NOVA Core

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

Future phases may introduce provider abstractions, deterministic AI fixtures,
optional small local models, budget enforcement, clearly labeled replay demos,
and justified orchestration/observability infrastructure. Agents, Semantic
Kernel, Kafka, RAG, VLMs, external integrations, cloud deployments, and real
hardware integrations are **planned only**, not implemented or simulated here.
