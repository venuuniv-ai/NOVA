# NOVA Phase 4 final audit

Date: October 14, 2026 (America/New_York).

**Disposition: PASS within the documented deterministic local/fixture scope,
with optional local inference implemented but not exercised against a real LLM.
Remaining Phase 4 blockers: none identified.** Phase 5 was not started.

## Verified baseline and initial audit

Current HEAD remains Phase 3 checkpoint
`fd656797c60db50c60e78a163595d5ed4017a153`, branch main. Phase 1
`d1d80d687171e992c963e92c797ec924ba815cb5` and Phase 2
`1cecd1b276887241d5e46c77159f76f85cc14bd7` remain unchanged. No checkpoint was
amended; no Phase 4 commit, push, remote configuration or cloud provisioning occurred.

Before implementation, README, architecture, Phase 2/3 architecture and Phase 3
final audit, existing intelligence/proactive modules, kernel integration,
PostgreSQL migrations, Redis/Compose configuration, API patterns, frontend
selection guards and tests were reviewed. The baseline model abstraction was a
real kernel service backed only by deterministic fixtures. No routing, model
usage/cost ledger, response cache, health/circuit, or budget enforcement existed.
The existing approval boundary was application-owned and preserved.

## Architecture implemented

Typed ModelRequest → rule-based privacy/complexity → ModelRouter candidate
policy → scoped signed Redis exact cache → circuit admission / PostgreSQL
budget reservation → FixtureInferenceProvider or optional local compatibility
adapter → strict output/usage validation → server pricing/settlement → durable
ModelCall decision/attempt/accounting record → typed ModelResponse.

InferenceProvider describes provider/model/tier/capability/availability and
normalized generation. FixtureInferenceProvider wraps FixtureModelProvider for
existing structured agents and communication; summary/reasoning demo results
are explicitly deterministic replay, **NOT AN LLM**. Missing tokens remain
UNKNOWN/null and fixture API spend is zero. No reasoning equivalence is claimed.

LocalOpenAICompatibleProvider implements generic local `/v1/models` health
and `/v1/chat/completions` JSON generation through bounded HTTPX transport.
It is disabled by default, does not require credentials, permits an explicitly
configured private local credential, enforces model identity/schema/body/usage
bounds, and normalizes errors. No runtime, model, weights, cloud CLI or vendor
SDK client was installed/launched/downloaded for inference.

**Local runtime: LOCAL RUNTIME NOT CONFIGURED.** No enablement/base URL/model
was present in the session environment or an actual workspace .env. Only the
server-configured endpoint would be checked if explicitly enabled. No arbitrary
port scan was performed. Real local inference, runtime throughput and LLM latency
were not benchmarked; adapter integration was exercised with HTTPX MockTransport.
CloudOpenAICompatibleProvider remains architecture only, with no configured
production cloud transport. Mandatory Semantic Kernel client dependencies
remain installed but unconfigured; their presence is not provider activation.

## Routing, privacy, capability and device policy

PUBLIC/INTERNAL/PERSONAL/SENSITIVE_LOCAL_ONLY and LOW/MEDIUM/HIGH/REASONING are
typed classes. Explicit purposes and context markers raise privacy/complexity;
request declarations cannot lower the inferred privacy floor. Obvious sensitive
markers force local-only. These are deterministic rules, not learned classifiers
or comprehensive PII detection. Classification reasons and exclusions persist.

Routing prefers eligible local capacity for LOW/MEDIUM and the strongest
eligible declared capability for HIGH/REASONING. Reasoning capability explicitly
requires a reasoning route; fixture fallback requires declared REASONING_REPLAY
and is labeled REASONING_REPLAY_LIMITATION. Every fallback independently rechecks
privacy, capability, availability and budget. Provider request mutation cannot
alter authoritative routing input. Bounded candidate chains prevent loops.
No eligible provider returns controlled failure.

Local-only excludes every cloud/external-priced candidate, including failures
and fallback. PERSONAL cloud requires explicit server policy; there is no cloud
provider in the production registry. URLs/API keys cannot be submitted through
routing APIs. Configured local URLs must be loopback or Docker host, without
URL credentials/query/fragment; redirects/proxies are disabled. Actual local
runtime behavior remains an operator trust boundary, including any possible
upstream relay. Known cloud-backed model identifiers are refused.

Desktop permits higher local eligibility, Mobile permits LOW/MEDIUM, Wearable
uses limited fixture eligibility. This is **routing simulation**, not hardware
benchmarking or on-device execution. Local inference runs on the developer host.
FAST preferences exclude SLOW-declared services; strength/latency declarations
are configuration rather than measured scores. A retry after handoff retains
its original captured routing device, while a new request captures the new one.

## Budget, usage, cache and circuit behavior

Model responses accept PROVIDER_REPORTED / LOCAL_ESTIMATED / UNKNOWN provenance.
No tokenizer is installed and no estimated counts are fabricated. Missing usage
is null/UNKNOWN; reported counts must be bounded nonnegative integers with a
consistent total. Cache hits have no fresh tokens or provider-call latency.

Typed Price carries manually configured USD input/output rates, effective date
and source. No current commercial tariff is assumed. Unknown pricing is
COST_UNKNOWN/null and fails closed for external-priced eligibility. Fixture
has $0 API spend; local has $0 external API spend but compute/electricity is
LOCAL_COMPUTE_NOT_PRICED. Configured priced usage is an estimate, not a bill.
The built-in priced probe is explicitly hypothetical test policy.

BudgetPolicy reserves full declared input-context plus capped output exposure
in PostgreSQL before invocation. Daily row locks protect concurrent reservations;
request caps include exposure from previous fallback attempts. Every CLOUD kind
is protected even if its optional priced flag is false. Unknown outcomes retain
the reservation conservatively; success settles to the configured estimate.
UTC defines the budget day, and reservation day persists through midnight.
Startup recovery marks interrupted calls failed and retains outstanding exposure.
Default budgets are zero and do not block fixture/local. No production paid
transport is implemented; priced enforcement is proven using deterministic
in-process test providers, not paid traffic.

Redis caches exact results, not semantic similarity. Keys hash user/task scope,
input/model/policy/settings/schema/mode; no raw prompt is in a key. Local-only
bypasses caching. Bounded TTL defaults to 300 seconds. HMAC binds content to its
key; malformed/tampered/cross-key entries are rejected. Per-process key rotation
forces recomputation after restart. Redis errors do not lose authoritative data.
Signed PERSONAL cache values remain transient plaintext on the trusted local
host: signing is integrity, not encryption.

Owned request UUID locks and separate exact-input guards serialize duplicate
requests/cache stampedes through PostgreSQL advisory locks. Changed input with
an old UUID returns 409. Original UUID retries return metadata without output
or another invocation. ModelCall does not retain complete prompts or generated
content by default. Three consecutive failures open a 30-second process circuit;
one half-open probe is admitted. History is durable, circuit counters ephemeral.
Body reads enforce elapsed deadlines as well as byte/per-operation limits;
pending I/O can require an additional configured timeout before deadline detection.

## Kernel integration and Phase 3 authorization

Explicit `run-routed-agents` registers RoutedModelProvider with the real kernel.
Existing agents keep their typed methods; NOVA routes inside the facade and
actual per-operation providers are recorded under the execution's same trace.
The dinner path still completes six stages with Critic PASS. Agent execution
records identify the facade; the UI links to actual provider history and labels
routed activity accurately. Default Phase 2/3 routes remain fixture-backed.

Explicit `proactive/evaluate-routed` prepares a bounded CommunicationAgent draft
before taking action locks, then hands the validated response/context/trace to
Phase 3. That service revalidates identity/evidence, assigns status, evaluates
REQUIRE_APPROVAL, and hashes its own canonical payload. No routed model can
approve, execute, change approval hashes, edit approved content, or select an
execution adapter. A stronger model receives no new authorization. The routed
model call and proposal share their trace; approval and simulation remain the
same explicit, independently validated Phase 3 operations. No external message
is sent. A preparation that never commits its event may require a new event key
because generated model output is intentionally not durably retained.

## Migration, APIs and UI

Migration `0004_model_routing` adds model_calls and model_budget_days: UUID/FK
request/task/user/trace links, input hashes, classification, decision/candidates,
bounded attempt metadata, accounting response without output, lifecycle/errors,
reservation/day/aggregate exposure, UTC budget amounts, uniqueness, status and
nonnegative budget checks/indexes. Routing persistence lives in the same request
row rather than a duplicated parallel task or separate decision subsystem.

| Method | API |
| --- | --- |
| POST | `/api/v1/model-router/evaluate` |
| GET | `/api/v1/model-router/providers` |
| GET | `/api/v1/model-router/calls` |
| GET | `/api/v1/model-router/budget` |
| GET | `/api/v1/tasks/{id}/model-calls` |
| POST | `/api/v1/tasks/{id}/run-routed-agents` |
| POST | `/api/v1/proactive/evaluate-routed` |

`/models` shows configured health/capabilities, server-defined requests, decision
path/reason codes/candidates, actual model-call/cache/fallback/usage/cost history,
and UTC budget/exposure. Command Center adds a compact real history summary.
No invented savings, throughput, GPU memory or quality score is shown. BUDGET
and FAILURE are explicitly **TEST POLICY FIXTURE / POLICY_REPLAY**, never
production model benchmarks. Parent ownership and task-keyed child guards block
stale reads/acknowledgments and duplicate clicks; only request intent is stored
in browser storage. The 390px screenshot was generated and visually inspected;
responsive checks found no horizontal overflow.

## Actual final validation

82 additional backend cases and seven browser tests were added. All 98 backend
and 19 browser cases from Phases 1–3 remain retained and passing.

| Executed check | Final result |
| --- | --- |
| Full PostgreSQL-backed backend `pytest -q` | **180 passed**: 98 prior + 82 Phase 4 |
| Separate post-implementation adversarial selection | **58 passed**, 24 deselected |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed; 53 Python files formatted |
| Backend `pip check` | No broken requirements |
| Frontend `npm run lint` | Passed |
| Frontend `npm run typecheck` | Passed |
| `NEXT_TELEMETRY_DISABLED=1 npm run build` | Passed |
| `npm audit --audit-level=high` | Zero reported vulnerabilities |
| Backend, backend-tests, frontend Docker image builds | Passed |
| Entire Chromium Playwright suite, retries=0 | **26 passed**: 19 prior + 7 Phase 4 |
| `docker compose config --quiet` | Passed |
| Isolated `alembic downgrade 0003_proactive_actions`, `upgrade head`, `check` | Passed; no drift |
| Application `alembic current` | `0004_model_routing (head)` |
| Application `alembic check` | No new upgrade operations detected |
| `py_compile scripts/acceptance_phase4.py` | Passed |
| Phase 4 acceptance script | Passed |
| Phase 4 acceptance after backend/frontend restart | Passed |
| Original Phase 3 and Phase 2 acceptance after restart | Passed |
| Original Phase 1 continuity after restart | Passed |
| `git diff --check` | Passed |

Full backend validation used the rebuilt test image and isolated ephemeral
PostgreSQL/test-Redis services:

```sh
docker compose --profile test run --rm backend-tests sh -c \
  'alembic downgrade 0003_proactive_actions && alembic upgrade head && alembic check && pytest -q && ruff check . && ruff format --check . && pip check'
```

No application database downgrade occurred. Required checks were actually
executed; final passing results do not rely on hidden retries or fake browser
state. Held-response browser tests delay delivery of real backend results.

## Acceptance and restart evidence

Final task: `8b85f8dd-cdf7-470f-a7f6-7880cd0a39c8`.
Routed proposal: `1a930985-ecdb-40b5-b279-43df3ea51f00`.
Communication trace: `c3d23e0a-0a93-506f-92b9-fd359471e3a3`.

Seven persisted requests cover simple MISS, identical simple HIT, reasoning
limited replay, sensitive local-only BYPASS, budget-denied probe downgrade,
allowed failure fallback, and routed communication preparation. Cache HIT
invoked no provider. The priced probe was never invoked. All default responses
were fixture, token usage remained UNKNOWN, and required API spend was zero.
The proposal remained PENDING_APPROVAL with approval=None and execution=None;
its trace matches the communication ModelCall. Backend tests separately prove
preapproval execution refusal, exact human approval hash and NOT SENT simulation.

After backend/frontend restart and readiness checks, verification retained the
same seven request/trace IDs, decisions, zero consumed/reserved exposure and
pending proposal. Cache contents were not required for those reads. Representative
Phase 3 task `2efed4f2-1ecf-4e4f-8b56-eca91c910ec0` retained proposal, approval,
execution, same hashes/trace/receipt, Mobile and four audits. Phase 2 task
`495411fd-b1ad-4890-90e3-0c679b7078e8` retained six runs, five tools, Critic PASS,
plan and Mobile. Phase 1 task `0251cb6e-c92c-4aee-acfa-9ecf7fd4a80e` retained
Mobile and the three ordered creation/handoff events.

## Adversarial findings and resolutions

All findings below are closed and regression-tested; no historical finding was erased.

- **P4-A01 — High, aggregate request budget:** first draft checked individual
  attempts but not accumulated fallback exposure. Added durable accounted
  exposure; a timed-out priced attempt now blocks a second individually
  affordable attempt that would exceed the request cap.
- **P4-A02 — Cache envelope robustness:** malformed body=null could raise an
  attribute error rather than ERROR/recompute. Added envelope type checks and
  an explicit no-server-failure regression. HMAC poisoning/isolation tests pass.
- **P4-A03 — Failure classification:** no-candidate budget denial initially used
  generic POLICY_BLOCKED. It now records BUDGET_BLOCKED with no invocation.
- **P4-A04 — UI mode truthfulness:** initial inherited fixed fixture labels were
  inaccurate for explicitly routed activity. Added routed disclosure/history
  links and neutral default/optional-local labels; existing fixture labels remain.
- **P4-A05 — Retry after handoff:** recomputing device on original-key acknowledgment
  could create a false key conflict. The API now uses the original owned call's
  captured device; handoff/refresh retains one request and original trace.
- **P4-A06 — High, cloud price flag:** a CLOUD declaration with priced_external=false
  could skip budget checks. Every CLOUD kind now requires reservation/known
  pricing regardless of that optional flag; two regressions prove no invocation.
- **P4-A07 — Reasoning capability:** the fixture exception now explicitly requires
  REASONING_REPLAY. A text-only fixture cannot satisfy a reasoning request, and
  explicit reasoning capability raises classification even if LOW was requested.
- **P4-A08 — Local slow-trickle timeout:** per-read HTTP timeout alone could be
  prolonged by ongoing response bytes. Added elapsed body deadlines and a
  synthetic advancing-stream regression, without a long sleep or real network.

**P4-V01 — new browser assumption, CLOSED:** one intermediate 26-test suite
passed 25 and failed because the new routed-agent test created a generic task
but expected dinner's planner revision/four model calls. The generic task
correctly produced three calls and skipped specialists. The regression now
creates the explicit dinner task and verifies DONE/four calls. The final entire
suite passed 26/26 with zero retries. Initial import/long-line lint findings
were corrected before final checks; no failed required check remains unresolved.

The separate adversarial audit inspected privacy/cloud escape, fallback copies,
unknown/manipulated prices and usage, aggregate/daily reservations and races,
cache signing/isolation/malformed data/stampedes, circuit admission, local URL
control/redirects/timeouts, prompt/error persistence, kernel boundaries, Phase 3
authorization, stale UI response ownership and restart recovery. It reran 58
focused tests after implementation. No paid client or real local LLM was needed.

## Cost, security and scope limitations

Required external API/infrastructure spend: **$0**. Fixture API spend is zero;
optional local inference has zero external API spend with compute/electricity
not priced. No cloud resource, managed service, paid model API, real communication,
model download, installed inference runtime or cloud CLI was used. Real local
inference remains optional and unverified because no endpoint/model was configured.

This is an unauthenticated single-user local demo with loopback application ports.
It is not a public/multi-tenant deployment or OS agent sandbox. Privacy rules
are explicit heuristics, capabilities/prices are trusted server declarations,
and a local runtime's upstream behavior cannot be attested. No production cloud
adapter/billing reconciliation exists. Unknown priced outcomes conservatively
consume exposure, which can under-utilize budget. Circuit/recovery/cache signing
are single-process; multi-worker coordination is not claimed. Generated content
is absent from model-call history, so some interrupted draft preparations need
a new key. Routed preparation can compute a draft before final cooldown refusal.

Cache values are local plaintext with integrity protection and TTL; not encrypted
personal-data storage. The existing frozen proactive demo clock and lazy expiry
remain documented. Polling, separate reads, 100-record history limits and no
hosted CI are retained. Advisory/Python/container vulnerability scanning and
penetration testing were not performed; npm audit/pip checks are not certification.
The Playwright environment-color warning is non-failing.

No VLM/image/audio/camera pipeline, real hardware/account/calendar/contact/message,
vector memory, Kafka/Go gateway, full telemetry, deployment infrastructure,
OAuth, bandits, experimentation, shadow/canary rollout or Phase 5 work was added.

## Files and Git

38 Phase 4 files: 12 tracked modifications and 26 additions, including this audit.
The manifest follows. No generated dependency, screenshot/trace, build, cache,
bytecode, database artifact, actual .env or credential is included. `.env.example`
contains disabled local settings and a local URL only. Candidate sizes are bounded
source/configuration/docs/test text. Source review distinguishes intentional
malicious dummy URL/token test data from real credentials.

```text
.env.example
README.md
backend/app/config.py
backend/app/main.py
backend/app/model_routing/__init__.py
backend/app/model_routing/api.py
backend/app/model_routing/budget.py
backend/app/model_routing/cache.py
backend/app/model_routing/circuit.py
backend/app/model_routing/contracts.py
backend/app/model_routing/kernel_provider.py
backend/app/model_routing/models.py
backend/app/model_routing/policy.py
backend/app/model_routing/providers.py
backend/app/model_routing/registry.py
backend/app/model_routing/replay.py
backend/app/model_routing/router.py
backend/app/model_routing/service.py
backend/app/proactive/service.py
backend/migrations/env.py
backend/migrations/versions/0004_model_routing_model_routing.py
backend/tests/conftest.py
backend/tests/test_model_routing.py
compose.yaml
docs/adr/0004-model-routing-and-privacy.md
docs/adr/0005-model-budgets-cache-and-accounting.md
docs/architecture.md
docs/phase-4-architecture.md
docs/phase-4-final-audit.md
frontend/app/globals.css
frontend/app/models/page.tsx
frontend/components/intelligence-workspace.tsx
frontend/components/model-workspace.tsx
frontend/components/nova-workspace.tsx
frontend/lib/models.ts
frontend/styles/models.css
frontend/tests/models.spec.ts
scripts/acceptance_phase4.py
```

HEAD remains `fd656797c60db50c60e78a163595d5ed4017a153`, branch main,
three preserved commits, empty index. All Phase 4 changes remain unstaged/untracked.
No commit/amendment, push or remote configuration occurred.

## Local operation and final disposition

```sh
docker compose up --build -d --wait
python3 scripts/acceptance_phase4.py
# After backend/frontend restart, verify the printed task ID:
python3 scripts/acceptance_phase4.py --verify-task TASK_ID
```

Open `http://localhost:3000/models?task=TASK_ID` or use Command Center's Model
Router link. API docs are at `http://localhost:8000/docs`. Validation containers
were stopped after completion; persistent application volumes and acceptance
records were preserved. No database volume was deleted.

**Final result: Phase 4 accepted for the documented local deterministic scope.
Real local inference is optional and not configured. Remaining blockers: none
identified. Phase 4 is not committed; Phase 5 was not started.**
