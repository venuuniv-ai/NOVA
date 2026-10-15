# Phase 7: reproducible fixture evaluation and offline experiments

## Baseline inventory

Checkpoint fd2d054bd384a0d270f969b00c785bef4eb68cda provides persistent task
continuity; five-agent Semantic Kernel orchestration; bounded tool records and
Critic policy; proactive triggers and exact human approval; model routing,
accounting and budgets; sanitized fixture perception; and controlled memory with
PostgreSQL full-text/pgvector retrieval. Existing acceptance scripts cover restart
persistence. There was no versioned cross-system evaluation runner, experiment
assignment, comparison, persisted regression gate or Evaluation Lab.

These are the measurable subsystems. The new platform does not invent a real
calendar, restaurant tool, cloud inference, real computer vision, real semantic
embedding model or real-user utility labels.

## Data and methodology

`backend/app/evaluation/datasets/nova-golden-v1.json` is the repository-owned
nova-golden dataset, version 1.0.0, with 104 distinct scenarios: continuity 15,
agents 16, proactive 17, routing 16, perception 15, memory 15, end-to-end 10.
Each scenario has its own ID/version/category, initial fixture state, bounded
case identifier, typed checks and suite/safety/metamorphic tags. Checks define
observation field, comparison operation, expected value, grader, metric and
severity. They encode expected agents/tools/arguments/context/policy/output and
forbidden behavior without executable dataset code. No upload/expected-result
API exists. Only fixed server operation handlers execute.

Dataset name/version and every scenario version persist with a SHA-256 content
hash. Reusing an installed dataset version with changed bytes is refused. A change
to expected results requires a dataset or scenario version change. Existing run
results retain their own expected/observed checks. Run identity binds input intent,
configuration, source fingerprint, dataset/fixture/grader/gate versions, seed 0,
provider mode, suite and judge mode. UUIDs and elapsed times vary; outcomes and
assignment algorithms are deterministic. `code_checkpoint` is null when no build
checkpoint environment value is supplied; the hash of actual Python source is
always recorded, rather than claiming an uncommitted tree equals a checkpoint.

SMOKE selects 10 tagged cases; REGRESSION selects 25; FULL selects all 104.
Scenario-specific task success requires every defined check to pass. ERROR also
fails task success. Deterministic grader types are EXACT_MATCH, SET_MATCH,
TRACE_MATCH, RULE_BASED, DETERMINISTIC and POLICY. Grading supports bounded inert
dictionary lookup and equality, inequality, containment/exclusion, set and upper
bound checks. A missing observation fails, including negative expectations.

Agent checks inspect actual persisted agent/status/order/tool traces; generic
work must skip specialists. Tool checks cover recorded function selection and
known arguments, plus invalid argument/allowlist rejection. Calendar task text
remains omitted from stored arguments. Plan checks cover fixture evidence,
Sarah/Italian, Critic PASS, missing constraints, unsupported output and bounded
correction. Scope is documented fixture behavior, not general natural-language
reasoning quality.

Memory checks call the actual MemoryService and compare actual bound expected
UUIDs, lifecycle, ownership, scope, ranks and provenance. Defined positive cases
calculate Recall@5 and reciprocal rank; cases without positive expected IDs do
not enter those denominators. Perception checks execute ingestion, processors,
VISION routing and context, or reject invalid schema/geometry/provenance. Synthetic
instruction-bearing VLM text is exercised as untrusted data, not real OCR.
Routing checks include classification, privacy, cache/replay, every priced
provider attempt, budget denial and fallback. Proactive cases use defined fixture
labels for thresholds, suppression and proposals; they do not establish user utility.

## Metrics, gates and judge boundary

Each metric records name, numerator, applicable denominator, value, units and
methodology. Agent/tool/memory/perception/routing/proactive/policy compliance is
passing applicable named checks / all applicable named checks. This is not a
claim that partial tool expectations constitute comprehensive precision/recall.
Task success is passing scenarios / executed scenarios. Zero applicable samples
produce null, never an invented perfect score. Nonfinite, negative-denominator
and inconsistent ratio inputs are rejected.

Fixture latency measures actual wall time around scenario reset/setup and flow,
not real-model latency. With at least 20 observations, P50 is the median and P95
the nearest-rank percentile; smaller samples report unavailable. Known API cost
sums actual Phase 4 configured estimates only. Unknown cost, fixture zero API
spend and unpriced local compute are separately counted; missing prices/tokens
are never invented. No paid inference is enabled.

Predeclared gates-v1 blocks any critical invariant failure, any execution error,
fixture task success below 0.95, or measured fixture P95 above 60 seconds. Latency
with insufficient samples is NOT_APPLICABLE. Comparison adds a maximum 0.02
absolute task-success drop. Thresholds were fixed before final measured acceptance.
Failure severity is INFO/LOW/MEDIUM/HIGH/CRITICAL. Critical counts and failed gates
remain visible alongside aggregate rates; a judge cannot overrule them.

Judge is an abstract interface with typed bounded rubric request/response.
Default disabled. FixtureJudge tests orchestration using a nonempty-content
rubric, not reasoning/coherence quality: FIXTURE JUDGE / NOT REAL LLM-AS-JUDGE.
It has no tools, policy decisions or configurable rubric supplied by output text.
REAL LLM JUDGE NOT CONFIGURED. No real judge adapter/inference is exercised or
required; future model judging must use Phase 4 routing and explicit enablement.

## Isolation and runner lifecycle

POST claims a durable RUNNING row with an owned idempotency key and request hash,
then schedules a local background worker. Exact replay acknowledges the original
run; changed intent returns 409. User locks and partial unique indexes serialize
evaluations and experiments. One local evaluation slot exists per owner. Background
work is single-process, not a distributed durable queue.

The runner creates a temporary server-UUID PostgreSQL schema with the business
schema, then reseeds fresh state before every scenario. A ContextVar and SQLAlchemy
connection-checkout hook scope SessionLocal and advisory-lock connections to that
schema. Search path contains only the isolated schema and pg_catalog, with no
public business-table fallback. pgvector's public cosine operator is explicitly
qualified. Checkout resets public requests' search path and statement timeout.
Contexts propagate through asyncio/to_thread and reset in finally blocks. Scenario
SQL has a 15-second statement timeout. The dataset cannot select SQL, schema,
filesystem paths, code or normal user identity.

Actual task, agent, memory, perception, router and proactive services execute
against isolated state. Runtime inference is fixture-only even if optional local
models are configured. Redis cache keys use the evaluation namespace and bounded
TTL. Proactive cooldowns use an evaluation-local deterministic adapter; the durable
service still records suppression and enforces approval. Evaluation proves that
adapter boundary, while earlier suites retain actual Redis behavior tests.

Between scenarios, only scoped generated media are removed and only scoped
business tables are reset. At completion, temporary schema state is dropped.
Compact normalized observations, actual trace/observation/memory IDs, bounded
accounting and grader snapshots persist in public evaluation tables. Those trace
IDs identify temporary evaluation artifacts; they are not links to normal Task
Detail or claims that deleted temporary business rows remain queryable.

Startup marks interrupted runs/experiments failed, never successful. Known
interrupted run schemas/media are cleaned by their server-generated run UUID.
This assumes one application process. This is application isolation using a
trusted database role, not an OS sandbox or database-role security certification.

## Experiments and allocation

Immutable definitions compare BASELINE proactive threshold 2 minutes with
CAUTIOUS_THRESHOLD 10 minutes. Only evaluation constructor parameters differ;
normal demo defaults remain 2. Explicit safety setups retain their established
inputs so a candidate cannot evade a safety check merely by suppressing setup.

Assignment uses SHA-256(experiment UUID + scenario identity), modulo 10,000;
bucket < percentage * 100 selects candidate. Definition and assignment persist;
there is no random reassignment on refresh/restart. Small-sample realized counts
need not equal the configured percentage exactly.

AB, SHADOW SIMULATION and CANARY SIMULATION are paired offline replays of eligible
inputs. Both configurations are measured; persisted buckets select the simulated
served outcome for aggregate allocation results. This does not avoid candidate
measurement calls and is not production traffic routing/shadowing/canary rollout.
Reports compare paired task/policy/tool/latency/cost metrics and actual denominators.
They state INSUFFICIENT SAMPLE SIZE / NO STATISTICAL SIGNIFICANCE CLAIM.

Shadow uses only its own disposable schema. Application-level shadow guards
refuse approve and execute; scenarios requiring positive approval/execution are
excluded from both paired shadow runs and the eligible count reflects that.
Normal unauthorized-attempt tests still execute and must be blocked. Canary can
exercise fixture human approvals in isolation, but exact HITL and NOT SENT
simulation remain required. Public business-state hashes before/after experiments
verify no changes without copying personal values into reports. Concurrent normal
user changes may affect that comparison; the platform does not attribute their
cause or claim an OS-level write sandbox.

The cautious candidate may suppress labeled useful proposals. Such losses are
reported as quality regressions; a manufactured candidate win is not required.

## Persistence, APIs and UI

Migration 0007_evaluation_experimentation adds evaluation_datasets,
evaluation_runs, evaluation_scenario_results, experiment_definitions,
experiment_assignments and experiment_results. UUIDs/FKs, version/key uniqueness,
status checks, elapsed constraints, owned active-run indexes and bounded generated
JSON support the local scope. Graders/metrics/gates are nested bounded snapshots,
not redundant separate task/trace systems.

Under /api/v1: GET /evaluation/datasets; POST/GET /evaluation/runs;
GET /evaluation/runs/{id}; GET its /scenarios, /metrics, /report.json, /report.md;
POST /evaluation/compare; POST/GET /experiments; GET /experiments/{id};
POST /experiments/{id}/run. Mutations are idempotent. Owners are server-assigned;
clients cannot upload expected data or fault code. Python-only evaluator fault
callbacks are internal test hooks; no public fault endpoint exists.

/evals presents actual dataset/suite/configuration, persisted run progress,
metrics/methodology/denominators, failures, critical counts, gates, scenario
inspector and experiment assignments/comparisons. Command Center links to the
latest recorded evaluation. HTTP acknowledgment differs from database completion.
Only request intent is kept in localStorage. Selected-run identity and cancellation
prevent late reads/acknowledgments from replacing another selected run. A synchronous
posting guard blocks duplicate clicks. Offline/error/loading/empty states are explicit.

## Local commands and limits

```sh
docker compose up --build -d --wait
python3 scripts/acceptance_phase7.py
docker compose exec backend python -m app.evaluation.cli --suite REGRESSION
# Isolated test service can also run the same bounded CI gate:
docker compose --profile test run --rm backend-tests sh -c \
  'alembic upgrade head && python -m app.seed && python -m app.evaluation.cli --suite REGRESSION'
```

The CLI exits nonzero on failed gates. --configuration CAUTIOUS_THRESHOLD can
exercise an honest quality regression. --output writes JSON/Markdown to an
operator-chosen local directory; no API accepts filesystem paths. A compact
versioned baseline report is generated from an actual FULL run, not hand-scored.
No hosted CI/deployment service is required or configured.

Single-user, unauthenticated loopback demonstration. No production reliability,
formal safety/security verification, real-user usefulness, CV accuracy, semantic
quality or statistical significance is claimed. Real embedding, CLIP, DINOv2,
SAM and VLM inference remain unconfigured and unexercised. No paid service/model
is required. Runtime data/screenshot/cache files remain ignored. No Phase 8 work.
