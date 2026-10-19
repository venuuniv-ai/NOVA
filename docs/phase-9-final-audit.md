# NOVA Phase 9 final audit

**FINAL PHASE 9 STATUS — COMPLETE, October 19, 2026 (local qualification).**
Both authorized SELECTION_V1 application cases passed, followed by final backend
700/one explicit real-model skip, controller 13, Go race/vet, frontend lint/typecheck/
build, 56 browser cases across three profiles, baseline golden 104/104 FULL,
10/10 SMOKE and 25/25 REGRESSION, Kafka duplicate/forgery/HITL/outage recovery,
security/privacy and cleanup checks. No additional real inference occurred during
qualification. All task-owned services are stopped; real configurations remain
disabled. General model quality, real vision/judging, production deployment and
Phase 8 Kubernetes/NetworkPolicy limitations are not promoted by this completion.
Main remains at Phase 8 with an empty index; no commit/push. See the final section.

**Latest authorized SELECTION_V1 execution — October 19, 04:04–04:06:** positive
and conditional insufficiency cases both PASSED. The model answered Italian pasta
at index 0; the application verified and attached the original UUID/full quote.
The second response explicitly abstained with null answer/index and no citations.
Exactly two RAG requests/two BGE embeddings/two Qwen generations, zero retries.
Cleanup verified; scoped configuration disabled and attestation closed.
**REAL GROUNDED ACCEPTANCE PASSED. Phase 9 remains pending final cross-stack
qualification; it is not marked complete.** See the final execution section.

**Latest offline implementation — October 19, 03:35:** optional SELECTION_V1
separates model answer/selection from application-derived citations. **700 backend
passed / one real-model skip; 13 controller passed.** No model loaded or new real
acceptance executed. Legacy behavior stays default. Over-abstention cause remains
unproven; **PHASE 9 NOT COMPLETE**. See the final section and new approval proposal.

**Latest authorized grounded acceptance — October 19, 03:09:** Case 1 returned
VALID ABSTENTION / FAILED POSITIVE ACCEPTANCE (214 input / 11 output tokens).
Case 2 NOT EXECUTED; zero retries. Retrieval and final source/privacy validation
passed; no positive claim/citation was produced. Models and task-owned services
stopped, scoped configuration disabled, attestation closed. **REAL GROUNDED
ACCEPTANCE FAILED; PHASE 9 NOT COMPLETE.** See the final execution section.

**Latest offline grounding correction — October 19:** provider error masking,
source-content/visual revalidation and the acceptance transaction gap corrected;
bounded named-subject preference selection and an opt-in pinned context budget
added. Final backend **671 passed / one real-model skip**, controller **13 passed**.
No model activation or new real acceptance. Over-abstention remains unexplained;
**Phase 9 NOT COMPLETE**. See the final offline correction section and new proposal.

**Latest authorized 9I-F execution — October 19:** the single F-clarification
variant returned VALID ABSTENTION / FAILED POSITIVE DIAGNOSTIC. 236 input / 11
output tokens; no truncation or retry. No A/AF, BGE, RAG or database operation.
Qwen/controller stopped; scoped configuration disabled. Clarification result
INCONCLUSIVE; Phase 9 remains NOT COMPLETE. See the final execution section.

**Latest Phase 9H status — October 18:** all system-message differences classified;
three guarded diagnostic variants prepared offline. 623 backend tests and 13
controller tests passed. Initial Phase 9I proposal requests one 9I-F generation
only and awaits fresh approval. No models loaded or production changes made;
Phase 9 remains NOT COMPLETE. Later mission stages have not been started.

**Latest authorized Phase 9G isolation — October 17:** mechanical copy control A
PASSED; production-prompt case B returned VALID ABSTENTION / failed positive
diagnostic on identical synthetic data. Two Qwen generations, no BGE/RAG/retries.
Positive schema/copy capability is demonstrated; the specific abstention cause
remains unresolved. All processes stopped; Phase 9 remains NOT COMPLETE.

**Latest Phase 9G status:** offline contract isolation completed; no new production
defect or causal explanation was established. 613 backend tests and 13 controller
tests passed. A synthetic Qwen-only experiment is proposed but NOT APPROVED /
NOT EXECUTED. No model loaded; services stopped. Phase 9 remains NOT COMPLETE.

**Latest authorized Phase 9F diagnostic — October 17:** the single corrected-prompt
positive cycle returned a valid abstention: classification B, positive acceptance
FAIL. No retry or insufficiency cycle occurred. Models/services are stopped and
private configurations disabled. Phase 9 remains NOT COMPLETE; see the final section.

**Latest Phase 9F status:** offline investigation found and corrected a prompt-example
ordering mismatch with the pinned schema grammar. Its causal role remains unproven.
590 backend tests and 13 controller tests passed; no model loaded. Phase 9 remains
NOT COMPLETE. See the final Phase 9F section and its new, unapproved proposal.

Date: October 16, 2026 (America/New_York).

**Latest Phase 9E execution — October 17:** the approved entity-qualified positive
RAG returned a valid abstention and **FAILED positive acceptance**. The conditional
insufficiency cycle was not run. Models/services are stopped, real configurations
disabled, and Phase 9 remains **NOT COMPLETE**. See the final **PHASE 9E** section.

**Latest Phase 9D status — October 17:** offline prompt/request investigation and
regression passed. Positive instructions were clarified; Qwen's prior abstention
cause remains unproven. No model was loaded. A fresh proposal uses an explicit
source-entity question; real acceptance remains unapproved and Phase 9 NOT COMPLETE.
See the final **PHASE 9D — OFFLINE GROUNDED ANSWER RELIABILITY INVESTIGATION** section.

**Latest authorized acceptance — October 17:** the 96-token positive RAG cycle
returned a valid abstention and **FAILED positive acceptance**. The insufficiency
cycle was not attempted under the stop-on-failure instruction. All models/services
are stopped and real configurations disabled. Phase 9 remains **NOT COMPLETE**.
See the final **OCTOBER 17 — AUTHORIZED 96-TOKEN FINAL ACCEPTANCE EXECUTION** section.

**Latest Phase 9B status:** authenticated real BGE inference/reindex/retrieval
and Qwen structured generation executed successfully. The sequential RAG attempt
failed output validation and returned no answer. Regression passed; see the final
**PHASE 9B — RESUMED EXECUTION** section. Earlier blocked sections remain history.

**Standalone execution update:** the separately approved standalone BGE and Qwen CPU
probes passed on October 16. Both models were unloaded/stopped afterward. See
the final **APPROVED LOCAL MODEL ACTIVATION EXECUTION** section. The earlier
blocked dispositions and fixture measurements below remain historical evidence;
combined semantic RAG and real model quality acceptance remain unexecuted.

**Disposition: resource-safe implementation and deterministic regression verified;
real inference acceptance BLOCKED / NOT EXECUTED. No real model quality sign-off.**
A local Qwen artifact exists and was inspected read-only; it was not loaded.
No model weights were downloaded. No inference runtime or ML framework was installed.
Phase 10 was not started. Phase 8 Kubernetes rollout and NetworkPolicy enforcement
remain UNVERIFIED; their historical audit was not changed.

**REAL EMBEDDING MODEL NOT CONFIGURED.** Fixture hash embeddings are not a learned
semantic model. **REAL LLM JUDGE NOT CONFIGURED.** Real CLIP, DINOv2, SAM and VLM
inference remain unconfigured/unexercised. An adapter/MockTransport result is not
real inference. Installed, configured, executed, measured and evaluated are
separate states throughout this report.

## Baseline, resources and model inventory

Initial checkpoint: clean main at
`f4c430cbf42a1168c3e167780dc8ade8844d450f`. All eight checkpoint commits remain
unchanged. No commit/amend/push/remote configuration occurred. The approved scope
is captured in [implementation specification](phase-9-implementation-spec.md).
See [architecture](phase-9-architecture.md) and [preflight](phase-9-resource-preflight.md).

Read-only preflight: Apple M2 arm64, 8 GiB unified RAM, Metal 4 reported hardware
support (not an executed inference backend), 3.7 GiB free data-volume disk at 99%
capacity, 5149.56 MiB used swap of 6144 MiB. Docker memory 4106604544 bytes,
8 logical CPUs. macOS memory_pressure reported 55% under its accounting, about
62 MiB free pages and substantial compressed/active/inactive memory; that is not
4.4 GiB guaranteed allocatable model RAM. Inference resource gate requires >=5 GiB
host/local free disk, <2 GiB host swap, fresh private host attestation, <=2048 MiB
declared model memory and explicit operator resource approval. Current result:
**BLOCKED_BY_RESOURCES**. No Docker allocation/cache/volume cleanup was used.

Existing Ollama 0.35.1 client reported no running instance. No llama-server or
MLX-LM executable was found. Host pip inventory: mlx 0.32.3, pip 26.2.1, wheel
0.48.0; no torch/transformers/sentence-transformers installed on the host. Existing
backend dependencies suffice for HTTP adapters/tests; incremental dependency
installation was zero. Standard Hugging Face/LM Studio cache locations were absent;
this was a bounded inventory, not a scan of every private disk/directory.

Ollama cache contains qwen2.5:1.5b (~940 MiB). Its 986048512-byte model layer was
SHA-256 verified read-only:
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.
Cached metadata identifies Qwen2.5 1.5B Instruct, GGUF file_type 15 (quantization
interpretation not verified), declared context 32768, Apache-2.0; cached license
text was inspected. These facts do not attest runtime loading or generated output.
Estimated small-context runtime memory 1.5–3 GiB is a planning estimate, not a
measurement. No existing embedding or vision artifact was found in these caches.

The pinned future embedding proposal is
[download manifest](phase-9-model-download-proposal.json):
BAAI/bge-small-en-v1.5 revision
`5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, model.safetensors 133466304 bytes plus
listed config/tokenizer/README files; model SHA-256
`3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.
Only public repository metadata was read, not these model files. Declared MIT,
384 dimensions, ~0.3–1 GiB runtime estimate excluding a potential framework/runtime
installation. Approval and a new safe preflight are required before downloads or
installation. No embedding model/runtime installation is authorized by this report.
Sources: [BGE model repository](https://huggingface.co/BAAI/bge-small-en-v1.5),
[Qwen model repository](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct).

## Requested implementation and evidence boundaries

| # | Requested audit item | Implemented / executed boundary |
| --- | --- | --- |
| 1 | Initial Git checkpoint | Phase 8 hash above verified; clean start; no history rewrite |
| 2 | Host resource preflight | Actual RAM/disk/swap/Docker/architecture/GPU inventory above |
| 3 | Model inventory | Existing Qwen SHA verified; no embedding/vision weights found in standard caches |
| 4 | Runtime inventory | Ollama installed but stopped; no new runtime launched |
| 5 | Implementation changes | Explicit inference workspace/service, versioned reindexing, grounding, local transport, separate evaluation |
| 6 | Provider architecture | Reuses Phase 4 InferenceProvider and Phase 6 EmbeddingProvider; bounded OpenAI-compatible local surface |
| 7 | Model registry | Private operator JSON, bounded metadata, file digest, version/license/context/dimension/backend/memory declaration; safe durable catalog snapshot |
| 8 | Capability routing | Single selected provider, no strict-mode cloud/fixture fallback; existing privacy/circuit/ledger policy retained |
| 9 | Real embedding integration | Async batch transport plus versioned single-text adapter implemented; MockTransport tested; real execution NOT EXECUTED |
| 10 | Reindexing | Owned 10-record batches, cursor/vector atomic commit, failure rollback, explicit resume, immutable namespaces and retained old vectors |
| 11 | Hybrid retrieval | Existing RRF/structured/lexical retained; explicit lexical-only skips embeddings; selected namespace used for vector-only/hybrid |
| 12 | Memory privacy | Existing eligibility before retrieval and revalidation after generation; lifecycle/owner gates preserved |
| 13 | LLM integration | Existing local server protocol with JSON/schema, output/context bounds, tokens UNKNOWN unless reported; no actual LLM execution |
| 14 | Agent integration | Explicit strict-mode Kernel facade, existing agents/tools/Critic; fixture agents completed in acceptance |
| 15 | Structured validation | Existing Pydantic schemas, extra fields/tool calls rejected; no authority from model fields |
| 16 | Grounded RAG/citations | Owned evidence UUID/exact quote verification, conflict abstention and no raw answer persistence; not general entailment |
| 17 | Vision integration | Local inline-image transport uses owned verified media and existing PerceptionOrchestrator; HTTPX mock tested only |
| 18 | Multimodal fusion | Bounded authorized memory + persisted owned visual observations, IDs/provenance/time preserved |
| 19 | Injection tests | Extra approval/tool/owner fields and fabricated quotes/citations refused; original policy/injection regressions retained |
| 20 | Observability | Existing ModelCall accounting + owned run metadata, OTel duration/queue hooks, safe fixed instrumentation names; no real throughput/load/TTFT measured |
| 21 | Benchmark methodology | Explicit bounded HTTP samples, mode/hardware/OS/concurrency, unknown usage preserved; no implied cold-load or TTFT benchmark |
| 22 | Benchmark results | Three explicit fixture HTTP samples; real benchmark refused before invocation |
| 23 | Model evaluation | Separate labeled retrieval-v1 measurements below; real semantic/vision/LLM quality NOT EVALUATED |
| 24 | UI | /inference modes, server status/resources, approval-needed proposal, owned task controls, metadata and measured latency/tokens or UNKNOWN |
| 25 | API security | Existing Phase 8 auth/device/RBAC/ownership; task/run/job owner checks; operator-only isolated evaluation |
| 26 | Migration | 0011_inference_registry, four tables; isolated downgrade/upgrade/check passed; application forward-only |
| 27 | Restart persistence | Actual restart retained identical inference metadata, reindex progress and proposal/approval/execution evidence |
| 28 | Backend tests | 535 passed, 1 real-model opt-in case skipped; 495 prior retained + 40 new passing cases |
| 29 | Go tests | go test -race ./... and go vet ./... passed |
| 30 | Browser tests | 50 replay-profile passed (48 prior + 2 new), 3 strict local-auth passed, 2 real OIDC passed separately |
| 31 | Phase 7 golden | 104/104 FULL, SMOKE 10/10, REGRESSION 25/25; candidate 23/25 still FAIL |
| 32 | Phase 8 regression | Actual Kafka duplicate/forgery/HITL and broker outage recovery passed |
| 33 | Real model tests | Separately marked; no approved resource-safe configured runtime; skipped, not passed |
| 34 | Skipped/blocked | Actual text/embedding/vision inference, real semantic/model quality, cold model load/TTFT/real throughput blocked/unexecuted |
| 35 | Actual cost | Required external API/infrastructure spend $0; host compute/electricity unpriced |
| 36 | Resource constraints | Disk and swap gate failed; no models loaded to force a result |
| 37 | Security limits | Trusted local operator/runtime, narrow extractive checks, single process; no new penetration/security certification |
| 38 | Files changed | Exact manifest below; only source/config/test/docs, no runtime artifacts |
| 39 | Git status | main at Phase 8 checkpoint, index empty; Phase 9 unstaged/untracked |
| 40 | Blockers | Real inference/resource/download gates and unverified model quality remain open; Phase 8 deployment qualification unchanged |

## Architecture, authorization and persistence

The implementation extends existing routing/contracts/memory/perception instead
of duplicating task or agent systems. Existing default routes retain fixtures.
Explicit /inference requests choose FIXTURE, LOCAL_REAL or DISABLED. Missing real
model/capability/resource approval returns a recorded failure with null output.
An unvalidated result is cleared before response; original-key retry returns only
original metadata, never an invented new completion. Changed intent conflicts.

Private model files are read-only, bounded to 2 GiB and SHA-256 verified against
operator metadata. Paths, endpoint URLs and resource approval are never API inputs.
Private text/vision and embedding config files can be separate; no two models are
loaded by NOVA. Model capabilities/context/quantization are operator declarations,
not learned guarantees or a health-based production rating. Public catalog is
server-configured inventory, not an exhaustive inventory of developer-host weights.
A stopped Ollama artifact does not become a configured NOVA provider automatically.

HTTP transport uses existing local URL validation, no proxy/redirect, eight-second
async deadline, 64 KB response bound, bounded input/output and one active call with
zero pending queue. Busy requests fail RATE_LIMITED immediately. Cancellation closes
transport/relinquishes admission; errors normalize without retaining provider bodies.
Circuit state is process-local and shared for the bounded strict provider identities.
No cloud provider or paid traffic path is added. A trusted runtime could itself
relay upstream; this application cannot attest its internals.

Memory namespaces include model/version/dimension/artifact fingerprint. Original
vectors remain untouched. EmbeddingVersion maps namespaces and timestamps;
MemoryEmbedding.created_at timestamps each vector. ReindexJob owns task/user and a
fixed UUID scan upper bound. Steps lock owner/job, recheck active lifecycle/privacy/
time/task eligibility, process up to ten records and commit vector/cursor writes
atomically. A failed batch keeps its original cursor, stores a safe error and can
resume explicitly. New/corrected memories outside the captured scan need another
job. This is not a repeatable-read full-database snapshot or an automatic daemon.

Grounding bounds memory and visual context, treats it as data, validates cited
UUIDs and exact quotes, abstains on structured fact conflict, and rechecks memory
eligibility after generation. This prevents unsupported citation IDs and direct
quoted-content alteration; it **does not verify general factuality, relevance,
completeness or successful paraphrase understanding**. All source text remains
untrusted. Visual context cannot create permanent preference memories or expand
tool/action permissions. Existing Planner/Critic/application policy and canonical
payload-bound approval remain authoritative. Events/models cannot authorize an
execution; only the existing explicitly approved NOT SENT simulation is available.

Generation accounting reuses ModelCall; four new tables hold catalog snapshots,
owned request metadata, embedding namespaces and reindex progress. Prompts and
completions are not stored in new run rows; Phase 4's documented temporary exact
cache remains. Interrupted RUNNING runs fail APPLICATION_RESTARTED. READY jobs
resume from committed cursors; no distributed recovery claim. Real vision uses
Phase 5 owned media/normalization/persistence and distinct LOCAL_VLM provenance;
linked inference metadata carries configured fingerprint. No real vision output
was obtained or used as evidence in this phase.

## Actual validation and acceptance

Final full backend validation passed **535 cases, one explicit real-model skip,
in 90.98 seconds**.
The isolated migration round trip downgraded only test DB to 0010, upgraded to
0011 and checked drift. Application Alembic reports `0011_inference_registry
(head)`, no new operations. Original application data was never downgraded.
ruff check / format --check passed (117 Python files), pip check passed. Frontend
lint/typecheck/native production build passed; npm audit reported zero findings.
Go race tests/vet and Compose configuration validation passed. Scripts py_compile
passed. No hosted CI, Kubernetes, Terraform plan/apply or container image rebuild
was performed in Phase 9. Existing images plus read-only current source bind mounts
were used for resource-safe backend execution; frontend ran the native production
build. These are real API/PostgreSQL/Kafka services, not frontend-only state.

Entire browser replay profile: **50 passed**, five explicit authenticated/OIDC
cases skipped in that profile. Those ran separately: local-auth **3 passed**
(3.8 s), actual local Keycloak OIDC **2 passed** (2.9 s). Total coverage is 55 cases
across profiles, not one 55-pass suite. Retry count zero. No authentication trace
captured credentials; runtime fixture passwords/tokens remain ignored/private.
New mode/refusal/fixture, measured retrieval-comparison display and 390px
responsive checks passed. The final workspace build/tests were repeated after
adding the measured comparison table. Tests use the actual
backend, not fabricated task snapshots.

Authenticated Phase 9 acceptance task:
`49f58dfe-20a1-4623-be38-1f148cd43b48`.
Inference run `6018056d-1301-4185-bb72-bbc45842d8c4`, trace
`8d2a01a9-de19-405c-9937-165034363843`.
Reindex job `20b762b1-ada3-498c-b6ec-a5aca837273e`: DONE, eight eligible rows checked,
fixture namespace retained. Strict fixture agents finished DONE. Same task moved
Desktop → Wearable → Mobile. A subscribed draft proposal
`dcc0c2f5-6abb-44f3-9149-93e080705f2b` remained unapproved until explicit human
approval, then simulated execution returned external_message_sent=false. All
**13 outbox events** reached all three consumer groups. LOCAL_REAL and DISABLED
requests failed honestly. No real model run occurred.

SQL also confirmed zero DONE LOCAL_REAL runs and zero leftover evaluation schemas
before shutdown. Actual PostgreSQL/backend/gateway/worker restart retained identical run metadata,
reindex job list/progress, proposal/approval/execution and task UUID. The standalone
acceptance --verify-run passed. The additional reindex regression commits a
10-of-14 partial batch, invokes recovery, resumes to 14/DONE without losing the
cursor. Failed-batch rollback and owner isolation are separately tested.

Independent retained Phase 8 acceptance task
`352f8981-2c6d-4775-9a69-0616234cf938`: same UUID Mobile, nine outbox events,
three groups, one job, payload-bound approval and NOT SENT execution. Three
injected duplicates and a forged approval-like envelope were handled with no
duplicate effects and three dead letters. Ten-task continuity probe measured
31 HTTP samples, P50 **14.008 ms**, P95 **28.836 ms**, consumer catch-up **1.371 s**.
Actual broker outage task `4e43668b-d539-433a-bb20-adceae36b6d9` committed with
pending events and recovered in **34.058 s** from restart command. These are local
fixture probes, not model speed, production capacity, HA or disk-loss recovery.

Phase 7 FULL run `4cc87f62-72e3-464e-bcb3-bc3f5616ef5f`: **104/104**, critical=0,
gate PASS. SMOKE 10/10 and REGRESSION 25/25 CLI exited successfully. AB
`c5142238-a6a7-49af-867a-fca2b6ee3912`, SHADOW
`392a7e93-bfb2-4b65-9349-09630cdabeb5`, CANARY
`6ef060c7-f4ac-4075-a2c0-ac69f783189c` retain baseline 25/25 versus cautious 23/25;
candidate gates FAIL. Original dataset, baseline JSON and Phase 1–8 audit files are
unchanged. No fixture result was relabeled as real model quality.

## Separate retrieval evaluation and benchmark

Dataset nova-inference-retrieval-1.0.0 is separate from the 104 golden scenarios.
It contains three controlled added facts/preferences plus seeded fixtures, five
positive questions and one no-answer query. Actual PostgreSQL ranking measured:

| Strategy | Embeddings used | Positive denominator | Recall@5 | MRR | nDCG@5 | Items for no-answer query |
| --- | --- | --- | --- | --- | --- | --- |
| LEXICAL | None | 5 | 0.4 | 0.4 | 0.4 | 0 |
| SEMANTIC namespace ranking | Fixture token hashes only | 5 | 1.0 | 0.69 | 0.7475 | 5 |
| HYBRID | Fixture token hashes only | 5 | 1.0 | 0.69 | 0.7475 | 5 |

The name SEMANTIC selects pgvector infrastructure; it does not make fixture token
hashes a learned semantic model. The tiny candidate set and K=5 inflate recall.
Lexical misses paraphrases, and hash/hybrid retrieves irrelevant no-answer items.
This is an observed relevance limitation. No real embedding comparison or semantic
superiority is claimed. The predeclared future positive Recall@5 threshold 0.8
was not lowered: lexical 0.4 falls below it. No real model candidate was evaluated
or passed. Lifecycle/privacy/owner/approval are independent hard pytest assertions,
not hidden by the relevance average. No-answer recall/MRR/nDCG denominators are
null rather than invented positives. The versioned JSON also identifies safety
case categories; those are exercised by lifecycle/security tests, not counted as
extra measured relevance queries. A human review worksheet is provided and is
**NOT PERFORMED**; neither heuristics nor fixture judging are called human truth.

Three explicitly selected FIXTURE HTTP benchmark samples on arm64/macOS 26.6.2:
**89.045, 25.636, 17.688 ms**, concurrency 1, warmup 0. Tokens UNKNOWN/null.
These are HTTP fixture-pipeline wall times, not LLM latency or cold/warm load
measurements. Default real benchmark returned BLOCKED without making a request.
No actual load time, TTFT, tokens/s, real model requests/s, GPU memory, sustained
load, long-context/concurrent real benchmark or real quality score was measured.
Those measurements remain blocked pending resources/configuration. The script's
current nonstreaming HTTP sample support is narrower than a full runtime-specific
cold-load/streaming benchmark harness; no such capability is claimed complete.

## Findings, corrections and remaining blockers

- Initial lint/format/import issues were corrected before passing checks.
- A fixture/local vision extension initially assumed FIXTURE routing tier; fixture
  VLMs use VISION tier. Corrected provenance based on the actual provider identity;
  focused perception regressions passed, then the full suite passed.
- A new vision transport test first tried ingesting a wearable fixture on Desktop;
  the backend correctly refused. The test now makes the real valid handoff first.
- Source review found an invalid generated result could remain in a FAILED response.
  Clear output on every failure; the explicit regression passes.
- Lexical-only initially performed unnecessary embedding work. It now skips it;
  a test fails if any embed call occurs during lexical retrieval.
- Two isolated backend test invocations were accidentally overlapped, producing
  cleanup interference. Both were cancelled; no application data was involved.
  Final suites ran sequentially and passed without retries. Overlapping failures
  are not counted as passing checks.
- Admission was tightened to immediate busy refusal with zero pending queue; the
  final full suite was rerun. No arbitrary model waits or swap-forcing loop exists.

Open blockers: host disk/swap gate; no configured/approved embedding or vision
model; stopped/unconfigured text runtime for NOVA; no real inference/semantic/
vision quality evaluation. Real model/judge acceptance is NOT EXECUTED. Model
download/runtime installation requires explicit approval; a resource increase or
new model alone would not prove quality. No paid transport, cloud provisioning or
external message was used. Required external spend **$0**; host energy unpriced.

Known limits: single process/local unauthenticated replay profile plus separate
strict authenticated profile, trusted operator/runtime/config/host attestation,
conservative byte exposure rather than a tokenizer, exact bounded vector search,
soft-delete historical retention, finite fixture evaluation and narrow structured
conflict detection. Host inventory is bounded. No real model idle unload/streaming
or comprehensive automated benchmark matrix, production readiness, penetration
test, advisory/container scan or security certification is claimed. The previous
Kubernetes/NetworkPolicy limitations remain exactly as audited.

## Files, Git and local operation

39 changed/new text files: 18 modified and 21 additions.

```text
.github/workflows/local-regression.yml
README.md
backend/app/inference/__init__.py
backend/app/inference/api.py
backend/app/inference/contracts.py
backend/app/inference/evaluation.py
backend/app/inference/models.py
backend/app/inference/providers.py
backend/app/inference/registry.py
backend/app/inference/retrieval-v1.json
backend/app/inference/service.py
backend/app/main.py
backend/app/memory/contracts.py
backend/app/memory/service.py
backend/app/model_registry.py
backend/app/model_routing/api.py
backend/app/model_routing/contracts.py
backend/app/model_routing/kernel_provider.py
backend/app/model_routing/providers.py
backend/app/perception/contracts.py
backend/app/perception/service.py
backend/migrations/env.py
backend/migrations/versions/0011_inference_registry.py
backend/pyproject.toml
backend/tests/conftest.py
backend/tests/test_inference.py
compose.yaml
docs/architecture.md
docs/phase-9-architecture.md
docs/phase-9-final-audit.md
docs/phase-9-human-review.md
docs/phase-9-implementation-spec.md
docs/phase-9-model-download-proposal.json
docs/phase-9-resource-preflight.md
frontend/app/inference/page.tsx
frontend/components/nova-workspace.tsx
frontend/tests/inference.spec.ts
scripts/acceptance_phase9.py
scripts/benchmark_phase9.py
```

All changes are unstaged/untracked on main; HEAD remains
`f4c430cbf42a1168c3e167780dc8ade8844d450f`. Index empty, no remote configured,
no commit/amend/push. No Phase 10. No actual .env, token/key, model weight, private
media, runtime database/cache, screenshots/traces, dependencies, Terraform state
or build output is included. Generated validation outputs remain ignored or /tmp.
Historical checkpoints and measured reports were not modified.

Local operation after review:

```sh
docker compose -f compose.yaml -f compose.phase8.yaml up --build -d --wait
# Provision a private short-lived local operator token as described in Phase 8.
# Open http://localhost:3000/inference . FIXTURE remains the default.
# Real runtime config must stay private; no model downloader exists.
# Tests use the dedicated _test PostgreSQL database and offline flags.
docker compose --profile test run --rm backend-tests
```

Phase 9 validation used existing images with read-only app/migration bind mounts
instead of new image builds; native frontend production output was rebuilt.
Final validation containers/server are stopped with application PostgreSQL/media/
Redis/Kafka/auth/identity volumes preserved. No application volume was deleted.

**Final result: implemented and tested resource-safe integration; real inference
and real quality acceptance remain BLOCKED / NOT EXECUTED. Not a real AI quality
or production deployment sign-off. No commit, push, paid inference or Phase 10.**


## REAL INFERENCE ACTIVATION

Continuation preflight: October 16, 2026 (America/New_York).

**Result: BLOCKED AT RESOURCE GATE. No download, installation, runtime startup,
model loading or real inference occurred in this continuation.** Earlier fixture
metrics and test results above are historical and remain unchanged. They were
not rerun or relabeled as real inference.

### Fresh repository and resource verification

Branch main and HEAD `f4c430cbf42a1168c3e167780dc8ade8844d450f` match the expected
Phase 8 checkpoint. The exact existing 39-file Phase 9 manifest still matches:
18 modified / 21 added. No unexpected path was found. Index remains empty;
whitespace checks pass. Phase 1–8 checkpoints, previous audits and golden dataset
remain unchanged. Existing Phase 9 work was preserved, not reset or reimplemented.
The existing implementation/reference/preflight/proposal and actual registry,
resource-gate and provider code were reviewed.

| Fresh observation | Result / boundary |
| --- | --- |
| Host physical RAM | 8 GiB |
| Architecture / GPU hardware | arm64, Apple M2, 8 GPU cores, Metal 4 reported; inference backend not exercised |
| Host free disk | Approximately 15 GiB; passes >=5 GiB minimum |
| Swap usage | **3905.38 MiB used** of 5120 MiB; fails the strict <2048 MiB gate |
| macOS memory_pressure | 43% reported system-wide free percentage; not guaranteed allocatable model RAM |
| Free physical pages | About 59 MiB (3774 × 16 KiB); compressed pages about 2.74 GiB |
| Docker allocation | 4106604544 bytes (3.825 GiB), 8 logical CPUs; unchanged |
| Running Docker containers | None |
| Ollama runtime | Existing client 0.35.1; version probe reported no running instance |
| Other runtime executables | llama-server and mlx_lm.server not found on PATH |
| Standard additional model caches | Hugging Face hub and LM Studio cache directories absent |
| Declared <=2048 MiB model memory | Not established as a verified safe configuration; no new declaration/attestation issued |
| Fresh private host attestation | Not issued because swap gate failed |
| Model download / installation approval | Not granted by the continuation request |
| First real model-load approval | Not granted; no load attempted |

The earlier 3.7 GiB free disk and >5 GiB swap measurements are retained above as
history. They are not being reused as current values. Disk has improved; swap
still fails the existing gate. Gate thresholds were not weakened or overridden.

### Read-only model verification

The current Ollama manifest inventory contains qwen2.5:1.5b. Its existing
986048512-byte layer was hashed again read-only and matches both manifest and
expected SHA-256:
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.
Cached metadata still identifies Qwen2.5 1.5B Instruct, Apache-2.0, file_type 15
and declared context 32768. No inference or quantization behavior was measured.
No existing valid artifact was redownloaded or modified.

The pinned BGE proposal remains unchanged and is not present in the inspected
standard caches. No substitute model was selected. Its weight size alone is
133466304 bytes; that is **not a complete runtime installation footprint**.
Dependency resolution/complete installation planning and an actionable approval
request are deferred until the resource preflight passes, as required by the
continuation's stop condition. No ML package installation or model-loader import
was used to discover capabilities.

### Activation and evaluation status

| Action / evidence | This continuation |
| --- | --- |
| Downloaded model artifacts | None |
| New artifact checksum | None; existing Qwen layer checksum reverified |
| Embedding runtime install/load | Not executed |
| Qwen runtime startup / first model load | Not executed |
| Actual generation or embedding calls | None |
| Real 384-dimensional vectors / reindex namespace | Not executed / not created |
| Real retrieval Recall@5, MRR, nDCG@5 or latency | Not measured |
| Real LLM token/latency/memory/throughput measurements | Not measured |
| Real grounded RAG / strict agent evaluation | Not executed |
| Real model benchmark or regression after activation | Not executed; no activation occurred |
| Vision activation | Not executed; separate approval remains required |
| Real LLM judge | NOT CONFIGURED |
| Resource consumption during inference | Not measured; no inference process started |
| Failures | Resource-preflight refusal; no model inference failure/result invented |

The prior five-positive-question fixture retrieval scores remain fixture-only
history and too small for general quality conclusions. No thresholds, baseline
scores, privacy rules, approval hashes or Kafka behavior were changed. No actual
external message was sent. Runtime/model configuration was not enabled and no
application volume, cache, artifact or Docker allocation was changed.

### Safe remediation and next approval boundary

Reduce host memory pressure by saving work and closing unused memory-heavy
applications/VMs, then allow macOS to reclaim memory and remeasure swap. A normal
user-controlled reboot after saving work is another option if swap remains high;
this agent did not restart the host or Docker. Do not delete swap files or prune
protected caches/volumes. The existing strict swap threshold must actually pass;
a free-memory percentage or extra disk alone is not a substitute.

Once all resource gates pass, prepare the complete pinned embedding runtime/file
footprint and a bounded Qwen activation plan before requesting separate explicit
download/install/load approvals. Proposed initial Qwen parameters must be reviewed
then; the earlier 1.5–3 GiB planning estimate is not proof that it fits <=2048 MiB.
Do not start either model merely because its artifact exists, and never run both
models simultaneously on this host.

Only this audit was appended during the continuation. No code, tests, dataset or
previous audit was changed; no regression was rerun unnecessarily for a read-only
preflight. No commit, push, remote configuration, paid service or Phase 10 work.
**Real inference activation remains BLOCKED / NOT EXECUTED.**


## POST-RESTART RESOURCE VERIFICATION

Measured October 16, 2026 (America/New_York). This section follows the earlier
blocked preflights; it does not rewrite them or imply that a host restart was
performed or independently verified by this agent.

**Resource thresholds: PASS for the proposed bounded profiles. Actual model
activation: BLOCKED PENDING EXPLICIT APPROVAL. No model was loaded.** Application
model configuration remains inactive, with no operator resource approval enabled.

### Fresh measured state

| Check | Actual observation | Result |
| --- | --- | --- |
| Free disk | 21950496768 bytes, **20.443 GiB** | PASS, >=5 GiB |
| Physical RAM | 8589934592 bytes, **8 GiB** | Host capacity; not all available to a model |
| Swap | **1221.25 MiB used**, 2048 MiB total | PASS, strict <2048 MiB used |
| Memory pressure | macOS reports **65%** system-wide free percentage | Not a guarantee of allocatable model memory |
| Free pages / inactive / compressed | About 115 MiB free pages, 2.16 GiB inactive, 1.15 GiB compressed | Snapshot, not a model residency measurement |
| Docker allocation | **4106604544 bytes (3.825 GiB)**, 8 logical CPUs | Unchanged |
| BGE CPU proposed declaration | **1024 MiB** | Within <=2048 MiB declaration ceiling; estimate, not measured fit |
| Qwen initial CPU proposed declaration | **2048 MiB** | At ceiling; first load must stop if exceeded |
| Fresh host attestation | Private snapshot created; one-hour validity | Measurement attested, not load authorization |

The private `.secrets/phase9-post-restart-attestation.json` has mode 0600 and is
ignored by Git. It captures timestamp/free disk/swap and proposed declarations;
operator_resource_approved, model_load_approved and download_install_approved are
all **false**. It was not exported to an application/runtime environment. No
`resource_approved=true` model configuration was created. Its freshness must be
rechecked and observations repeated immediately before any later approved action.
The stopped application's default environment therefore still fails closed.

Existing Qwen's 986048512-byte layer was rehashed read-only and still matches
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.
Ollama 0.35.1 version probe reports no running instance. No Qwen download, alias
creation, model load, generation or unload was executed. Metal hardware reported
previously is not a measured/activated inference backend.

### Exact proposed installation and activation scope

The new [activation plan](phase-9-activation-plan.md) records all pinned package
versions, compatible wheel names/sizes and SHA-256 hashes, proposed commands,
resource/watchdog limits, integrity checks, stop procedures and separate approvals.
Only public PyPI metadata was fetched to resolve dependencies: **no wheel, source
archive or model file was downloaded**. The metadata helper initially encountered
a non-PEP-440 historical release label, skipped invalid release labels, then
completed resolution. No installation or runtime validation is implied.

The plan uses the existing Phase 9 provider interfaces and a necessary local CPU
embedding bridge, not another task/routing/memory system. The bridge is a future
implementation prerequisite after review, not a service claimed running today.
Host Python 3.14.8 arm64 is proposed in an isolated ignored `.local` venv. Existing
Anaconda Python 3.13.5 was inspected read-only; it has NumPy but lacks the required
embedding libraries, so no shared environment modification is proposed.

Known transfer footprint:

- BGE pinned model/config/tokenizer/card: **134505225 bytes**, including the
  133466304-byte safetensors weight from the unchanged authoritative proposal.
- All 34 pinned direct/transitive binary wheels: **166979696 bytes**.
- Combined known transfer bytes: **301484921 bytes** (~287.52 MiB).
- Expected installed environment/model footprint: **0.6–1.5 GiB planning estimate**,
  not measured. **3 GiB incremental disk reservation** includes environment,
  artifacts, temporary unpacking, venv tooling and small logs. No source builds,
  persistent wheel cache, automatic substitutions, model conversion or additional
  ML extras are approved. Installed size must be measured after any approved
  installation and the operation stopped if the budget is exceeded.

BGE: same pinned revision/license/hash as the earlier proposal, CPU float32,
384 dimensions, first batch one, input <=128 tokens, two CPU threads, one active
request/zero waiting queue, eight-second request deadline and one bounded
30-second initial-load watchdog. These are proposed limits, not measurements.
Verify finite nonzero normalized CLS vectors and artifact identity before any
owned namespace/reindex/evaluation work. Offline local-files-only loading is
mandatory; no Hub/model initialization downloads.

Qwen: reuse existing Ollama/artifact, one initial CPU-only test, context 512,
maximum output 32 tokens, two threads, concurrency one, temperature zero,
eight-second adapter deadline and 15-second operator hard-stop watchdog. The
plan proposes a new small metadata alias (estimated <1 MiB), not editing existing
weights/manifests, to bind context/CPU settings. Runtime option acceptance must be
verified after server-start approval; do not assume support or expand bounds if
validation fails. RSS estimate 1.2–2 GiB is unmeasured; stop at the 2048 MiB budget,
swap >=2048 MiB or disk <5 GiB. Unload with `ollama stop` and confirm no resident
model; terminate only the task-owned server if necessary. No model/cache deletion.

Important integration limit identified during plan review: a request semaphore
cannot prevent separate servers from retaining two models. BGE and Qwen must be
activated **sequentially**, with verified unload/process termination and resource
recovery between them. Combined real-semantic RAG must wait for an explicit tested
sequential handoff; do not enable both model servers permanently or present the
existing request semaphore as a model-residency guarantee.

### Remaining approval requirements and unexecuted work

1. **BGE download/install approval:** exact existing model manifest plus the
   34 hash-locked wheel distributions, isolated environment/bridge preparation,
   within the 3 GiB disk reservation. This does not authorize model loading.
2. **First BGE load approval:** one bounded CPU vector test after installation,
   hash verification and another fresh passing resource check.
3. **First Qwen activation/load approval:** start existing local Ollama, register
   only the proposed task alias, and perform one bounded generation with safe
   unload/stop in finally. No model download; no concurrent embedding load.

No approvals are assumed from the resource-verification request. Model execution,
real retrieval metrics, real RAG/agent quality, real model benchmarks and vision
remain **NOT EXECUTED**. No real LLM judge is configured. No regression suite was
rerun for this documentation-only/read-only verification; earlier 535 backend,
55 cross-profile browser and 104 golden results retain their original scope.

Git: main at `f4c430cbf42a1168c3e167780dc8ade8844d450f`, index empty, eight
checkpoints preserved, no remote or push. The original 39-file Phase 9 manifest
remains preserved as historical implementation scope; this continuation adds
`docs/phase-9-activation-plan.md`, so the current candidate is **40 text files:
18 modified / 22 added**. Only the final audit and the new plan were written in
this verification; private attestation is ignored. No existing application code,
test, dataset, previous audit, model artifact, cache, volume or Docker allocation
was modified. No commit, paid service or Phase 10 work.

## APPROVED LOCAL MODEL ACTIVATION EXECUTION

Executed October 16, 2026, approximately 12:44–12:50 America/New_York. The
operator explicitly approved the exact installation, first BGE load and one Qwen
generation in the preceding activation plan. **Result: installation PASS;
standalone learned embedding probe PASS; standalone local text probe PASS.**
This supersedes earlier activation-blocked status only for these bounded probes.
It does not change any historical fixture result or establish real model quality,
semantic retrieval/RAG acceptance, agent quality or production readiness.

### Fresh resource checks and enforcement

The branch remained main at `f4c430cbf42a1168c3e167780dc8ade8844d450f`.
Existing Phase 9 changes, all eight checkpoint commits and historical reports
were preserved. Actual host measurements were taken before installation, before
each model process and after termination; stale prior measurements were not used
to authorize runtime execution.

| Measurement | Before installation | Before BGE | Before Qwen | After both probes |
| --- | --- | --- | --- | --- |
| Free disk bytes | 20,696,412,160 | 19,594,715,136 | 19,587,837,952 | approximately 19.58 billion / 18.23 GiB |
| Used swap MiB | 981.19 | 917.19 | 917.19 | 917.19 |
| Physical RAM | 8 GiB | unchanged | unchanged | unchanged |
| Docker memory allocation | 4,106,604,544 bytes | unchanged | unchanged | unchanged |
| macOS reported free percentage | 60% | not separately sampled | not separately sampled | 52% |

macOS's percentage is not guaranteed allocatable model RAM. Disk stayed >=5 GiB
and swap stayed <2048 MiB. The BGE declaration was 1024 MiB and Qwen 2048 MiB.
The installation stayed within the 3 GiB disk reservation. Final `.local/phase9`
logical size was 1,033,942,544 bytes; allocated size was approximately
1,106,227,200 bytes, including the environment, model, metadata and safe local
evidence. No Docker allocation, host service or application volume was changed.

Task-owned watchdogs sampled host resources and runtime RSS approximately every
0.1 seconds during the probes, stopping on the configured thresholds. The BGE
startup watchdog was 30 seconds; request deadline eight seconds. Qwen used an
eight-second HTTP timeout and 15-second generation watchdog. No model request
was retried. RSS is sampled resident process memory, conservatively aggregated
across each runtime's processes, not a hardware-enforced memory quota or an
unsampled instantaneous peak/complete system memory measurement.

Both runtime processes inherited a macOS `sandbox-exec` profile denying external
network access and permitting loopback only. An actual external TCP connection
was refused with PermissionError under that profile; loopback HTTP worked for
the probes. Offline Hugging Face environment flags and local-files-only loading
were mandatory. This is not a comprehensive packet-capture/security certification.
No external message adapter, paid API or cloud resource was invoked.

### Approved installation and artifact validation

Created only the isolated `.local/phase9/embedding-venv` with existing Python
3.14.8 arm64. The exact 34-distribution hash lock from the approved plan was
installed using binary wheels only, `--require-hashes`, `--no-cache-dir`,
`--isolated` and the explicit public PyPI index. No pip upgrade, dependency
substitution, source build, extra ML framework or optional extras were installed.
All 34 installed versions match the lock; only normal venv bootstrap pip 26.2.1
is additional. `pip check` passed. A separate post-install RECORD integrity
check verified **20,490 hashed installed files** across the 34 distributions.
Installation took 28.388 seconds, excluding venv creation/validation. This is
package integrity/compatibility evidence, not a vulnerability scan.

The selected 34 wheel archive sizes matched public metadata (166,979,696 bytes),
and pip enforced their approved SHA-256 hashes. Every pinned BGE file was
downloaded from revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`;
the seven final file sizes total **134,505,225 bytes**. The six ordinary files
were verified against the pinned repository Git blob hashes, and the tensor
against its approved SHA-256. Computed final SHA-256 values:

| File | Bytes | SHA-256 |
| --- | --- | --- |
| README.md | 94783 | ddb964361a55c6e5dfca6361615854b260c9c960205d04c7520151aaa1d75837 |
| config.json | 743 | 094f8e891b932f2000c92cfc663bac4c62069f5d8af5b5278c4306aef3084750 |
| model.safetensors | 133466304 | 3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad |
| special_tokens_map.json | 125 | b6d346be366a7d1d48332dbc9fdf3bf8960b5d879522b7799ddba59e76237ee3 |
| tokenizer.json | 711396 | d241a60d5e8f04cc1b2b3e9ef7a4921b27bf526d9f6050ab90f9267a1f9e5c66 |
| tokenizer_config.json | 366 | 9261e7d79b44c8195c1cada2b453e55b00aeb81e907a6664974b4d7776172ab3 |
| vocab.txt | 231508 | 07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3 |

Intermediate failure retained: the first tensor transfer hit an operator-added
120-second transfer watchdog at 111,673,344 bytes. Expensive repeated directory
size enumeration contributed local monitoring overhead; this was not a proven
model or host-memory failure. The incomplete file was never loaded. One HTTP
206 Range continuation fetched only its remaining pinned bytes, with a 60-second
bound; final tensor size/hash then passed. No different artifact or model was
substituted. There was no inference retry or failed checksum treated as a pass.

### BGE first load and learned vector

Implemented/reviewed [minimal bridge](../scripts/phase9_embedding_bridge.py).
It binds only 127.0.0.1:11435, exposes `/v1/models` and `/v1/embeddings`, uses
the existing OpenAI-compatible embedding wire contract, rejects additional
authority fields, caps bodies/responses, and admits one embedding at a time
without an inference waiting queue. It does not start from application imports
or download anything. Valid/invalid request contract checks and syntax checks
passed without importing an ML framework; the real probe then exercised HTTP.

Runtime: PyTorch **2.14.1**, Transformers **5.20.0**, CPU float32, two compute
threads and one interop thread, batch one. AutoTokenizer/AutoModel used only
the verified local directory, `trust_remote_code=False`, safetensors,
`model.eval()` and `torch.inference_mode()`. Over-128-token input is rejected
rather than silently truncated. CLS output is L2-normalized.

| Actual result | Measurement |
| --- | --- |
| Load/import readiness | **11.855 seconds**, within 30 seconds |
| Controlled text | A controlled coffee cup rests on the desk. |
| One actual embedding request | **196.894 ms** |
| Learned vector dimensions | **384**, simulation=false |
| Vector validity | all finite, nonzero; L2 norm **1.0000000055492742** |
| Peak sampled process-group RSS | **466,567,168 bytes / 444.95 MiB**, below 1024 MiB |
| Invalid two-item batch | HTTP **422**, no second inference |
| Unload | task-owned process terminated; process RSS zero and embedding listener absent before Qwen |

The full vector was not placed in Git. Its controlled-response fingerprint is
`8fdddd7612743630bb939afe0fda291a1e6829a0521097123258801ab9489588`.
Termination emitted a Python resource-tracker semaphore cleanup warning; no
model process/listener remained. This warning is retained, not hidden as a clean
shutdown log. No repeated-vector reproducibility or semantic retrieval quality
claim follows from this one vector. No reindex or real retrieval evaluation ran.

### Qwen first load and generation

Only after BGE termination and another passing resource check, started the
existing **Ollama 0.35.1** inside the loopback-only sandbox. Reverified the existing
986,048,512-byte tensor SHA-256 before and after:
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.
Created only the proposed `nova-qwen-phase9` alias from existing qwen2.5:1.5b;
no new text weights/runtime were downloaded. Ollama refreshed modification
timestamps on reused blobs; their contents/sizes/hashes remain verified. The
original model manifest retains the same tensor. The alias's referenced blob
sizes and digests were all checked after execution; no cache cleanup occurred.

`/api/show` verified num_ctx=512, num_predict=32, num_thread=2, num_gpu=0,
temperature=0 before the generation. The runtime log independently confirms
`-c 512 -np 1 -ngl 0 -t 2`, CPU buffers, one slot and zero VRAM. There were no
other loaded models before the request. Runtime reports Q4_K_M quantization;
this is now executed-runtime metadata, rather than interpreting the prior GGUF
file_type alone.

One controlled OpenAI-compatible `/v1/chat/completions` request returned:

```json
{"summary":"A blue cup is placed on a desk."}
```

The response had exactly the existing SUMMARY contract's `summary` string field,
no tool calls, valid JSON, correct model identity and finish_reason=stop. Usage
reported **40 prompt tokens + 17 completion tokens = 57 total**, below the
32-token output ceiling. This was a direct local transport/schema probe, not an
authenticated NOVA API/service integration or full agent acceptance run.

| Actual result | Measurement |
| --- | --- |
| Cold-load-inclusive request wall time | **3411.508 ms**, within eight seconds |
| Peak sampled runtime-tree RSS | **1,253,228,544 bytes / 1195.17 MiB**, below 2048 MiB |
| Separate TTFT / model-only load latency / throughput | not measured |
| Native unload response | done_reason=unload |
| `/api/ps` after unload | empty models array |
| Final task-owned server | terminated; both model ports have no listener |

The cleanup call was an empty unload command, not a second generation. BGE and
Qwen were never resident concurrently. The small alias metadata remains for
review; no `ollama rm`, pull, pruning or application-volume deletion occurred.

### Evidence, remaining scope and Git

Safe local evidence remains ignored under `.local/phase9`: installation log and
command results, installed integrity record, model transfer/integrity records,
BGE/Qwen runtime logs, sampled resources and probe summaries. The final private
host attestation is `.secrets/phase9-approved-execution-attestation.json`, mode
0600. It describes completed scoped approvals, no active models and no enabled
application registry; it is not future activation authority. No private config
was exported into a running NOVA service.

No production/quality sign-off: real-semantic RAG remains disabled pending an
explicit tested sequential residency handoff. Application provider/registry
integration, real reindexing, retrieval Recall/MRR/nDCG, grounded RAG, agent
quality, longer benchmarks, concurrency, vision and real LLM judging were **not
executed** in this task. **REAL LLM JUDGE NOT CONFIGURED.** No fixture metric was
relabeled as real inference. Historical 535 backend, browser and 104 golden
results were not rerun for these standalone probes. Phase 8 Kubernetes and
NetworkPolicy qualifications remain unchanged.

Current Phase 9 candidate: **41 text files, 18 modified / 23 added**, including
the prior additive activation plan and new bridge. This execution changed only
this audit and added the bridge in the source tree. Artifacts/environments/logs/
attestations remain ignored. `git diff --check` passed; index empty; main and
all Phase 1–8 checkpoint hashes unchanged. No commit, push or remote
configuration. Required external API/infrastructure spend **$0**; host compute
unpriced. No Phase 10. Both models and task-owned runtime servers are stopped.

## PHASE 9B — REAL APPLICATION INTEGRATION

October 16, 2026 (America/New_York). **Disposition: integration code and offline
failure/cancellation tests implemented; real application execution BLOCKED by a
fresh swap-gate refusal. No Phase 9B real reindex, retrieval comparison,
authenticated generation or grounded RAG success is claimed.** The earlier
standalone BGE/Qwen successes remain separate historical evidence.

### Baseline and resource refusal

Confirmed main at Phase 8 checkpoint
`f4c430cbf42a1168c3e167780dc8ade8844d450f`, empty index, with the existing 41
Phase 9 text candidates preserved. Read the supplied Phase 9B requirements,
activation plan, current providers/service/registry/reindex/evaluation/auth code
and earlier probe evidence. No previous checkpoint was changed or new phase
started.

The first read-only measurement had 893.19 MiB used swap, approximately 18.2 GiB
free disk, 8 GiB physical RAM and Docker allocation 4,106,604,544 bytes. A required
second measurement, before any application/model startup, found **2988.44 MiB
used swap**, above the unchanged strict <2048 MiB limit. Registry-file preparation
then refused to produce a passing environment attestation. The subsequent
Compose command failed because that environment file did not exist; it did not
start an application container. No coordinator or model runtime was started.

Later read-only measurements showed 5611.81 MiB swap used, 38% macOS reported
free percentage and approximately 12.56 GiB disk headroom. Final measurement at
14:18:48 reported **5547.81 MiB swap used**, **13,502,488,576 bytes free disk**.
Memory-pressure percentages are not guaranteed allocatable RAM. The cause of
host-wide memory growth was not established. No model memory consumption can be
attributed to this continuation because no model process ran.

The swap threshold was not increased, and no disk/cache/volume deletion, Docker
restart, host restart or Docker allocation change was used to force a pass.
Model activation stopped at the failed gate. Independently testable code checks
continued in bounded offline processes; further Docker checks were stopped as
host pressure increased. Full application/browser/golden/Kafka regression was
not started under that pressure.

### Implemented

- Added [local residency controller](../scripts/phase9_residency.py), explicitly
  operator-started on loopback port 11436. It accepts only the existing BGE and
  Qwen alias, verifies their approved tensor fingerprints, and verifies that the
  Qwen alias references the expected existing artifact and bounded runtime
  parameters. It refuses preexisting/unowned model listeners rather than taking
  over another process. No downloader or external inference fallback exists.
- Actual runtime acquisition/release is separate from request admission. A
  nonblocking acquisition guard admits one resident model; existing acquisition
  cannot be displaced by a second acquisition or invalid release. Startup is
  bounded to 30 seconds, inference to eight seconds, and abandoned leases to 60
  seconds. A watchdog checks host disk/swap and model-process RSS, with unchanged
  1024 MiB BGE / 2048 MiB Qwen ceilings. Shutdown uses task-owned process/descendant
  termination, bounded escalation and listener/process checks. Failed termination
  poisons the controller so later acquisition fails closed.
- The controller runs model processes under the earlier loopback-only OS sandbox;
  BGE remains local-files-only, CPU float32, two threads, batch one and at most
  128 input tokens. Qwen must retain context 512, output at most 32, two threads,
  one slot, CPU-only and temperature zero. These new coordinated paths have not
  yet executed real models; prior standalone execution does not validate them.
- Existing `LocalProvider` now supports an explicitly private
  `managed_residency=true` configuration. It acquires a host runtime before its
  eight-second inference deadline and releases it in `finally`, including failed
  inference and cancellation during acquisition. Control acquisition is bounded
  separately; an expiring host lease backs up cleanup after client loss. The
  application semaphore still controls requests, while this controller manages
  actual processes. Controller access requires a private bearer key; lease/key
  fields, paths and endpoints are not public model metadata.
- Registry inventory can expose distinct text and embedding model metadata while
  excluding private configuration. FIXTURE remains the default; LOCAL_REAL still
  requires explicit artifact configuration, resource approval and a fresh gate.
- Added explicit operator-only `POST /api/v1/inference/evaluation/real`. It reuses
  the existing isolated labeled retrieval-v1 evaluation and existing
  `MemoryService`/pgvector, adding real BGE SEMANTIC/HYBRID comparisons alongside
  lexical and fixture rankings. Real vectors are created only inside that
  disposable evaluation namespace. The existing default fixture endpoint and
  historical labels/thresholds remain unchanged. This new endpoint was not run.
- Existing owned reindex transactions, namespace fingerprinting, lifecycle/privacy
  filters, evidence collection, quote/UUID verification, post-generation privacy
  revalidation, schema validation and payload-bound approval remain authoritative.
  No event/model/controller endpoint grants action or approval authority.

These are implementation claims, not real-runtime integration sign-off. Failure
paths have offline coverage below; model residency, host-container connectivity
and the complete authenticated flow still need actual execution.

### Configured

Prepared ignored private BGE/Qwen registry JSON and a controller key under
`.secrets/phase9b`, plus a temporary Compose overlay with source/artifact read-only
mounts. BGE identity is the approved 384-dimensional tensor; Qwen identity is the
previously approved existing alias/artifact. No extra model/package download or
installation occurred. The failed preflight prevented activation. Both private
model JSON files were explicitly reset to `resource_approved=false` at closure;
no passing resource environment was created or exported to an application.
Private files have mode 0600. No bearer key or private model path was added to Git.

The controller and application are stopped. Model ports 11434/11435, controller
port 11436, and application/gateway ports 8000/8080 had no listener at the final
check. There is no active residency lease. A passing future host check must
precede any attempted enablement; existing configuration files alone are not
permission to bypass the gate.

### Executed and measured

| Actual check | Result / scope |
| --- | --- |
| Host-side offline coordinator tests | **11 passed**, final run 0.053 seconds |
| Backend managed-lease/authorization/inventory tests | **6 passed**, 41 deselected, 1.26 seconds |
| Toy subprocess termination | Actual non-model Python child terminated and verified by a host test |
| Resource-gate/startup failure | Offline refusal and cleanup tests passed; no model load |
| Cancellation during acquisition | Backend test verified acquire then release, with no inference |
| Invalid release / second acquisition | Tests show another active lease is not displaced |
| Expired-client lease / shutdown failure | Expiry cleanup and poisoned-controller refusal tests passed |
| Inference deadline guard | Host test refused an expired deadline |
| Backend/controller lint and format | Passed on the integration snapshot; final deadline-guard/test additions also syntax-checked |
| Final Python syntax / Git whitespace | Passed |
| Real BGE/Qwen load, RSS and unload through coordinator | **NOT EXECUTED** |
| Real embedding/generation/end-to-end RAG latency | **NOT MEASURED** |

Backend checks used the existing `nova-backend-tests:latest` image with current
source mounted read-only, `--network none --memory 384m --cpus 2`, without database
or model startup. Only selected independent tests ran outside the DB fixture
module. This is not the full PostgreSQL-backed suite. No real model integration
flag was enabled. The standalone controller tests use fake callbacks plus one
small non-model Python subprocess; they do not import torch or load weights.

Intermediate checks are retained: the first isolated pytest command lacked
PYTHONPATH and failed collection; correcting it produced four passing tests,
then the expanded six-test selection passed. Initial import-order/line-length
lint findings were corrected before the passing lint check. Those initial
failures are not counted as passes. No retry configuration or test weakening was
introduced. Final host tests include the subsequently added deadline refusal.

### Evaluated, blocked and unverified

No Phase 9B real relevance/model evaluation executed. Existing retrieval-v1 has
**five positive questions and one no-answer query**. Requested comparisons remain:

| Comparison | Recall@5 / MRR / nDCG@5 | No-answer / latency in Phase 9B |
| --- | --- | --- |
| LEXICAL | Not rerun; historical fixture report unchanged | Not rerun |
| FIXTURE SEMANTIC | Not rerun; historical fixture report unchanged | Not rerun |
| FIXTURE HYBRID | Not rerun; historical fixture report unchanged | Not rerun |
| REAL BGE SEMANTIC | **NOT EXECUTED** | **NOT MEASURED** |
| REAL BGE HYBRID | **NOT EXECUTED** | **NOT MEASURED** |

No threshold was lowered, no score was invented, and no five-question result is
presented as general superiority. No real owner-authorized reindex job, atomic
real-vector batch/resume, cross-owner/privacy/lifecycle retrieval test, authenticated
Qwen request, grounded answer/abstention, citation rejection or payload-bound
approval test ran against the Phase 9B application. Existing deterministic tests
and historical approval/Kafka results remain separate, unchanged evidence.

Unresolved blocker: **host swap exceeds 2048 MiB**. Full 535-backend baseline,
55 cross-profile browser cases, 104 golden scenarios and Phase 8 Kafka/HITL
regression were not rerun after these changes. Their historical passes are not
new passes. Real controller startup/shutdown/cancellation under actual model load,
Docker-to-host loopback reachability, authenticated registry/provider integration,
real reindex/evaluation, sequential grounded RAG and end-to-end latency all remain
**UNVERIFIED**. An actual future model contract failure must be recorded as
failure/abstention, not replaced with fixture output. No vision activation or real
LLM judging occurred. **REAL LLM JUDGE NOT CONFIGURED.** Phase 8 Kubernetes and
NetworkPolicy qualifications remain unchanged.

### Git and stop state

Current candidate: **43 text files, 18 modified / 25 added**. This continuation
updated the existing inference API/evaluation/provider/registry and test files,
added the controller and its host tests, and appended this audit. Existing
implementation was extended, not recreated. Models, venv, credentials, private
registries, probe evidence and temporary overlays remain ignored/outside Git.

Branch main; HEAD `f4c430cbf42a1168c3e167780dc8ade8844d450f`; index empty;
all Phase 1–8 checkpoints, historical golden dataset and baseline reports
unchanged. No commit, push, remote configuration, cloud/paid service, external
message, cache pruning, volume deletion or Phase 10. Required external spend $0.
**STOPPED with Phase 9B real application execution BLOCKED / NOT EXECUTED.**

## PHASE 9B — RESUMED EXECUTION

October 16, 2026, approximately 15:07–15:33 America/New_York. Resumed on the
operator's instruction after another fresh resource check. **Qualified result:
authenticated BGE application inference, owned real-vector reindexing, labeled
real retrieval comparison and Qwen structured text generation executed. The
sequential grounded RAG attempt FAILED output validation; no successful grounded
answer or model-quality sign-off is claimed.** All validation services are now
stopped. This section supplements the earlier blocked attempt and standalone
probes without replacing their measurements.

### Status boundaries

| State | Current evidence |
| --- | --- |
| Implemented | Existing managed-residency/provider paths exercised; added compact real-mode grounding context selection and two regression tests |
| Configured | Private, verified BGE/Qwen registry files were explicitly enabled for execution; disabled again afterward; FIXTURE remains the default |
| Executed | Authenticated application embedding, one owned reindex job, five-way retrieval comparison, Qwen summary, failed RAG, client-reset cleanup, regression and restart checks |
| Measured | Actual API/runner latency, sampled runtime RSS, learned vector dimensions, reported text tokens, retrieval metrics, resource snapshots and process termination |
| Evaluated | Five positive retrieval questions and one no-answer question; finite fixture regressions; no general AI quality evaluation |
| Failed / open | Qwen grounded response failed validation with the unchanged 32-token ceiling; no answer was exposed |
| Unverified | Successful real grounded citations/abstention, actual interrupted real-vector partial-batch recovery, general quality, sustained load, full streaming/TTFT and production deployment |

### Resources, configuration and authenticated architecture

Fresh first preflight: **1618.25 MiB swap used**, approximately **16.1 GiB free
disk**, 8 GiB RAM, 68% macOS reported free percentage. A second passing measurement
was recorded in the private startup environment before application startup.
Docker allocation remained **4,106,604,544 bytes / 8 logical CPUs**. No disk,
swap, model-memory or timeout threshold was weakened. No additional package,
model weight or inference runtime was downloaded or installed.

Started only the necessary existing PostgreSQL, Redis, FastAPI and Go gateway
images initially, with current backend source mounted read-only. Application
PostgreSQL/media/auth volumes were reused and preserved. Private model artifact
mounts were read-only. The first startup refused a temporary cache TTL of zero;
the overlay was corrected to the existing schema minimum of one second. This
startup error is not counted as a pass.

The backend container actually reached the loopback residency controller through
`host.docker.internal:11436`. Its private bearer authentication returned HTTP 200
for the authorized probe. The application's LOCAL_REAL requests then used the
existing `LocalProvider`/`VersionedEmbedding`, private artifact configurations and
controller acquire/infer/release sequence. FastAPI independently authenticated
local credentials; the Go gateway also accepted an authenticated identity read.
The measured real inference calls used direct authenticated FastAPI HTTP, rather
than claiming a browser or gateway inference benchmark.

Actual security checks: no bearer returned **401**; a different owned identity
received **404** for the task, memory, inference-run and reindex resources; forged
approval input returned **422**; a non-operator owner received **403** from the
real evaluation endpoint. Credentials remained in ignored private files/volumes,
not URLs, source or browser traces. These checks do not certify production
security or hardware device identity.

### Real semantic memory and persistence

Controlled application task: `70b45f12-b509-4443-a66f-81b86caf872c`.
Authenticated embedding run: `cd06bc13-921c-4563-a35c-5b2c399a0e79`, DONE,
LOCAL_REAL, simulation=false. Model BGE-small-en-v1.5, pinned revision
`5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, tensor SHA-256
`3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.

Owned reindex job: `82f96340-9abd-4e43-b826-26d42b4a7377`, DONE, three records,
namespace **bge-small-en-v1.5@bd60ce951a6ec4edab8518c1b3301686**. Its controlled
memories are cuisine `4d4b4842-c804-4e72-90c9-7162d6436c37`, deadline
`3b1d6f94-383e-4276-863c-432ca6c0dc1f` and beverage
`83850485-9c3c-43d5-ba5d-c71573b6e294`. Retrying the completed job returned
identical cursor/state/processed count; another owner could not step it.

Actual SQL verified **three 384-dimensional non-simulation vectors** alongside
all **three original 32-dimensional fixture vectors** for these memories. The
existing batch transaction committed vector/cursor writes together. The full
backend regression also passed atomic rollback, partial 10-of-14 resume, owned
scope/privacy/lifecycle and citation policy tests. Those fault/resume tests use
deterministic providers: this run did not crash a partial real-vector transaction
or claim that such a crash was exercised.

Backend restarts across validation profiles retained the same task, reindex job,
run IDs, model fingerprints and terminal states; owner reads passed and foreign
owner reads still returned 404 afterward. Application Alembic remains
`0011_inference_registry`. Final SQL found **zero leftover evaluation schemas**.
No application database downgrade, historical embedding replacement or parallel
memory/task system was introduced.

### Labeled retrieval comparison

The explicit authenticated operator POST to `/api/v1/inference/evaluation/real`
ran the unchanged retrieval-v1 dataset inside its disposable schema. There are
**five positive questions**, one with two relevant documents, and **one no-answer
question**. Each strategy has six timed searches; relevance averages use only
five positives. The same expected IDs and thresholds were used for every arm.
The entire evaluation took **39,307.00 ms**, including setup, real indexing,
rankings, model startup/shutdown and cleanup.

| Strategy | Embedding | Recall@5 | MRR | nDCG@5 | Mean search ms, six queries | No-answer returned |
| --- | --- | --- | --- | --- | --- | --- |
| LEXICAL | none | 0.4 | 0.4 | 0.4 | 3.612 | 0 |
| FIXTURE SEMANTIC | token hash, simulation | 1.0 | 0.69 | 0.7475 | 2.696 | 5 |
| FIXTURE HYBRID | token hash, simulation | 1.0 | 0.69 | 0.7475 | 2.524 | 5 |
| REAL BGE SEMANTIC | learned 384-D | 1.0 | 0.9 | 0.9101 | 2268.813 | 5 |
| REAL BGE HYBRID | learned 384-D | 1.0 | 0.9 | 0.9101 | 2257.780 | 5 |

The tiny K=5 candidate set inflates recall. Real BGE ranked these labels better
than token hashes in this run, but **still returned five irrelevant results for
the no-answer question**. No no-answer threshold was invented or tuned after the
run. The existing positive Recall@5 threshold 0.8 was unchanged. Passing that
small positive threshold does not establish general semantic superiority,
calibration, usefulness or grounded generation quality. Historical fixture
scores/baseline JSON remain unchanged. Real search durations include runtime
acquisition, model readiness and release per request, not just vector math.

### Authenticated Qwen and failed grounded RAG

Text run `0cffe2d8-ca88-4103-9a9f-0e30911b514a`: DONE, LOCAL_REAL,
simulation=false, no fallback. Correct existing alias **nova-qwen-phase9** and
artifact fingerprint
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.
The existing CPU-only configuration remained context 512, max output 32,
temperature zero, two threads, one slot. The response passed SUMMARY schema:

```json
{"summary":"A blue cup is placed on a desk."}
```

Provider-reported usage: **107 input / 17 output tokens**. Application model-call
latency **5060.71 ms**; authenticated HTTP wall time **6046.09 ms**. These include
startup/generation/cleanup at their respective scopes; no TTFT/throughput claim.

Before the real RAG attempt, compact context selection was added so the bounded
real model receives at most one retrieved evidence item with its ID/exact text,
not verbose provenance metadata. Conflict checks still cover the full retrieved
set before narrowing; conflicting evidence still forces abstention. Fixture
context behavior is unchanged. Both selection and full-conflict preservation
are covered in the passing full backend regression.

RAG run `545bae8f-6899-42e7-94e8-2dc7c5a8ac70`, retrieval snapshot
`ef89f2a2-ccce-4c18-a4aa-c5a745da0853`, attempted the complete actual handoff:
owned hybrid memory retrieval with BGE → BGE termination → Qwen acquisition →
controlled grounded generation → validation refusal → Qwen termination.
**Result FAILED, output=null**, HTTP wall time **10,876.00 ms**. The model-call
attempt ledger records **INVALID_RESPONSE**, 7166.642 ms; the router's final API
safe error is the coarser UNAVAILABLE after its sole configured provider fails.
The runtime completed within the unchanged deadline and logged 276 prompt tokens
and 32 generated tokens. Raw invalid completion was not retained, so no more
specific parse/contract explanation is asserted. No retry, larger token/context
limit, different model, fixture fallback or invented answer was used.

This is successful fail-closed handling of an unsuccessful grounded generation,
not successful RAG/citation acceptance. The post-generation citation/privacy
acceptance path was not reached for that invalid response. Independent retained
regressions reject fabricated UUIDs/quotes, cross-owner/deleted evidence,
extra tool/approval authority and conflicting claims. A real successful grounded
answer or explicit model abstention remains an open acceptance item.

### Residency, monitoring and failure cleanup

The controller recorded **23 BGE acquisitions and two Qwen acquisitions**, all
terminated, with ordered nonoverlapping start/stop records. This includes actual
indexing/evaluation requests and a separate bounded client-reset cleanup test;
it is not a request-throughput benchmark. In the reset test the client dropped
its acquire connection during actual BGE startup; four seconds later no model
listener remained. Offline cancellation/lease/poisoned-shutdown tests also passed.

| Actual runtime observation | BGE | Qwen |
| --- | --- | --- |
| Peak sampled aggregated RSS | 484,147,200 bytes / 461.72 MiB | 1,527,447,552 bytes / 1456.69 MiB |
| Unchanged memory ceiling | 1024 MiB | 2048 MiB |
| Maximum controller readiness time | 3.855 s, includes model readiness | 0.545 s, server readiness only |
| Maximum recorded shutdown time | 0.040 s | 0.036 s |
| Logged acquisition-boundary swap | 1554.25–1570.25 MiB | 1554.25 MiB |
| All recorded processes/listeners stopped | yes | yes |

Qwen loads weights lazily during generation; its controller readiness number is
not a weight-load measurement. Ollama separately logged runner startup in 2.28
seconds. RSS was sampled with process/descendant checks; aggregated RSS may count
shared pages more than once and does not prove an instantaneous hard RAM quota.
Disk stayed above 5 GiB and resource watchdogs remained active. Models never ran
concurrently. The sandbox/offline policy and artifact checks were reused; no
model or package download occurred in this continuation.

### Regression and intermediate failures

| Executed validation | Actual result |
| --- | --- |
| Full current-source PostgreSQL backend suite | **543 passed, 1 explicit real-model skip**, 60.11 s |
| Backend lint / format / pip compatibility | passed, 117 Python files formatted |
| Host controller/process tests | **11 passed**, final run 0.062 s |
| Full replay browser profile, retries=0 | **50 passed**, five explicit profile skips, 54.0 s |
| Separate strict local-auth browser profile | **3 passed**, 2.7 s |
| Separate actual Keycloak OIDC browser profile | **2 passed**, 2.7 s |
| Authenticated FULL golden run | **104/104**, zero critical violations, gate PASS |
| Authenticated cautious REGRESSION run | **23/25**, expected gate FAIL |
| Real Kafka duplicate/forgery/HITL acceptance | passed, details below |
| Restart-owned metadata / schema cleanup checks | passed |
| Final Git whitespace / artifact-path checks | passed |

Browser coverage is **55 cases across three separate profiles**, not a single
55-pass invocation. The existing native frontend production build was reused;
frontend source did not change in this continuation. Current backend source was
mounted read-only into existing images; no image/model/framework download or
new image build was used. Authentication profiles disabled browser tracing.

Golden run `7cf2a7d3-adc8-4019-bf43-6776165c6b19` passed 104/104.
Cautious run `8d28d82f-5f58-4e4c-950d-51b1a283424e` remained 23/25, not
relabeled as a win. Historical baseline/dataset files were not edited.

Intermediate validation failures remain disclosed. The first test command
incorrectly omitted test dependencies and was aborted at setup. The next full
run had **523 passed / one failed / 19 setup errors / one skip** because the
operator-chosen 192 MiB isolated test-DB cap caused an actual PostgreSQL OOM
(connection loss/recovery); Docker's OOM flag confirmed it. The ephemeral test DB
was then given 512 MiB and 32 MiB shared_buffers, and the unchanged full tests
passed. These are test-infrastructure limits, not raised model budgets or Docker
allocation. No application volume/database was reset or downgraded. No test
retry mechanism, weakened assertion or earlier failure was counted as passing.

Actual Kafka/HITL acceptance task `a82b1e63-68fa-4a97-b266-4f2c47e0c220`
kept its UUID through Mobile, nine outbox events, three consumer groups, one job
and proposal `c57b2ae6-0a92-45cc-8a39-f35fef763047`. Three duplicate deliveries
produced no extra effect; a forged approval-like envelope produced three dead
letters. The human approval hash remained bound to the proposal payload and
execution was SIMULATED / NOT SENT. No real external message was sent. This
reran duplicate/security acceptance, not another broker-outage or disk-loss test.

### Stop state, evidence and remaining limits

All task-started application, Kafka, worker, identity and frontend processes are
stopped; model/coordinator ports and application ports have no listener. Docker
reported no running containers. Existing application PostgreSQL/media/Redis/
Kafka/auth/identity volumes are preserved. Private model configurations again
have `resource_approved=false`; regression used empty real-registry environment
settings and fixture defaults. Credentials/configs/evidence remain ignored under
`.secrets/phase9b` and `.local/phase9/integration`. Reproducible control entrypoint
is `python3 scripts/phase9_residency.py --key-file <private-key-file>`; it must not
be enabled without a fresh passing resource check and private approved settings.

Final snapshot at 15:33:29: **17,794,453,504 bytes free disk**, **1612.06 MiB swap
used**, **8 GiB RAM**, unchanged Docker allocation, 31% macOS reported free
percentage. This is a snapshot, not future activation authority or guaranteed
available model RAM. No cache pruning, application-volume deletion, cloud
provisioning or paid service was used. Required external spend **$0**; local
compute/electricity unpriced. No vision inference or real LLM judge was enabled.
**REAL LLM JUDGE NOT CONFIGURED.** Phase 8 Kubernetes/NetworkPolicy verification
remains exactly as qualified in its historical audit.

Remaining limits: no valid real grounded answer/abstention; no actual interrupted
real partial-batch recovery; finite five-positive retrieval labels with poor
no-answer behavior; no general quality, sustained-load, streaming or production
sign-off. Go/hosted CI/Kubernetes/Terraform were not rerun in this continuation.

Git: **43 text candidates, 18 modified / 25 added**, empty index, main at
`f4c430cbf42a1168c3e167780dc8ade8844d450f`. No model, venv, private credential,
runtime trace/media/database, browser artifact or build output enters the source
candidate. All Phase 1–8 checkpoint commits and historical measured reports are
preserved. No commit, push, remote configuration or Phase 10. **Stopped after
qualified integration evidence and audit; grounded RAG acceptance remains open.**


## PHASE 9 — FINAL OFFLINE REVIEW AND ACCEPTANCE BOUNDARY

October 16, 2026; closing resource observation at 16:31 America/New_York.
**PHASE 9 STATUS: NOT COMPLETE. Offline corrections and post-change regression
passed. Further real-model acceptance is BLOCKED pending fresh explicit approval.**
The operator's attached final mission sections 1, 4 and 13 explicitly require fresh
execution scope and separate approval before changing the existing 32-token real
profile. This mission did not provide those approvals. No model was loaded,
no inference runtime/controller was started, and no new real generation, learned
embedding, real reindex or real retrieval evaluation ran in this review. Existing
real successes and the failed grounded RAG above retain their historical scope.

### Baseline, resources and approvals

Verified main at `f4c430cbf42a1168c3e167780dc8ade8844d450f`, empty index,
no remotes. All eight Phase 1–8 checkpoint commits remain intact. The initial
43-file Phase 9/9B candidate was preserved; existing work was extended, not reset.
Historical audits, golden dataset, thresholds and measured baseline reports were
not edited. The new section is additive.

| Resource | Initial read-only preflight | Final observation |
| --- | --- | --- |
| Free host disk | Approximately 15.73 GiB | 16,871,964,672 bytes / 15.713 GiB |
| Physical RAM | 8 GiB | 8,589,934,592 bytes / 8 GiB |
| Used host swap | 1643.06 MiB | 1579.06 MiB |
| macOS reported free percentage | 72% | 39% |
| Docker allocation | 4,106,604,544 bytes, 8 CPUs | unchanged |
| Logical host CPUs | 8 | 8 |
| BGE / Qwen declared ceiling | 1024 / 2048 MiB | unchanged; neither loaded |

Disk >=5 GiB and swap <2048 MiB passed the measured snapshots. The macOS percentage
is not guaranteed allocatable model RAM. A fresh ignored private attestation at
`.secrets/phase9-final-review-attestation.json`, mode 0600, records a one-hour
snapshot with operator_resource_approved=false, model_load_approved=false and
new_runtime_profile_approved=false. It is not future execution authority and was
not exported into a model-enabled application. No resource threshold or Docker
allocation was raised; no protected cache, model file or application volume was
deleted. The test-database memory incident below did not authorize model execution.

Read-only tensor verification passed again:

- BGE: 133,466,304 bytes, revision
  `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, SHA-256
  `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.
- Existing Qwen: 986,048,512 bytes, SHA-256
  `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.
  Existing `nova-qwen-phase9` profile remains output 32, context 512, CPU-only,
  two threads, one slot and temperature zero. No new alias was created.

Both private registry JSON files remain resource_approved=false. Regression
containers used empty real model/embedding configuration paths, offline flags
and fixture defaults. No weights, packages or inference framework were installed
or downloaded. Required external API/infrastructure spend remains $0; local
compute/electricity is unpriced.

### Root-cause investigation and corrections

The historical RAG run `545bae8f-6899-42e7-94e8-2dc7c5a8ac70` failed with
output=null after 276 prompt / 32 generated tokens. Its raw completion was not
retained. **The historical root cause cannot be established** as truncation,
missing field, wrong type, fabricated UUID/quote, formatting or refusal from that
record alone. Its recorded INVALID_RESPONSE remains failure; it is not relabeled.

Source review identified actionable reliability gaps: grounded transport requested
JSON-object mode without a constrained schema; parse/schema failures were collapsed
into INVALID_RESPONSE; the single strict local provider's final router response
then collapsed that into UNAVAILABLE. The application could not retain a safe,
specific diagnostic in its owned run record. These are identified code limitations,
not proof that any one caused the old completion to fail.

Corrections implemented and exercised with synthetic responses:

- Grounded requests now send the existing GroundedOutput JSON schema through
  response_format=json_schema with strict=true and a compact prompt treating
  evidence as untrusted data. It requires a supplied UUID/full exact quote and
  explicit abstention on insufficient/conflicting evidence. SUMMARY behavior
  retains JSON-object mode. The real runtime's schema compatibility is UNVERIFIED;
  an unsupported response must fail closed rather than fall back to free text.
- Parsing separates JSON syntax, structured schema, model identity, response shape,
  tool authority, refusal, usage/result metadata, output-limit, HTTP status and
  timeout diagnostic categories. Validation is strict; fenced/free text is refused.
  A valid JSON prefix with finish_reason=length is also refused. No citation repair,
  unvalidated output exposure, retry loop or fallback was added.
- Diagnostic records are bounded and revalidated before persistence. They retain
  only fixed categories/classes, whitelisted field paths/types, bounded reported
  counts, fixed finish reason/status and an EOF_AND_LENGTH indicator when both
  conditions occur. Unknown field names are replaced by a fixed placeholder;
  exception messages, inputs, context and raw provider bodies are excluded.
  Owned ModelCall/run metadata retains correlation and existing model identity.
  The strict single-local-provider router preserves its actual invoked safe error.
- Residency now has a nonblocking inference guard separate from acquisition.
  Reusing one private lease cannot queue another inference or replace a runtime
  while a released in-flight call unwinds. Lease validity is rechecked before
  returning its result. Existing resource checks, bearer authentication, sandbox,
  watchdogs, termination verification and poisoned-controller refusal remain.
- Explicit real evaluation can include per-rank semantic/fusion scores and controlled
  relevance labels without source text, UUIDs or vectors. Default fixture evaluation
  output, original labels, thresholds and historical scores remain unchanged.
  This new optional real diagnostic output was not executed against a real model.

The 32-token runtime ceiling was not changed. A quoted claim must fit JSON keys,
a UUID, exact quote and abstain flag; 60–90 output tokens is an unmeasured planning
allowance for a short single claim. The [separate acceptance proposal](phase-9-final-acceptance-plan.md)
requests a new task-owned 96-token alias plus two finite sequential cycles, one
positive and one insufficiency case. Context 512, CPU threads, model memory and
eight-second inference deadline remain unchanged in that proposal. Larger output
can increase compute time/memory; no safe fit or success is assumed. Nothing in
the proposal enables or implements a 96-token runtime profile today.

### Retrieval, citations, privacy and workflow review

Historical retrieval-v1 contains five positives and one no-answer question. Its
real BGE semantic/hybrid scores remain Recall@5=1, MRR=.9, nDCG@5=.9101, with five
irrelevant no-answer results. This is historical finite evidence, not a new run
or general quality result. No similarity cutoff was calibrated or introduced.
Top-k returns candidates without an answerability guarantee; RRF fuses ranks,
not semantic truth. Future threshold work needs independently reviewed calibration
examples and an untouched holdout with precision/recall/abstention reporting.
No new human judgments or extra evaluation labels were invented.

The verified local BGE model card permits v1.5 embeddings without a query prefix
and recommends one for some query/passage tasks. Current query/document processing
consistently omits a prefix; bridge CLS pooling and L2 normalization match its
Transformers example. No preprocessing or namespace fingerprint was silently
changed. Existing real namespace
`bge-small-en-v1.5@bd60ce951a6ec4edab8518c1b3301686` and original fixture vectors
were preserved. Reindex still uses an owned fixed UUID upper bound, atomic
vector/cursor commits, explicit resume and immutable model namespaces. It is
not a repeatable-read snapshot: new/corrected memories need a new explicit job.

Full retrieved-set conflict checks still precede compact model context selection.
Citation acceptance still requires an authorized evidence UUID and full exact
quote; post-generation memory eligibility is rechecked. Existing owner/task,
privacy, lifecycle, expiry/deletion, namespace and payload-bound approval rules
remain authoritative. Deterministic tests cover these boundaries and explicit
abstention, malformed/extra authority output, unavailable/timeout, wrong identity/
dimension, cancellation, release/resource refusal, idempotency and reindex recovery.
They are fixture/synthetic evidence, not learned-model privacy or quality scores.
Exact quotation proves source correspondence, not general relevance or entailment.

Planner/Critic/tool authority was not delegated to models or the residency service.
No real external messaging was enabled. JWT/OIDC, non-operator refusal and private
registry boundaries remain in place. Actual local checks exercised missing bearer,
invalid login, cross-owner refusal, forged approval, duplicate/idempotent requests,
canonical approval binding and simulated NOT SENT execution. Expired authorization
and other failure cases are deterministic backend tests; no penetration/security
certification, advisory/container scan or real vision/judge evaluation is claimed.

### Post-change validation and measured evidence

| Executed check | Actual result |
| --- | --- |
| Full current-source PostgreSQL backend suite | **568 passed, 1 explicit real-model skip**, 59.49 seconds |
| Backend Ruff lint / format / dependency compatibility | PASS; 107 app/test files already formatted; pip check PASS |
| Host residency/process/resource tests | **12 passed**, final run 0.049 seconds |
| Frontend lint / typecheck / native production build | PASS, existing installed dependencies |
| Full replay browser profile, retries=0 | **50 passed**, 5 explicit profile skips, 1.2 minutes |
| Separate strict local-auth profile | **3 passed**, 2.8 seconds |
| Separate actual local Keycloak OIDC profile | **2 passed**, 3.3 seconds |
| Phase 7 FULL / SMOKE / baseline REGRESSION | **104/104**, **10/10**, **25/25**, gate PASS |
| Cautious REGRESSION candidate | **23/25**, expected gate FAIL |
| Kafka duplicate / forged approval / HITL | PASS; 3 duplicates, 3 forged-envelope dead letters, no duplicate effects |
| Actual broker outage / outbox recovery | PASS; same committed task, pending events drained in **26.913 seconds** from restart command |
| Restart persistence / owner isolation | PASS; identical owned task/run metadata and reindex list; foreign reads 404 |
| Alembic application head / drift | `0011_inference_registry (head)`; no new upgrade operations |
| Evaluation schema cleanup | SQL found zero leftover `nova_eval_%` schemas |
| Go race tests / go vet | PASS using cached local compiler image, network disabled; race test reported cached |
| Final whitespace / candidate artifact checks | PASS; text-only source candidate, ignored runtime outputs excluded |

Browser coverage is 55 cases across three distinct profiles, not one 55-pass
invocation. Tests ran sequentially by suite using existing images/current source
bind mounts, with no new image build or dependency/model download. The host tests
use fake runtime callbacks plus a real small non-model child termination test;
no torch import or model load was required. New deterministic coverage includes
valid grounded answer/abstention, truncated/malformed/fenced JSON, invalid authority,
sanitized paths, owned safe ledger diagnostics, cancellation during generation,
a duplicate lease and partial-batch rollback after the first vector write followed
by successful explicit resume. That rollback is not an interrupted real-model
transaction.

Intermediate failures are retained: the first full run had 567 passed / one failed /
one skip because the new ledger test requested default TEXT from its STRUCTURED-only
synthetic provider. The policy correctly refused it; the test request was corrected
to the intended STRUCTURED capability. The next full run had 516 passed / one failed /
52 setup errors after the ephemeral test PostgreSQL hit its 512 MiB cap; Docker
confirmed OOMKilled. Only the disposable test services were restarted. The successful
run kept 512 MiB and 32 MiB shared_buffers; test-only WAL retention was bounded to
64 MiB (minimum 32 MiB), with a checkpoint, avoiding accumulated tmpfs WAL pressure.
Application data/model limits were untouched. Initial formatting/import findings
were fixed. A restart harness initially treated transient HTTP 503 as a terminal
failure; its readiness loop was corrected to wait for readiness, then a fresh actual
restart and equality/foreign-owner checks passed. No assertion or test threshold
was weakened; these initial failures are not counted as passes.

Authenticated FULL run `a57c8031-3392-46f7-b05a-8add700210a0`; SMOKE `c1dc7bd0-36f0-452e-b1e7-93a84f644c72`;
baseline REGRESSION `0ad84da2-f333-4318-822c-4f27a30746b3`; cautious `bf487e91-cc2d-4b4a-ba68-1b1d25180cdf`.
New fixture acceptance run `59efe030-871c-4312-a3d2-b3522019e6fb`, task `a1fa341d-60c4-4811-aa38-ba65aec21322`,
retained after restart. Actual Kafka acceptance task `9977fafb-e3b6-470f-a601-7bc095afe7a8`,
proposal `05e29e7e-7e7e-46ca-8ceb-d1a2d4d23286` retained payload-bound approval and
SIMULATED / NOT SENT execution. The two-task fixture continuity sample measured
seven HTTP requests, P50 13.080 ms, P95 23.299 ms and consumer catch-up .855 seconds;
these are fixture continuity timings, not model performance or production capacity.
Read-only restart checks also retained the prior real task and embedding run IDs,
with unchanged reindex metadata; reading prior results is not new real execution.

No new real embedding/generation/acquisition/validation/release latency, tokens,
model RSS, TTFT or throughput was measured. Earlier real latency/RSS/usage values
above were neither overwritten nor reused as new results. Full hosted CI,
Kubernetes/Terraform rollout and NetworkPolicy enforcement remain UNVERIFIED under
their historical qualifications; no production deployment sign-off is given.

### Capability disposition and remaining acceptance gate

| Capability | State in this review |
| --- | --- |
| Safe diagnostics, constrained grounded protocol, lease inference guard | IMPLEMENTED; EXECUTED/MEASURED/EVALUATED with synthetic/fixture tests |
| Private real model registry / resource approval | CONFIGURED but disabled; no fresh activation approval |
| Existing learned embedding/reindex/retrieval and text success | Historically EXECUTED/MEASURED; preserved, not rerun |
| Corrected grounded transport against installed Ollama | UNVERIFIED; BLOCKED pending scoped approval |
| Successful real grounded citation/privacy acceptance | NOT EXECUTED in this review; mandatory item still open |
| Historical real RAG | FAILED; no answer exposed, no retrospective cause invented |
| Explicit abstention and invalid-output refusal | EXECUTED/EVALUATED deterministically; real acceptance pending |
| General retrieval/model quality, no-answer calibration, human review | UNVERIFIED; no new labels or quality claim |
| Real interrupted partial-batch recovery, sustained load, streaming/TTFT | UNVERIFIED |
| Vision, learned judge | NOT EXECUTED; REAL LLM JUDGE NOT CONFIGURED |

The next required approval is the exact [two-cycle/profile proposal](phase-9-final-acceptance-plan.md),
followed by another passing preflight and verified offline regression/configuration.
Neither the 96-token alias nor its controller allowance exists yet. No model may
be loaded based on this report alone. At least one valid real grounded answer
passing schema, citation and privacy checks is still mandatory before Phase 9 can
be COMPLETE. A failed future case must remain failed, with output cleared.

### Stop state, security review and proposed checkpoint manifest

All task-started validation containers and native frontend server are stopped.
Docker reported zero running containers; ports 3000/8000/8080/8180/11434/11435/11436
have no listener. No model/controller was started in this review, so there is no
new model-unload event to claim. Existing application PostgreSQL/media/Redis/Kafka/
auth/identity volumes remain preserved. Private credentials, model files, venv,
attestations and runtime/browser/build evidence remain ignored. Public metadata/
protocol documentation reads did not download model weights or package archives.

Reviewed tracked and untracked text candidates and scanned for private-key blocks,
JWT literals and long credential assignments: no matching embedded credential
found. Verified runtime/environment/model/build paths remain ignored. This bounded
source review is not a security certification. Validation evidence remains under
ignored paths and /tmp; no prompt/completion/private evidence dump was added.

Exact proposed future staging scope: **47 text files, 19 modified / 28 added**.
It preserves the original 43 candidates, adds diagnostic module/tests/acceptance
proposal and modifies the existing shared routing service. No staging command was
run. The complete intended manifest is:

```text
.github/workflows/local-regression.yml
README.md
backend/app/inference/__init__.py
backend/app/inference/api.py
backend/app/inference/contracts.py
backend/app/inference/evaluation.py
backend/app/inference/models.py
backend/app/inference/providers.py
backend/app/inference/registry.py
backend/app/inference/retrieval-v1.json
backend/app/inference/service.py
backend/app/main.py
backend/app/memory/contracts.py
backend/app/memory/service.py
backend/app/model_registry.py
backend/app/model_routing/api.py
backend/app/model_routing/contracts.py
backend/app/model_routing/diagnostics.py
backend/app/model_routing/kernel_provider.py
backend/app/model_routing/providers.py
backend/app/model_routing/service.py
backend/app/perception/contracts.py
backend/app/perception/service.py
backend/migrations/env.py
backend/migrations/versions/0011_inference_registry.py
backend/pyproject.toml
backend/tests/conftest.py
backend/tests/test_inference.py
backend/tests/test_inference_diagnostics.py
compose.yaml
docs/architecture.md
docs/phase-9-activation-plan.md
docs/phase-9-architecture.md
docs/phase-9-final-acceptance-plan.md
docs/phase-9-final-audit.md
docs/phase-9-human-review.md
docs/phase-9-implementation-spec.md
docs/phase-9-model-download-proposal.json
docs/phase-9-resource-preflight.md
frontend/app/inference/page.tsx
frontend/components/nova-workspace.tsx
frontend/tests/inference.spec.ts
scripts/acceptance_phase9.py
scripts/benchmark_phase9.py
scripts/phase9_embedding_bridge.py
scripts/phase9_residency.py
scripts/test_phase9_residency.py
```

Proposed future commit title:
`Phase 9: integrate local AI inference, semantic memory and grounded RAG`.
Suggested body should disclose the successful bounded real embedding/text evidence,
failed historical grounded run, safe diagnostics and remaining real acceptance
boundary; do not describe Phase 9 as complete until its gate actually passes.

Final Git: main at `f4c430cbf42a1168c3e167780dc8ade8844d450f`, index empty,
no commit, push, remote configuration or history rewrite. No Phase 10.
**STOPPED: Phase 9 NOT COMPLETE; fresh profile/execution approval is required for
its remaining real grounded acceptance.**


## OCTOBER 17 — AUTHORIZED 96-TOKEN FINAL ACCEPTANCE EXECUTION

October 17, 2026 (America/New_York). The positive RAG request ran at approximately
06:14 local time. **PHASE 9 STATUS: NOT COMPLETE. Positive grounded acceptance
FAILED; the insufficiency cycle was NOT EXECUTED because the operator required
an immediate stop after either cycle failed. No inference was retried.**

This section supersedes the earlier pending-approval disposition only for the
explicitly authorized execution below. Historical fixture results, real measurements,
the earlier failed 32-token RAG and the prior offline review remain unchanged.

### Authorization, profile and offline verification

The operator explicitly approved three bounded actions: create
`nova-qwen-phase9-rag96` from the existing verified artifact, perform one positive
LOCAL_REAL HYBRID RAG request, then one insufficiency request only if the first
passed. Maximum scope was two BGE query embeddings, two Qwen generations and two
authenticated RAG cycles, zero inference retries. The approved task and namespace
were exactly `70b45f12-b509-4443-a66f-81b86caf872c` and
`bge-small-en-v1.5@bd60ce951a6ec4edab8518c1b3301686`.

Implemented the separate alias allowance in the existing residency controller:
original alias remains capped at 32; only the new alias permits up to 96. Both
retain context 512, CPU threads 2, GPU layers 0, temperature 0 and concurrency 1.
The controller rejects excess/invalid token limits and runtime override fields.
Existing eight-second inference, 30-second startup, lease, process termination,
network sandbox and resource ceilings were unchanged. Added safe inference/usage
and timestamp observations plus an explicit operator evidence-directory option
so this execution did not overwrite the earlier residency records. Added only
citation/privacy validation duration metadata to the existing application flow;
no schema, ownership, privacy, citation or relevance rule was weakened.

Before model startup, current-source offline regression passed **568 backend tests,
one explicit real-model skip, in 58.70 seconds**. Backend lint/format and pip check
passed (107 app/test files already formatted). **13 host controller tests passed**,
including distinct 32/96 ceilings, override refusal, concurrency, expiry, cancellation,
resource refusal and non-model child cleanup. Initial controller import-order and
line-length lint findings were corrected before the passing lint check. No inference
failure was retried. Frontend/browser/Go/golden/Kafka suites from October 16 were
not rerun here and remain historical; no frontend, gateway, agent, dataset or
messaging implementation changed in this execution.

Fresh tensor SHA-256 checks before and after execution passed:

- BGE, 133,466,304 bytes, revision
  `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`:
  `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.
- Qwen, 986,048,512 bytes:
  `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.

Ollama **0.35.1** created the new alias using existing local weights. `/api/show`
verified context 512 / output 96 / threads 2 / num_gpu 0 / temperature 0, and
`/api/ps` was empty before and after alias creation: no generation or model load
was used to create metadata. The new manifest is 1091 bytes; its distinct parameter
blob is 76 bytes, totaling 1167 logical bytes relative to the original alias's
references. All referenced blob sizes and hashes were verified. The original
32-token alias manifest SHA-256 remains
`dafd3dc8e500e0774baaf6dc50d5792374815c013e8de4a3a98ac026b1473271`.
No original alias/weight was replaced, no cache was pruned and no extra runtime,
package or model weights were downloaded. Runtime generation logs independently
confirm `-c 512 -np 1 -ngl 0 -t 2`, CPU buffers and one slot.

BGE reused isolated Python **3.14.8**, PyTorch **2.14.1**, Transformers **5.20.0**,
CPU float32 and its existing two-thread, batch-one, <=128-token bridge. Library
versions were read without installing packages. Local-files-only/offline loading
and the loopback-only OS sandbox remained in place for model processes. No
unexpected external transport or resource watchdog violation was recorded; no
packet-capture or comprehensive network/security certification is claimed.

### Resource and ownership gates

Initial fresh check: 8 GiB RAM, approximately 16.3 GiB free disk, **922.06 MiB used
swap**, macOS reported 63% free percentage, Docker **4,106,604,544 bytes** unchanged.
Model/controller listeners were absent. A fresh private scoped one-hour attestation
was created before startup; stale October 16 attestations were not reused. The
application used read-only current source/artifact mounts in existing images, local
JWT authentication and only the necessary PostgreSQL/Redis/backend/gateway services.
The authenticated task read matched the expected owner. Private controller bearer
authentication and Docker-to-host reachability were checked by an inventory read,
without acquiring or loading a model.

Before the RAG request, SQL/read-only metadata checks verified three eligible owned
384-dimensional non-simulation vectors in the exact real namespace and three original
32-dimensional fixture vectors. Real vectors were finite/nonzero and the stored
version fingerprint matched BGE. The existing real reindex job remained DONE,
processed=3. Afterward, row IDs, vector digests, dimensions, model namespaces,
simulation flags, timestamps and reindex cursor/state compared identically before
and after. No reindex, historical vector replacement or additional embedding probe
was performed.

| Boundary | Free disk bytes | Used swap MiB |
| --- | --- | --- |
| Initial private preflight | 17,502,392,320 | 922.06 |
| Before BGE acquisition | 17,475,698,688 | 922.06 |
| After BGE termination | 17,477,443,584 | 922.06 |
| Fresh check before Qwen acquisition | 17,477,439,488 | 922.06 |
| After Qwen termination | 17,477,103,616 | 1431.06 |
| Final stopped state | 17,474,338,816 | 1423.06 |

All recorded boundaries passed disk >=5 GiB and swap <2048 MiB. The existing
approximately 0.1-second resource/RSS watchdog remained active. Final macOS reported
free percentage was 54%; that is not guaranteed allocatable model RAM.
No threshold, model-memory declaration, Docker allocation or deadline was raised.

### Executed positive request and exact failure

Exactly one authenticated POST to `/api/v1/inference/generate` used LOCAL_REAL,
RAG, HYBRID, max_output_tokens=96 and the approved question:
**Which cuisine do I prefer?**

Request/trace UUID: `507ba1e3-d8ea-4c5e-ba4c-28918fbe045b`.
Application run: `a1b2864b-7e05-4e11-a004-4fe8479ad7f9`.
Retrieval snapshot: `4c2e129b-406a-4f3e-a57a-c607b84a8ec9`.

The actual sequence was BGE query embedding/retrieval → verified process/listener
termination → fresh host resource check → Qwen acquisition/generation → structured
validation and post-generation privacy revalidation → verified Qwen termination.
There were exactly two controller acquisitions, one per model, with nonoverlapping
start/stop records. BGE's transport produced the real 384-dimensional query vector
through VersionedEmbedding; no simulation or fixture fallback was used.

The persisted retrieval snapshot contains three real-namespace hits. Read-only
inspection confirms the approved cuisine memory
`4d4b4842-c804-4e72-90c9-7162d6436c37` ranked first and was selected for the compact
model context. Full-set conflict detection was false. No relevance threshold or
filter was added or changed. The prior retrieval-v1 quality scores were not rerun
or overwritten; this one request is not a new relevance benchmark.

**Application state: DONE, valid explicit abstention, claims=[], citation_ids=[].
Positive acceptance state: FAILED (`NO_POSITIVE_GROUNDED_ANSWER`).**
The model produced no cuisine claim despite the selected owned cuisine evidence.
The existing GroundedOutput schema and post-generation privacy path accepted the
abstention. The ledger records one uncached invoked local attempt, finish_reason=stop,
141 input tokens and 8 output tokens. This was not a JSON parsing failure, schema
refusal, timeout or output-limit event. Eight tokens were below the approved 96;
there is no evidence of truncation in this run. Why the model chose to abstain is
not established. No rationale, forced answer, citation repair or additional generation
was requested to explain or fix it.

No fabricated citation or unsupported positive claim was accepted, but no real
positive citation/quote acceptance succeeded either. Empty claims must not be
reported as positive grounded-answer acceptance. The application's valid-abstention
DONE state is intentionally distinguished from the failed positive test criterion.
Raw private model text/prompts are not diagnostic evidence; the controlled response
was checked in memory, while the retained run evidence contains safe metadata and
no raw completion. The exported retrieval evidence was projected to IDs/ranks/scores
without memory contents; the existing application retrieval snapshot was preserved.

### Measured latency, usage and residency

| Actual observation | BGE | Qwen 96-token profile |
| --- | --- | --- |
| Controller process readiness | 3.901 s, includes BGE readiness | 0.507 s, server readiness only |
| Forwarded inference HTTP duration | 35.803 ms | 4383.683 ms, includes lazy weight load |
| Peak sampled aggregated RSS | 367,968,256 bytes / 350.92 MiB | 1,320,484,864 bytes / 1259.31 MiB |
| Unchanged model ceiling | 1024 MiB | 2048 MiB |
| Controller shutdown | 32.010 ms | 26.048 ms |
| Reported text usage | not reported | 141 input + 8 output = 149 tokens |

Authenticated full RAG HTTP wall time: **10976.815 ms**.
Application model-call latency: **5567.355 ms** (Qwen provider acquisition,
inference, cleanup/validation scope). Post-generation citation/privacy validation:
**9.504 ms**. These scopes differ and are not additive components of
a complete instrumentation trace. Separate model-only latency, TTFT, streaming,
throughput, instantaneous hardware memory peaks and an untouched cold OS-cache
benchmark were not measured. Sampled process-tree RSS is not a hard memory quota.
No new cost-saving or model-quality claim follows from these measurements.

### Separate outcomes and mandated stop

| Outcome | This authorization |
| --- | --- |
| Successful positive grounded answers | **0** |
| Valid explicit abstentions observed | **1**, on the positive question; failed that question's required outcome |
| Failed acceptance cycles | **1**, positive case: NO_POSITIVE_GROUNDED_ANSWER |
| Separate insufficiency/abstention cycle | **NOT EXECUTED** after the positive failure |
| BGE query-embedding requests / Qwen generations | **1 / 1** |
| Authenticated RAG cycles / inference retries | **1 / 0** |
| External actions/messages | **0** |

The question **What is my spacecraft launch authorization code?** was not sent.
There is no second attempt marker, second query embedding or second generation.
The unused scope was not silently exercised. No future retry/extra generation is
implicitly authorized after the operator's stop-on-failure boundary.

### Shutdown, evidence, Git and final acceptance gate

Native Qwen unload was requested, then the task-owned process trees were terminated
and listeners verified absent. BGE and Qwen were never resident together. Both
model acquisition records report verified shutdown. The controller was stopped
with KeyboardInterrupt after its cleanup finally block; no model/listener remained.
All task-started application services are stopped; Docker reported zero running
containers. Ports 3000/8000/8080/11434/11435/11436 have no listener. Original and new
private Qwen configurations plus BGE configuration all have resource_approved=false.
The private scoped attestation is closed; a final mode-0600 attestation records no
active approval/model. The small new alias metadata remains; no model/cache removal
was used. Application PostgreSQL/media/Redis/Kafka/auth/identity volumes are preserved.

Safe evidence resides in ignored `.local/phase9/final-acceptance-20261017`; credentials,
private configs and closed attestations remain ignored under `.secrets/phase9b`.
Earlier evidence directories were not overwritten. No new model weights, package,
source build, runtime install, cloud/paid API, external message or deployment occurred.
Required external spend **$0**; host compute/electricity unpriced. Real vision and
LLM judging remain unconfigured/unexecuted. Kubernetes/NetworkPolicy and production
qualifications remain unchanged.

This authorization changed source only in the existing residency controller,
its host tests, the inference service's validation timing and this additive audit.
The source candidate remains **47 text files, 19 modified / 28 added**, with the
exact staging manifest recorded in the preceding section. Branch main and HEAD
`f4c430cbf42a1168c3e167780dc8ade8844d450f` are unchanged; index empty,
no commit/push/remote configuration or history rewrite. Git whitespace checks pass.
No Phase 10.

**Final acceptance gate: NOT COMPLETE.** A valid real grounded answer passing
schema, owned citation, exact quote and privacy checks remains absent. This run
demonstrated an actual valid-abstention path and safe sequential residency, but
failed the positive acceptance requirement; the separate insufficiency case is
unverified. Historical 32-token failure is not retrospectively diagnosed by this
new result. **STOPPED after the first failed acceptance cycle; awaiting further
operator instructions.**


## PHASE 9D — OFFLINE GROUNDED ANSWER RELIABILITY INVESTIGATION

October 17, 2026 (America/New_York). **Offline investigation and deterministic
regression completed. No BGE/Qwen load or real inference occurred. Phase 9 remains
NOT COMPLETE; the reason for Qwen's prior abstention is not conclusively established.**
The October 17 authorization was not reused. No new real-model execution approval
was provided by Phase 9D. The earlier positive failure and skipped insufficiency
cycle remain unchanged historical results.

### Confirmed observations and unresolved hypotheses

Reviewed the grounded instruction template, native JSON schema, compact context
selection, full-set conflict check, strict response parser, exact-UUID/full-quote
validator, privacy revalidation and retained safe execution metadata. The prior
ledger shows a valid eight-token abstention ending with stop, not an exhausted
96-token budget or JSON/schema failure. Its cuisine record ranked first and was
selected; no full-set conflict was recorded. No new model result was generated to
explain that decision.

The prompt and schema are structurally consistent: claims use evidence_id and quote;
non-abstaining output requires claims; abstaining output must have none. Python's
cross-field validator enforces that relationship even though the JSON schema does
not encode the entire conditional rule. The existing schema defaults claims to an
empty list, so a short explicit abstention is valid. This default was not changed.
The positive-output instructions were underspecified: only the abstention form was
shown, with no positive example or explicit id/text → evidence_id/quote mapping.
That is a confirmed instruction gap, not a proven causal explanation of Qwen's choice.

A second ambiguity concerns the question's referent. A bounded read-only metadata
query against the existing application PostgreSQL verified the approved cuisine
record `4d4b4842-c804-4e72-90c9-7162d6436c37` is ACTIVE, USER-scoped and owned by
the approved task's owner. Its subject is the public fixture entity label
`review_fixture`, predicate preferred_cuisine, and its value/normalized text match
the public pinned retrieval corpus. The check returned only metadata/booleans,
not raw source text or private prompts. No application record was modified.

The compact context contains query plus evidence id/text; it supplies no explicit
binding from that fixture subject label to the first-person “I.” Ownership grants
access, not proof that every stored subject is the requester. Subject-reference
ambiguity, the asymmetric old instruction template and small-model instruction
following remain hypotheses. No latent reasoning or model-quality cause is inferred
from a deterministic double. The investigation does not assert that the original
first-person question has now been answered or that the new prompt fixes Qwen.

### Exact changes and preserved boundaries

Only production change: `backend/app/inference/providers.py`, grounded system
instructions inside LocalProvider.generate. The new template:

- Explains the positive form with claims, evidence_id, quote and abstain=false.
- Maps the chosen evidence item's id unchanged to evidence_id and its full text
  verbatim to quote; requests one concise supported claim when directly relevant.
- Requires abstention for missing, irrelevant or conflicting evidence, or a full
  exact quote that cannot fit the stated output budget. The numeric budget is
  included, rather than requiring the model to guess its ceiling.
- Keeps evidence explicitly untrusted and forbids tools/actions/approvals, invented
  IDs, altered quotes and silently treating another mentioned subject as the user.

No cuisine value, real UUID, identity mapping or answer was hardcoded into the
production prompt. Private evidence is not interpolated into the system message;
source content remains in the JSON user-data message. No prompt logging was added.

`backend/tests/test_inference_diagnostics.py` gained scripted construction and
validation coverage. The new [acceptance proposal](phase-9d-acceptance-proposal.md)
is documentation only. This audit is additive. The output schema, UUID and quote
validators, memory eligibility/ownership/lifecycle, post-generation privacy checks,
full-retrieved-set conflict checks, metadata diagnostics and approval policy remain
unchanged. FIXTURE stays the default; LOCAL_REAL stays opt-in; DISABLED still refuses.
No routing fallback, relevance threshold, reindex/namespace, dataset or historical
score was changed. Context 512, output 96 for the existing alias, CPU threads 2,
GPU layers 0, temperature 0, concurrency 1, model ceilings and deadlines are unchanged.

### Offline reproduction and security validation

HTTPX MockTransport captured the actual constructed request in memory. Assertions
verified model alias nova-qwen-phase9-rag96, purpose GROUNDED, API operation RAG in
the application tests, query preservation, selected evidence UUID/full text,
96-token budget, temperature/streaming options and the exact unchanged JSON schema.
Selection tests preserve the full conflict decision before selecting at most one
source. Unicode, quotes and newlines round-trip exactly. Oversized context fails
CONTEXT_LIMIT before transport rather than being silently truncated.

A separate targeted test reconstructed the historical controlled evidence from
the public corpus and recorded UUIDs, including the original question, and asserted
its selected cuisine id/text and wire format. Its response is explicitly scripted
abstention; it neither replays Qwen nor predicts what the new prompt will do.
Private runtime prompts/evidence were not read into test fixtures or written to logs.

Scripted scenarios cover a directly relevant claim, irrelevant/missing/conflicting
source abstention and instruction-like source remaining in the user-data role.
Application tests run against the disposable test DB and transport doubles. They
reject fabricated UUIDs, changed quotes, extra approval/tool fields and invalid JSON,
with output cleared. Direct foreign-task access fails before provider selection.
Additional fault tests change evidence ownership or mark it deleted during scripted
generation and verify post-generation EVIDENCE_CHANGED refusal. Existing full-suite
retrieval/authentication/privacy tests separately cover pre-retrieval owner/lifecycle
filtering and expired/restricted evidence.

These are deterministic wiring/security checks, **not real-model quality scores**.
Scripted relevant/irrelevant responses cannot establish that Qwen follows the new
instructions or resists prompt injection. Exact quote correspondence still does
not prove general relevance/entailment. No validator, approval hash or action authority
was weakened to make these checks pass.

| Executed validation | Actual result |
| --- | --- |
| Full backend suite after final production prompt change | **585 passed, 1 explicit real-model skip**, 59.42 seconds |
| Additional historical-payload reconstruction after that full run | **1 passed**, 0.22 seconds |
| Host controller/resource/cancellation/process tests | **13 passed**, 0.051 seconds |
| Backend lint / format / pip compatibility | PASS; 107 app/test files formatted/checked; pip check PASS |
| Final whitespace / source artifact checks | PASS |

The full suite first passed 583 cases; adding the original-query preservation and
Unicode cases produced the final 585-pass invocation. The additional one-case
historical reconstruction was run separately without changing production code;
these are not one 586-pass invocation. Initial test formatting/import findings
were corrected before passing lint. No failing model request was rerun because
none was made. Test doubles did not start an inference runtime or import an ML
framework. Tests used the existing cached backend image with current source mounted,
explicit external/real-model test flags disabled, a 512 MiB test PostgreSQL with
bounded WAL and isolated Redis. Application data/volumes were not reset.

Broader browser, frontend build, Go, golden HTTP and Kafka deployment regressions
were not rerun: their code/contracts were unchanged, and the changed local grounded
prompt plus all backend security paths were covered by the full backend suite.
Their previous passes remain historical. No hosted CI, production/security
certification, Kubernetes rollout or NetworkPolicy enforcement is claimed.

### Resources, integrity and stop state

Initial read-only resource check: 8 GiB RAM, **1359.06 MiB swap used**, approximately
16.27 GiB host free disk; Docker reported no running containers. Before the full
suite, swap was 1343.06 MiB. Final observation at approximately 06:30 local time:

| Check | Actual observation |
| --- | --- |
| Physical RAM | 8,589,934,592 bytes / 8 GiB |
| Free disk | 17,462,067,200 bytes / 16.263 GiB |
| Used swap | 1335.06 MiB, below 2048 MiB |
| macOS reported free percentage | 52%, not guaranteed allocatable model RAM |
| Docker memory allocation | 4,106,604,544 bytes, unchanged |
| Model loads / real generations / new query embeddings | **0 / 0 / 0** |
| Model ceilings / startup and inference deadlines | unchanged |

Fresh read-only tensor hashing again matched BGE
`3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`
and Qwen
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.
No weight loader was invoked and no artifact was modified or downloaded.

Only ephemeral test services and, separately, existing PostgreSQL for the read-only
metadata check were started. They are stopped. No backend/gateway application
server, model/controller or native frontend was started. Docker reports zero running
containers; ports 3000/8000/8080/11434/11435/11436 have no listener. BGE and both Qwen
private configurations remain resource_approved=false. The fresh ignored mode-0600
`.secrets/phase9d-investigation-attestation.json` records offline scope and
operator_resource_approved=false / model_load_approved=false. It is not execution
authority. No old approval was exported to a model-enabled process.

No new real inference latency/tokens/RSS, retrieval score or quality metric was
measured. The previous 96-token positive abstention, its timings/RSS and skipped
insufficiency case are preserved exactly as audited. No model/cache/app volume was
deleted, no resource gate raised, and no paid API, cloud or external message used.
Required external spend $0; host compute/electricity unpriced.

### Fresh proposal, remaining uncertainty and Git

The [Phase 9D proposal](phase-9d-acceptance-proposal.md) requests one future positive
cycle, then one insufficiency cycle only if positive succeeds, using the existing
BGE artifact, owned task/namespace and 96-token Qwen alias. To avoid silently treating
a fixture subject as the requester, the positive question is explicitly
**Which cuisine does review_fixture prefer?** The negative question asks for that
entity's spacecraft launch authorization code. These are new proposed cases;
the original first-person case is not relabeled or overwritten. No answer value
is embedded into the prompt or proposal.

Fresh explicit scope approval and preflight are required before either model load.
The proposal retains all resource, residency and deadline limits, requires verified
unload between models and stops after the first failure with no inference retry.
The longer template's actual Qwen token count, 512-token runtime fit, real positive
claim behavior and real insufficiency behavior remain UNVERIFIED. Application
serialization tests establish no truncation before transport, not a proof of runtime
context behavior. Do not raise limits or invent a subject mapping to force a pass.

Phase 9 remains NOT COMPLETE because no positive real grounded answer has passed
all acceptance checks. Phase 9D completed the authorized offline work; it does not
authorize real acceptance, resolve the model's latent reason or establish quality.
Real judging/vision and deployment qualification remain unchanged/unverified.

Git: main at `f4c430cbf42a1168c3e167780dc8ade8844d450f`, index empty,
no remotes, no commit/push/history rewrite. All Phase 1–8 checkpoints and historical
golden/threshold/audit files remain unchanged. Current candidate: **48 text files,
19 modified / 29 added**, the preceding 47-file manifest plus the new proposal.
For exact future review scope, the current unstaged/untracked manifest is:

```text
.github/workflows/local-regression.yml
README.md
backend/app/inference/__init__.py
backend/app/inference/api.py
backend/app/inference/contracts.py
backend/app/inference/evaluation.py
backend/app/inference/models.py
backend/app/inference/providers.py
backend/app/inference/registry.py
backend/app/inference/retrieval-v1.json
backend/app/inference/service.py
backend/app/main.py
backend/app/memory/contracts.py
backend/app/memory/service.py
backend/app/model_registry.py
backend/app/model_routing/api.py
backend/app/model_routing/contracts.py
backend/app/model_routing/diagnostics.py
backend/app/model_routing/kernel_provider.py
backend/app/model_routing/providers.py
backend/app/model_routing/service.py
backend/app/perception/contracts.py
backend/app/perception/service.py
backend/migrations/env.py
backend/migrations/versions/0011_inference_registry.py
backend/pyproject.toml
backend/tests/conftest.py
backend/tests/test_inference.py
backend/tests/test_inference_diagnostics.py
compose.yaml
docs/architecture.md
docs/phase-9-activation-plan.md
docs/phase-9-architecture.md
docs/phase-9-final-acceptance-plan.md
docs/phase-9-final-audit.md
docs/phase-9-human-review.md
docs/phase-9-implementation-spec.md
docs/phase-9-model-download-proposal.json
docs/phase-9-resource-preflight.md
docs/phase-9d-acceptance-proposal.md
frontend/app/inference/page.tsx
frontend/components/nova-workspace.tsx
frontend/tests/inference.spec.ts
scripts/acceptance_phase9.py
scripts/benchmark_phase9.py
scripts/phase9_embedding_bridge.py
scripts/phase9_residency.py
scripts/test_phase9_residency.py
```

Only the grounded provider template, its existing diagnostic tests, this audit and
the new proposal were written in the source candidate during Phase 9D. Private
attestation/runtime outputs remain ignored; bounded credential/artifact pattern
checks found no embedded private keys or JWTs in the source candidate. This is not
a comprehensive security scan. No staging or checkpoint operation occurred.
**STOPPED after offline investigation and audit; fresh model authorization absent.
No Phase 10.**


## PHASE 9E — EXPLICITLY AUTHORIZED FINAL GROUNDED ACCEPTANCE

October 17, 2026 (America/New_York). Execution at approximately 06:39 local time.
**PHASE 9 ACCEPTANCE: NOT MET / NOT COMPLETE. The positive entity-qualified cycle
FAILED because it returned a valid abstention rather than a grounded cuisine claim.
The conditional insufficiency cycle was NOT EXECUTED. No inference was retried.**
This section adds actual evidence without changing any historical results or
retrospectively diagnosing the original first-person question.

### Authorized scope and pre-execution checks

The operator supplied fresh explicit Phase 9E approval for the exact proposal:
one positive authenticated LOCAL_REAL HYBRID RAG request, then one insufficiency
request only if positive passed. The approved positive question was
**Which cuisine does review_fixture prefer?** The conditional negative question was
**What is review_fixture's spacecraft launch authorization code?**
Task: `70b45f12-b509-4443-a66f-81b86caf872c`.
Namespace: `bge-small-en-v1.5@bd60ce951a6ec4edab8518c1b3301686`.
Existing alias: `nova-qwen-phase9-rag96`.
Maximum scope: two BGE query embeddings, two Qwen generations, two RAG cycles,
zero inference retries. The older October 17 approval was not reused.

Fresh initial observations: **1263.06 MiB swap used**, **17,454,600,192 bytes
free disk**, 8 GiB RAM, unchanged Docker allocation **4,106,604,544 bytes**.
No model/controller listeners, running Ollama process or running containers were
found. Verified the unchanged CPU/context/concurrency profile from the existing
alias's referenced parameters and, at runtime, `/api/show`: context 512, output 96,
threads 2, GPU layers 0, temperature 0, concurrency 1. No alias was created or altered.

Read-only tensor SHA-256 and existing alias/blob-size/digest checks passed before
execution and tensor checks passed again afterward:

- BGE: 133,466,304 bytes, revision
  `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, SHA-256
  `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.
- Qwen: 986,048,512 bytes, SHA-256
  `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.

Current-source offline preflight regression passed **586 backend tests, one explicit
real-model skip, in 59.70 seconds**. Ruff lint/format and pip compatibility passed;
107 app/test files checked/formatted. **13 controller tests passed in 0.044 seconds**.
No production code, schema, validator, instruction template, threshold, test or
runtime limit was changed during Phase 9E. Broader unchanged frontend/Go/browser/
Kafka/golden execution was not repeated; its earlier evidence remains historical.

A fresh private scoped host attestation was created, and only BGE plus rag96
configurations were temporarily enabled. Their private artifact bindings,
managed-residency setting and host/container gate were verified. The original
32-token configuration remained disabled. Direct authenticated FastAPI owner/task
reads matched the expected owner. Read-only checks verified three finite/nonzero
384-D learned vectors in the exact real namespace plus three original fixture
vectors and the existing DONE/processed=3 reindex state. A private bearer-authorized
controller inventory read verified container-to-host connectivity without acquiring
or loading a model.

### Positive request, result and exact failed criterion

Exactly one POST to `/api/v1/inference/generate` used LOCAL_REAL, operation RAG,
retrieval HYBRID, max_output_tokens=96 and the approved entity-qualified question.

- Request/trace ID: `78865a87-3f25-484c-b382-6bdef1877640`.
- Application run ID: `16ea128a-af83-4ded-ad01-6f8ca3d9cdbb`.
- Retrieval snapshot: `8ea383fe-de2c-4518-9df3-a898e5cc7add`.
- Model-call ID: `86990cd8-4221-4d7c-9f12-3854049bc205`.

The retrieval snapshot ranked the approved cuisine evidence
`4d4b4842-c804-4e72-90c9-7162d6436c37` first. The three hit IDs all identify
non-simulation results in the approved BGE namespace. Its recorded cosine similarity
was **0.821441910094993**; this is one observed ranking score, not a calibrated
relevance threshold or a new retrieval-quality benchmark. No threshold was introduced.
No reindex, standalone embedding probe, vector replacement or dataset change occurred.

The actual order was one BGE acquisition/query embedding/retrieval → verified BGE
termination and listener disappearance → fresh passing resource check → one Qwen
acquisition/generation → structured validation and post-generation eligibility
revalidation → verified Qwen termination. The controller recorded exactly one
nonoverlapping residency interval per model. BGE was never resident with Qwen.

**Application outcome: DONE with a valid explicit abstention, claims=[],
citation_ids=[], error=null. Positive acceptance outcome: FAILED,
NO_POSITIVE_GROUNDED_ANSWER.** The response passed the existing abstention contract
and privacy path, but returned no supported cuisine claim. An empty citation set
is not a successful positive UUID/quote acceptance result.

The owned ledger records one actual invoked phase9-local attempt, cache MISS,
finish_reason=stop, correct alias and Qwen fingerprint, simulation=false,
fallback_used=false and replayed=false. Reported usage was **212 input / 8 output
/ 220 total tokens**. The approved 96-token output limit was not exhausted.
Runtime logs report a 512-token context, 212 prompt tokens and truncated=0 at
release. No parse/schema failure, timeout or output-limit event was recorded.
The clarified prompt/schema path executed; its real positive-answer requirement
still failed. The model's reason for choosing abstention remains unresolved.

No new prompt, identity assumption, schema repair, citation substitution, forced
answer, larger budget or follow-up generation was used to chase a passing result.
The originally failed first-person case remains historical; this entity-qualified
case also failed positive acceptance. These finite results do not establish the
causal explanation of either model decision or general model quality.

### Actual measurements and resource boundaries

| Observation | BGE | Qwen rag96 |
| --- | --- | --- |
| Controller startup readiness | 3.593 s, includes BGE readiness | 0.465 s, server readiness only |
| Forwarded inference HTTP duration | 37.789 ms | 5368.400 ms, includes lazy weight load |
| Peak sampled process-tree RSS | 378,437,632 bytes / 360.91 MiB | 1,355,563,008 bytes / 1292.77 MiB |
| Unchanged memory ceiling | 1024 MiB | 2048 MiB |
| Verified shutdown duration | 30.688 ms | 31.590 ms |
| Reported usage | not reported | 212 input + 8 output = 220 tokens |

Authenticated full RAG HTTP wall time: **11390.498 ms**.
Application Qwen model-call latency: **6537.746 ms**, including its provider
acquisition/inference/cleanup scope. Post-generation citation/privacy validation:
**9.509 ms**. These are different timing scopes, not a complete
additive performance trace. Separate model-only load/generation latency, TTFT,
streaming and sustained throughput were not measured. New processes loaded models,
but OS page-cache state was not controlled; this is not a cold-cache benchmark.
Sampled aggregated RSS is not a hard instantaneous RAM quota.

| Resource boundary | Free disk bytes | Swap used MiB |
| --- | --- | --- |
| Initial preflight | 17,454,600,192 | 1263.06 |
| Before BGE acquisition | 17,453,305,856 | 1247.06 |
| After BGE release | 17,453,211,648 | 1247.06 |
| Before Qwen acquisition, fresh check | 17,453,207,552 | 1247.06 |
| After Qwen release | 17,453,215,744 | 1365.81 |
| Final stopped snapshot | 17,451,831,296 | 1357.81 |

All recorded boundaries passed disk >=5 GiB and swap <2048 MiB; no existing
resource/RSS/deadline watchdog violation was recorded. The eight-second inference,
30-second startup, BGE batch-one/128-token/two-thread CPU profile, Qwen CPU/context/
concurrency bounds and loopback-only sandbox/offline restrictions were retained.
No resource allocation or threshold was increased. Final RAM remains 8 GiB, Docker
allocation unchanged, macOS reported free percentage 53%; that percentage is not
guaranteed allocatable model memory.

### Separate acceptance outcomes and mandated stop

| Outcome | Phase 9E actual result |
| --- | --- |
| Successful supported cuisine answers | **0** |
| Valid explicit abstentions observed | **1**, on the positive question |
| Failed acceptance cycles | **1**, positive: NO_POSITIVE_GROUNDED_ANSWER |
| Conditional insufficiency acceptance | **NOT EXECUTED**, because positive failed |
| BGE query embeddings / Qwen generations | **1 / 1** |
| Authenticated RAG cycles / inference retries | **1 / 0** |
| Fabricated claims/citations accepted | **0** |
| External actions/messages | **0** |

The spacecraft question was not sent. There is no second attempt marker and no
second BGE or Qwen acquisition. Unused conditional scope was not exercised after
the failed positive case. The execution scope is closed; no further attempt is
implied by the earlier approval.

### Shutdown, preservation, evidence and acceptance disposition

Native Qwen unload was requested and both runtime process trees were terminated;
existing descendant/listener verification succeeded. The controller was then stopped
through its cleanup finally block (KeyboardInterrupt shutdown). All task-started
application services are stopped, Docker reports zero running containers, and
ports 3000/8000/8080/11434/11435/11436 have no listener. BGE and both Qwen private
configurations are resource_approved=false. The scoped attestation is closed;
a final mode-0600 private attestation records no active approval or model.

Before/after SQL snapshots compare identically for all six historical embedding
rows: IDs, dimensions, namespaces, simulation flags, timestamps and vector digests,
along with the existing reindex state/cursor. Both alias manifest digests and tensor
hashes remain unchanged. No deletion, pruning, alias rewrite or vector replacement was used to force a
result. Normal application accounting/retrieval writes were preserved. Application
PostgreSQL/media/Redis/Kafka/
auth/identity volumes are preserved.

Safe projected evidence is ignored under `.local/phase9/phase9e-acceptance-20261017`;
credentials/configs/closed attestations remain ignored under `.secrets/phase9b`.
No historical evidence file was overwritten. Diagnostic evidence excludes raw
private prompts, completions and memory text. Existing application retrieval
snapshot and documented temporary cache behavior are unchanged. No model/package
installation/download, cloud/paid API, external message, commit/push or remote
configuration occurred. Required external spend $0; host compute/electricity unpriced.

Only this additive audit was changed in the source candidate during Phase 9E.
There are still **48 text candidates, 19 modified / 29 added**, as listed in the
Phase 9D manifest. Branch main and HEAD
`f4c430cbf42a1168c3e167780dc8ade8844d450f` are unchanged; index empty,
no remotes/history rewrite. Phase 1–8 checkpoint commits, previous measured audits,
golden dataset and thresholds remain preserved. Whitespace checks pass. No Phase 10.

**Phase 9 acceptance criteria are NOT MET.** A valid real positive grounded answer
with supported UUID/exact quote/privacy validation remains missing; the separate
insufficiency question remains unexecuted. Other historical successes and current
safe abstention/sequential residency do not satisfy that positive requirement.
No production, general-quality, vision, real-judge or Kubernetes/NetworkPolicy
sign-off is added. **STOPPED after the first failed cycle, awaiting further instructions.**

## PHASE 9F — OFFLINE CONTROLLED GROUNDED RAG DIAGNOSIS

October 17, 2026 (America/New_York). **Offline investigation PASS; real-model
reliability and Phase 9 acceptance remain NOT COMPLETE. Zero model loads, BGE
embeddings, Qwen generations or authenticated real RAG cycles occurred.** Earlier
approvals were not reused. The Phase 9E failure and skipped insufficiency cycle
remain historical failures/unexecuted work, respectively.

### Actual execution evidence reviewed

Reviewed the retained Phase 9E cycles/residency records and Qwen runner log,
current prompt/schema/context construction, parser, exact UUID/full-quote
validation and post-generation eligibility checks. The actual positive run
`16ea128a-af83-4ded-ad01-6f8ca3d9cdbb` selected the cuisine record first, invoked
one uncached Qwen attempt, and returned a valid abstention: 212 input / eight
output tokens, finish_reason=stop, with no reported truncation. Its application
DONE state did not meet positive acceptance. No raw historical completion or
private prompt was recovered, inferred or logged by this investigation.

The explicitly named subject in 9E removed the earlier first-person ambiguity,
but abstention persisted. Historical ownership and source metadata identify
ACTIVE, owner-authorized cuisine evidence in the correct namespace. Offline
reconstruction uses the versioned public retrieval corpus and known controlled
IDs, not an assumption that ownership makes the source subject the requester.
No application database, memory, vector or namespace was modified or reindexed.

### Confirmed defect and exact correction

The installed Homebrew receipt and formula identify Ollama **0.35.1_1**, upstream
commit `b0c1ca4f7549d7acdfa52a7dcffc934bc63a43ce`, with llama.cpp **b11232** at
`6f767fe960c3b97cf37fac4626c86400561ca1e4`. The inspected Homebrew patches concern
MLX bindings, not the CPU schema converter. No runtime was launched to inspect
this provenance.

The pinned [schema converter](https://github.com/ggml-org/llama.cpp/blob/6f767fe960c3b97cf37fac4626c86400561ca1e4/common/json-schema-to-grammar.cpp)
partitions object fields into required and optional groups and emits required
fields first. Our unchanged root schema requires only `abstain`; `claims` is
optional. Both existing instruction examples instead began with `claims`.
**Confirmed implementation mismatch: the examples' serialization order disagreed
with the generated grammar's required-first order**, although either order is
valid ordinary JSON/Pydantic input. This is a source-established incompatibility
between examples and constrained serialization, not proof of the model's reason
for choosing true or abstaining.

Only production correction: in `backend/app/inference/providers.py`, reorder
both examples to `abstain` then `claims`, with a maintenance comment explaining
why. Their meanings, IDs/quote placeholders, abstention conditions and numeric
budget are identical. No expected answer, cuisine value or real UUID is added
to the instructions. No change to the wire schema, validator, source selection,
privacy, ownership, HITL, default mode, routing, relevance or resource limit.

### Exact structured-output compatibility

The pinned [Ollama OpenAI conversion](https://github.com/ollama/ollama/blob/b0c1ca4f7549d7acdfa52a7dcffc934bc63a43ce/openai/openai.go)
accepts response_format.type=json_schema and extracts the nested
json_schema.schema into native Format. It maps max_tokens to num_predict and
preserves the supplied temperature. The name/strict wrapper fields are not used
by that conversion; strict=true is not a separate guarantee of complete OpenAI
strict semantics. The unchanged application validators remain authoritative.

The pinned [CPU runner adapter](https://github.com/ollama/ollama/blob/b0c1ca4f7549d7acdfa52a7dcffc934bc63a43ce/llm/llama_server.go)
forwards object Format as a separate json_schema decoding constraint on the Go
completion path used in the retained 9E log. This verifies source support for
NOVA's exact nesting, rather than relying on current-version documentation or
HTTP 200 alone. It does not establish that all JSON Schema features are enforced
by the runtime, nor replace a real diagnostic of model behavior. Source inspection
read public text only; no package/model/runtime download or installation occurred.

### Offline reconstruction and context accounting

Expanded the deterministic reconstruction test across both historical questions
and both scripted outcomes. It reconstructs the selected public cuisine record
from subject, predicate and value using the same normalization as MemoryService;
asserts unchanged query, exact ID/full text, model alias, GROUNDED operation,
96-token allowance and nested schema; then validates positive and abstention
outputs against the unchanged citation contract. Subject/predicate/value remain
represented in normalized text rather than newly introduced identity fields.
No clipping or missing evidence field was found. Captured logs are checked not
to contain source text. Test doubles supply outcomes; they do not predict Qwen.

Added a regression that extracts both instruction JSON examples, checks their
keys begin with the unchanged required schema fields, and validates both example
branches after substituting synthetic ID/text. This catches the confirmed order
mismatch without requiring a model. It is not an execution of the installed
runtime grammar or a model-quality test.

A bounded read-only helper read **5,931,697 bytes of existing GGUF header/tokenizer
metadata and zero tensor bytes**. It reconstructed BPE using the already installed
tokenizers library, local vocabulary/merges/special tokens, the pinned Qwen2
pre-tokenization pattern and the two-message ChatML template. No torch/model
loader, Ollama server or inference was invoked. Only numeric summaries were
emitted; no private prompt or evidence was logged. The helper/counts remain
ignored under `.local/phase9/phase9f-offline`.

| Offline controlled reconstruction | Tokens / boundary |
| --- | --- |
| Previous prompt plus ChatML framing | **212**, matches the historical provider count |
| Corrected system instructions alone | **132** |
| Controlled user JSON alone | **69** |
| Corrected prompt including ChatML framing | **214** |
| Corrected prompt plus full output reservation | **310**, below context 512 |
| Controlled exact-quote positive JSON | **61**, before any terminal token |
| Explicit abstention including empty claims | **10**, before any terminal token |

The serialized schema is **569 UTF-8 bytes** with the existing Python JSON
serialization. It is transported separately on this source-verified completion
path, not appended as additional prompt text. Grammar processing consumes runtime
resources but adds no schema text tokens on that path. The 13 framing tokens in
the reconstruction are included in 214. Offline counts matching the historical
212 support this particular reconstruction; they do not certify every Unicode,
chat-template or tokenizer implementation against llama.cpp. The proposed changed
prompt has not been measured at runtime. No context-limit increase is justified.

The existing provider's byte exposure check counts user JSON plus output allowance;
it is explicitly not a complete system/framing/tokenizer context calculation.
No general tokenizer guarantee is inferred from it. For this controlled case,
the offline count and historical runtime record both argue against context/output
exhaustion as the cause. No broad context-accounting redesign was made in this
bounded diagnosis.

### Hypotheses and preserved validation limits

The order mismatch could affect constrained decoding/instruction following, but
its causal effect is **UNRESOLVED**. The schema allows an abstention-only object
and does not encode the entire claims/abstention conditional enforced by Python.
This is intentional acceptance of explicit abstention, not evidence of runtime
malfunction. A preference for the shorter permitted branch, sensitivity to compact
normalized facts, or conservative instruction following remain hypotheses.
No model reasoning, likelihood or relevance calibration was measured.

No contradictory subject mapping was added. Evidence is data usable for supported
claims while its embedded instructions remain untrusted. Exact quote, valid UUID
and successful privacy revalidation still do not prove general relevance or
entailment. The quote-budget instruction and full-set conflict refusal remain.
No schema tightening, forced positive prefix, hardcoded cuisine, fabricated
citation, abstention disablement or relevance cutoff was used to chase a pass.

### Deterministic regression and security evidence

Current-source full PostgreSQL-backed offline suite: **590 passed, one explicit
real-model skip, 60.00 seconds**. Ruff lint/format passed (107 app/test files),
pip check passed. **13 host controller tests passed in 0.047 seconds**. New tests
add three reconstruction variants and one required-order regression over the
prior 586-case passing snapshot. All results are deterministic infrastructure/
contract/security checks, not real semantic or model-quality measurements.

The full suite retains positive/abstention/missing/irrelevant/conflicting/injection
scripted cases, fabricated UUID and altered quote rejection, cross-owner and
deleted-evidence refusal, post-generation revalidation, extra tool/approval field
refusal, invalid JSON fail-closed behavior, managed residency cancellation/expiry
and request identity/ownership policy. No assertions or validators were weakened.
There was no failed inference or test retry. One long test decorator was formatted
before validation; no intermediate test failure occurred in this continuation.

Tests used existing images with read-only current source mounts and empty real
registry settings; external model tests remained disabled. Only the disposable
512 MiB test PostgreSQL, 48 MiB test Redis and bounded backend test process ran.
No application/model/controller/identity/frontend service was started. Test
services were stopped afterward, with no cache/volume deletion. Unchanged
frontend/browser/Go/golden/Kafka suites were not rerun; historical metrics retain
their original scope.

### Resource state, proposal and stop

Initial read-only snapshot: **1229.81 MiB swap**, **8 GiB RAM**, 16,818,240 KiB
free disk; macOS reported 68% free percentage. Final snapshot at 13:13:42 local:
**17,211,387,904 bytes free disk**, **1221.81 MiB swap used**, unchanged **8 GiB
RAM** and Docker allocation **4,106,604,544 bytes / eight CPUs**. macOS then
reported 51% free; it is not guaranteed allocatable model RAM. No allocation,
model ceiling or gate changed. Resource observations do not grant load authority.

All three private BGE/Qwen configurations remain resource_approved=false, mode
0600. Model/controller/application ports have no listener; no resident model or
running application container was found. Offline test services are stopped.
No new model-load attestation or active execution approval was issued.

The new [minimal diagnostic proposal](phase-9f-diagnostic-proposal.md) requests
fresh approval for **one** changed positive RAG cycle: at most one BGE query
embedding, one Qwen generation and zero retries, same controlled task/namespace/
question/96-token alias, with only the example-order correction. It preserves
all safety limits and requires verified sequential unload. It does not authorize
an insufficiency cycle or another automatic attempt. A single outcome would not
prove causality. The proposal is **NOT APPROVED / NOT EXECUTED**.

This continuation changed only the provider instructions/comment, deterministic
diagnostics tests, this additive audit, and the new proposal. Current candidate:
**49 text files, 19 modified / 30 added**; main remains at
`f4c430cbf42a1168c3e167780dc8ade8844d450f`, index empty. All eight checkpoint
commits, historical audits/metrics, retrieval corpus and baseline remain preserved.
No Git remote was configured, no commit/push, model/dependency download, paid/cloud
API, external message, resource increase or Phase 10. External spend $0.
**STOPPED after offline investigation. Phase 9 acceptance remains NOT MET.**

## PHASE 9F — AUTHORIZED ONE-CYCLE REAL-MODEL DIAGNOSTIC

October 17, 2026, approximately 14:28 America/New_York. **Actual classification:
B — VALID ABSTENTION / FAILED POSITIVE ACCEPTANCE.** The operator explicitly
approved one changed positive diagnostic using the abstain-first examples. Exactly
one BGE query embedding and one Qwen generation executed through authenticated
LOCAL_REAL HYBRID RAG. Zero inference retries, additional generations, standalone
probes or insufficiency cycles. The approval is now closed.

The example-order correction did **not** resolve positive acceptance in this run.
It remains a confirmed prompt/grammar ordering mismatch that was corrected; it
is not established as the cause of the previous abstentions. No new instruction,
schema, forced answer, token budget or relevance change followed this result.
The model's reason for abstaining remains unresolved.

### Preflight, identity and unchanged execution boundaries

Verified main/HEAD `f4c430cbf42a1168c3e167780dc8ade8844d450f`, no initial running
containers, model binaries or listeners on application/controller/model ports.
Initial resource gate passed: **17,079,373,824 bytes free disk**, **1181.81 MiB
used swap**. Host RAM remains 8 GiB; Docker allocation remains 4,106,604,544 bytes
and eight logical CPUs. A new private scoped one-hour attestation was created
for this cycle; no earlier model approval or attestation was reused.

Before execution and again afterward, both tensors matched their approved sizes
and SHA-256 values:

- BGE: 133,466,304 bytes, revision
  `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, SHA-256
  `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.
- Qwen: 986,048,512 bytes, SHA-256
  `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.

Both original 32-token and existing 96-token alias manifests and all referenced
blob sizes/digests were verified and unchanged. No alias was created or modified.
The existing private BGE/rag96 configurations were reviewed, explicitly enabled
for the authorized cycle and disabled afterward; the 32-token configuration
remained disabled. Managed residency, pinned bindings and private bearer control
were preserved. Actual runtime logs confirm context 512, one slot, GPU layers
zero and two CPU threads. Temperature remained zero, maximum output 96,
BGE memory ceiling 1024 MiB and Qwen ceiling 2048 MiB. Startup 30 seconds,
inference eight seconds, lease, queue, sandbox and offline limits were unchanged.

Started only existing PostgreSQL, Redis, backend and gateway images with current
source/artifacts mounted read-only; no build or image pull. A short-lived token
was renewed for the existing enabled owner identity/device using the existing
local signing key, without changing grants, roles or identity/device versions.
Authenticated task and ACTIVE cuisine-memory reads succeeded and matched the
controlled public corpus. The backend's actual mounted provider source was
checked for both corrected abstain-first examples before model acquisition.
A bearer-authenticated controller inventory read verified connectivity without
loading a model. Private credentials were not printed or placed in Git.

Before/after read-only SQL snapshots compare identically for all six historical
embedding rows: three learned 384-D vectors in the exact namespace and three
original fixture vectors, including IDs, dimensions, simulation flags, timestamps
and vector digests. The owned real reindex job remains DONE/processed=3 with the
same cursor. No reindex, memory mutation or namespace/vector replacement occurred.

The current corrected source had passed the earlier same-day offline validation:
590 backend tests, one explicit real-model skip, and 13 controller tests. Those
were not rerun or relabeled as new results during this bounded execution. No
production source or validator changed in this continuation.

### Single request and observed outcome

- Query: **Which cuisine does review_fixture prefer?**
- Task: `70b45f12-b509-4443-a66f-81b86caf872c`.
- Namespace: `bge-small-en-v1.5@bd60ce951a6ec4edab8518c1b3301686`.
- Request/trace: `75826944-d95f-48d4-a392-af9a1d0c0055`.
- Run: `db00a968-f133-4aa1-a74e-9181c0dcd959`.
- Retrieval snapshot: `4659e3e8-7f83-4ef5-92d2-7c6f53d5981b`.
- Model-call ledger: `7c6c0339-ebbb-475f-ad0b-6a64a8f5ed42`.

The approved cuisine evidence `4d4b4842-c804-4e72-90c9-7162d6436c37` again
ranked first; all three hits were non-simulation results from the approved BGE
namespace. Its recorded cosine score was 0.821441910094993, identical to 9E.
No similarity threshold was added and no new relevance benchmark is claimed.

The actual order was BGE acquisition → one query embedding/retrieval → verified
BGE process/listener termination → fresh passing resource check → Qwen acquisition
→ one generation → unchanged validation path → verified Qwen termination. The
two recorded residency intervals do not overlap.

Application state was **DONE, output.abstain=true, claims=[], citation_ids=[],
error=null**. This is valid structured abstention, not a supported cuisine claim.
The schema and post-generation validation path completed in **6.061 ms**; the
empty claims did not exercise successful positive evidence-UUID/full-quote
validation. No fabricated citation or unsupported claim was accepted. There was
no validation error to repair and no positive answer to report.

The ledger records one actual invoked phase9-local attempt, cache MISS,
finish_reason=stop, simulation=false, fallback_used=false and replayed=false.
Alias and artifact identity matched the approved Qwen profile. Reported usage:
**214 input / 11 output / 225 total tokens**. Runtime logs independently report
214 prompt tokens, context 512 and truncated=0 at release. The input count
matches the Phase 9F offline reconstruction; the 96-token ceiling was not exhausted.
The raw completion was not retained, so its precise serialization or rationale
is not inferred from token count.

| Outcome class | Actual count / result |
| --- | --- |
| A: supported cuisine claim | **0** |
| B: valid abstention on positive question | **1 — FAIL** |
| C: invalid response | **0** |
| BGE embeddings / Qwen generations | **1 / 1** |
| Retries / insufficiency cycles / external actions | **0 / 0 / 0** |

### Measured timings, memory and resource gates

| Observation | BGE | Qwen rag96 |
| --- | --- | --- |
| Controller readiness | 3.597 s, includes BGE readiness | 0.505 s, server readiness only |
| Forwarded inference HTTP | 35.748 ms | 5253.796 ms, includes lazy weight loading |
| Peak sampled process-tree RSS | 459,456,512 bytes / **438.17 MiB** | 1,504,657,408 bytes / **1434.95 MiB** |
| Declared memory ceiling | 1024 MiB | 2048 MiB |
| Verified shutdown | 31.547 ms | 28.053 ms |

Authenticated RAG HTTP wall time: **11232.761 ms**. Application model-call latency:
**6320.232 ms**, including provider acquisition/inference/release. Validation:
**6.061 ms**. These timings have distinct scopes; the full sequential HTTP request
is not limited to the per-inference eight-second deadline. No TTFT, sustained
throughput, controlled cold-cache load or general quality measurement is claimed.
RSS was sampled approximately every 0.1 seconds and aggregated across runtime
processes; it is not an instantaneous hardware-enforced memory quota.

| Resource boundary | Free disk bytes | Used swap MiB |
| --- | --- | --- |
| Initial preflight | 17,079,373,824 | 1181.81 |
| Before BGE acquisition | 17,081,868,288 | 1181.81 |
| After BGE termination | 17,081,847,808 | 1181.81 |
| Fresh gate before Qwen acquisition | 17,081,843,712 | 1181.81 |
| After Qwen termination | 17,080,348,672 | 1254.50 |
| Final stopped snapshot | 17,079,652,352 | 1246.50 |

All recorded boundaries passed disk >=5 GiB and swap <2048 MiB; sampled RSS stayed
below the unchanged model budgets. No watchdog/resource/security violation was
recorded. Final macOS reported free percentage was 51%, which is not guaranteed
allocatable model RAM. No limit or allocation was raised to achieve execution.

### Cleanup, evidence and remaining acceptance blockers

Both model process trees terminated and their listeners disappeared. The
controller was then stopped through its cleanup path; PostgreSQL, Redis, backend
and gateway were stopped. Final Docker inventory is empty; no application/model/
controller listener or resident Ollama/llama-server binary remains. All three
private real configurations are resource_approved=false, mode 0600. The new
attestation is closed with resource/model approval false and is not future
activation authority. Existing model artifacts, aliases and application volumes
were preserved; no cache/volume deletion or pruning occurred.

Safe projected evidence is ignored under
`.local/phase9/phase9f-authorized-20261017`, including resource snapshots,
before/after integrity/vector summaries, actual result/ledger, residency records
and runtime logs. New private token and closed scoped attestation remain ignored
under `.secrets/phase9b`. Historical evidence was not overwritten. No private raw
prompt, completion or memory text was added to diagnostics/Git.

**Phase 9 acceptance criteria remain NOT MET.** There is still no valid positive
real grounded claim with UUID/exact quote/privacy acceptance, and the separate
insufficiency acceptance remains unexecuted. The corrected prompt still yielded
abstention in this controlled case; no further prompt or model experiment was
performed. General model quality, sustained operation, real LLM judging, vision
and production deployment remain outside this result. Historical metrics and
Phase 8 Kubernetes/NetworkPolicy qualifications are unchanged.

Only this additive audit was changed in the source candidate during execution.
There remain **49 text candidates, 19 modified / 30 added**, empty index, main at
`f4c430cbf42a1168c3e167780dc8ade8844d450f`. All eight checkpoints and historical
reports remain preserved. No model/package download, dependency installation,
cloud/paid API, external message, commit, push, remote configuration or Phase 10.
External service spend $0; host compute/electricity unpriced.
**STOPPED after the single authorized diagnostic. No remaining execution approval.**

## PHASE 9G — OFFLINE STRUCTURED GROUNDED CONTRACT ISOLATION

October 17, 2026 (America/New_York). **Offline validation completed; root cause
UNRESOLVED. No real generation, BGE embedding, model load or repeated RAG request
occurred. No earlier execution approval was reused. Phase 9 remains NOT COMPLETE.**
The authorized 9F positive run remains classification B / failed positive
acceptance: 214 input / 11 output tokens, no truncation, model-call 6320.232 ms,
HTTP 11232.761 ms. This investigation does not relabel that result.

### Confirmed observations versus defects and hypotheses

**No new production implementation defect was confirmed.** The previous example
ordering correction remains in place; its failure to resolve 9F is actual evidence.
No further production instruction, schema, validation, retrieval, routing, identity,
threshold, residency or resource configuration was changed in Phase 9G.

Re-traced the exact generation contract and reconstructed it with synthetic
non-private instrument data, rather than repeating the cuisine acceptance:

1. Memory normalization represents subject/predicate/value as one exact text
   string. LOCAL_REAL selects the first evidence item only after checking the
   full retrieved set for conflicts. The model receives query plus id/text;
   subject/predicate/value are present in the normalized text, not separate fields.
2. The request has exactly system then user roles, no assistant prefix or hidden
   demonstration message. Evidence is serialized in the user JSON data, never
   interpolated into the system instructions. JSON escaping preserves Unicode,
   quotation marks and newlines; controlled round trips found no omission or
   transformation. The subject is not implicitly mapped to the requester.
3. GROUNDED uses the exact GroundedOutput JSON schema in nested
   response_format.json_schema.schema, alias nova-qwen-phase9-rag96,
   max_tokens=96, temperature=0, stream=false. The system gives both corrected
   examples. The full schema is a separate constraint, not additional prompt text
   on the source-verified CPU completion path.
4. The model's claim contains evidence_id and full exact quote. A separate answer
   field is not requested from the model: the application builds its extractive
   answer from validated quotes afterward. This is internally consistent.
5. Parsing validates JSON and the strict Pydantic contract, then token usage and
   finish reason. Length-terminated and unsupported finish reasons fail closed;
   malformed/contradictory positive output is not converted to abstention.
6. Application validation rechecks current owner/task/lifecycle/privacy eligibility
   for the selected evidence, then exact UUID/full-quote membership and conflicts.
   On failure output is cleared. A valid model abstention stays an abstention;
   application DONE is not positive acceptance.

No raw private prompt, completion or memory text was recovered or logged.
Safe retained 9F accounting still shows the correct first cuisine ID, one actual
uncached invocation, stop, no fallback and no truncation. It cannot reveal the
model's internal answerability decision or prove the exact bytes of an unretained
historical completion.

### Wire schema and runtime compatibility risks

Used the already installed, locked jsonschema 4.26.0 validator offline; no package
was installed. The unchanged root schema requires **abstain only**. Claims is an
optional array with maxItems=8 and no positive minimum. Each claim requires a
UUID-formatted evidence_id and quote of length 1–700; both object levels forbid
extra fields. The JSON schema has **no default keyword on claims**. Empty claims
is a Python default_factory result when omitted, not a runtime-injected schema
default. The cross-field relationship is enforced by Python, not encoded in the
wire schema.

| Controlled output | Wire JSON Schema | Unchanged Python contract |
| --- | --- | --- |
| abstain=false with one well-formed claim | accepts | accepts before citation/privacy checks |
| abstain=true with omitted claims | accepts | accepts, normalizes claims to [] |
| abstain=false with omitted or empty claims | accepts | rejects |
| abstain=true with a nonempty claim | accepts | rejects |
| Missing abstain, string boolean or extra authority field | rejects | rejects |

Thus a positive claim is not structurally forbidden, and permitted abstention is
not proof of schema malfunction. A syntactically valid but unauthorized UUID or
altered quote can pass the wire schema and still be rejected by exact application
citation checks. That separation is intentional and preserved. No schema was
strengthened to force a positive branch or weakened to accept an invalid answer.

Reconfirmed the installed Homebrew receipt's Ollama 0.35.1 source commit
`b0c1ca4f7549d7acdfa52a7dcffc934bc63a43ce` and pinned llama.cpp
`6f767fe960c3b97cf37fac4626c86400561ca1e4` against their public source. The
[OpenAI conversion](https://github.com/ollama/ollama/blob/b0c1ca4f7549d7acdfa52a7dcffc934bc63a43ce/openai/openai.go)
reads the exact nested schema and maps the output allowance; name/strict do not
supply additional conditional semantics. This matches prior source inspection
and actual API acceptance, not a newly executed runtime compatibility test.

The pinned [grammar converter](https://github.com/ggml-org/llama.cpp/blob/6f767fe960c3b97cf37fac4626c86400561ca1e4/common/json-schema-to-grammar.cpp)
has handling for references, required/optional objects, UUID format, string length
and array bounds used here. It emits required fields before optional fields and
permits both boolean values. No unsupported feature was identified as a categorical
barrier to a positive output. Its boolean grammar lists true before false; that
source ordering alone does not establish a probability bias or explain greedy
decoding. No actual grammar conversion/generation was run in Phase 9G, and the
offline JSON Schema validator is not a substitute for llama.cpp behavior.

Unresolved hypotheses: the early abstain decision/short valid branch may interact
with constrained decoding; compact normalized facts or conservative wording may
influence answerability; the small model may have difficulty copying UUID/full
quotes while following the complete instruction. These are hypotheses, not
confirmed runtime defects or measurements of model capability. The schema's
conditional gap is a verified contract boundary, not a proven abstention cause.

### Deterministic isolation and security validation

Added **23 cases** to the existing test_inference_diagnostics.py; no production
source changed. Coverage added or retained for the requested isolation axes:

| Axis | Offline evidence |
| --- | --- |
| A: schema-only positive contract | Actual JSON Schema engine accepts a controlled positive claim; comparison with Python exposes cross-field boundaries without injecting defaults |
| B: explicit supported synthetic evidence | MockTransport verifies the exact synthetic source/query, operation, alias, budget and scripted positive result |
| C: irrelevant evidence | Scripted abstention preserved; not a learned relevance measurement |
| D/E: UUID/full quote and rejection | Schema-valid foreign UUID/altered quote still fail exact membership; valid synthetic claim passes; extra claim authority rejected |
| F: injection | Source text stays untrusted user data, escaping round trips, no tools supplied; existing authority-field refusal passes; scripted outcomes do not prove real-model injection resistance |
| G: owner/privacy | Full suite retains authenticated task/foreign-owner refusal and deletion/owner change during generation causing EVIDENCE_CHANGED/output=null |
| H: context/finish handling | Reported token ceilings checked; positive stop remains positive; length/unknown finish fails without becoming abstention; separate tokenizer reconstruction below |

Current-source full PostgreSQL-backed suite: **613 passed, one explicit real-model
skip, 61.76 seconds**. Ruff lint/format passed, 107 app/test files; pip check
passed. **13 host controller tests passed in 0.047 seconds**. No failed test or
inference was retried. Formatting adjusted one new test line before validation;
no assertion, validator or existing case was weakened.

Existing images/current-source read-only mounts were used with empty real registry
settings, external tests disabled and offline flags. Only bounded disposable test
PostgreSQL (512 MiB), Redis (48 MiB) and backend test process ran. No application
or model service started. Test containers are stopped and volumes preserved.
Historical frontend/browser/Go/Kafka/golden and real retrieval scores were neither
rerun nor rewritten. These new results are deterministic contract/security evidence,
not real-model instruction-following, semantic relevance or privacy guarantees.

### Context accounting and proposed isolation experiment

A bounded helper reused the local tokenizer metadata and installed tokenizer
library without importing a model loader or reading tensor data. It read
5,931,697 bytes of GGUF header/tokenizer metadata and zero tensor bytes. Synthetic
subject synthetic_probe_7 / preferred_instrument / cello and a synthetic UUID
were reconstructed, not a production cuisine answer or real memory ID.

| Proposed synthetic case | Offline ChatML input | Input + full 96 output allowance |
| --- | --- | --- |
| Mechanical copy control A | 136 | **232/512** |
| Exact production grounded instruction B | 216 | **312/512** |

The controlled full-quote positive JSON takes 61 tokens before a terminal token.
Counts include ChatML framing. The prior original cuisine request's 214 runtime
input tokens matched its own offline reconstruction; the new synthetic cases
have not been tokenized by the runtime. No CPU-time/deadline promise follows from
these counts. The schema remains separate from prompt text on the inspected path.

The existing provider byte exposure check is not a full system/framing/token
reservation check. New numeric tests verify reported input/output ceilings and
the known 214+96=310 case; they do not turn that exposure check into a general
context guarantee. The actual 9F result has no evidence of token exhaustion or
truncation. No context, output or deadline increase was made or proposed.

The new [Qwen-only isolation proposal](phase-9g-qwen-isolation-proposal.md) requests
fresh approval for at most **two distinct conditional generations**, zero BGE
loads/embeddings, zero RAG API calls and zero retries. A uses an explicit synthetic
copy-control system instruction under the unchanged schema. B runs only after A
passes, with the production grounded system instruction and identical synthetic
user JSON. The sole intended wire difference is the system message. Each uses
the existing 96-token alias and controller, with verified unload and fresh gates
between cases. This is a future operator harness, not an executed or already
runtime-tested integration.

A supported copy followed by B abstention would show the production-prompt
answerability behavior outside retrieval/application state; two successes would
establish only this synthetic contract, leaving original-source/integration
uncertainty. A failure stops B and leaves runtime/schema/model-copy or timing
uncertainty. None proves historical causality or satisfies owner-authorized RAG
acceptance. No direct-provider experiment can replace the application owner/privacy
checks. The proposal is **NOT APPROVED / NOT EXECUTED**; previous approval is closed.

### Resources, Git and stop

Initial snapshot: 8 GiB physical RAM, **1230.50 MiB used swap**, **16,426,364 KiB
free disk**, no running containers. Final snapshot at 15:32:17 local:
**16,778,166,272 bytes free disk**, **1174.50 MiB swap used**, unchanged 8 GiB RAM
and Docker allocation **4,106,604,544 bytes / eight CPUs**. macOS reported 40%
free percentage at closure, not guaranteed model RAM. Resource thresholds were
not changed and no new model-load attestation/approval was issued.

Model/controller/application ports have no listener; private BGE and both Qwen
configurations remain resource_approved=false. No running containers remain after
stopping the offline services. Safe counts, reconstruction helper, validation log,
source-support summary and resource snapshot remain ignored under
`.local/phase9/phase9g-offline`. Existing private credentials were not exported or
modified. No application data, vectors, aliases, caches or volumes were deleted.

This continuation changed only the existing deterministic diagnostics tests,
this additive audit/banner and the new unapproved proposal. Candidate now contains
**50 text files: 19 modified / 31 added**. Main/HEAD remains
`f4c430cbf42a1168c3e167780dc8ade8844d450f`, empty index, no remotes configured;
all eight checkpoints and historical measured reports are preserved. No new model,
model/dependency installation/download, cloud/paid inference, external message,
resource increase, commit/push or Phase 10. Required external spend $0.
**STOPPED after offline investigation. Root cause unresolved; Phase 9 NOT COMPLETE.**

## PHASE 9G — AUTHORIZED QWEN-ONLY CONTRACT ISOLATION EXECUTION

October 17, 2026, approximately 15:43 America/New_York. The operator provided
fresh explicit approval for the exact synthetic two-case proposal, conditional
on A passing before B. **Case A PASSED supported copying; Case B returned VALID
ABSTENTION and FAILED the positive diagnostic.** Exactly two actual Qwen
generations ran, sequentially, with zero BGE loads/embeddings, RAG API calls,
inference retries, additional probes or insufficiency cycles. This diagnostic
is not Phase 9 application acceptance. The scoped approval is closed.

### Harness preparation and controlled comparison

Prepared/reviewed an ignored operator-only client around the existing
LocalProvider, managed residency, decode_local_result and verified_output. A
small subclass replaces only the outgoing system message for case A. Case B
uses the current production GROUNDED system instruction unchanged. Before actual
transport, the harness asserts each body equals its preconstructed expected
body. Both have exactly system then user messages, the same normal JSON user
serialization, unchanged GroundedOutput wire schema, alias, temperature and
96-token allowance. No production source was edited to obtain a passing result.

An offline capture adapter produced scripted synthetic responses solely to
construct/compare bodies and exercise parsing. These captures do not perform
HTTP, acquire a lease or load a model, and are not counted as real inference.
The offline construction check passed before activation. Actual per-case
transport counts were one each. No ModelRoutingService/cache or application
API/service run was used, so no application run ID or database ModelCall row
is invented for this experiment. Request UUIDs below identify provider requests.

A database connection guard raises before any connection attempt; observed
connection attempts were **zero** in offline preparation and both actual cases.
The ephemeral client containers mounted current source, the single Qwen artifact,
the operator harness and scoped private config/key read-only. They did not mount
application database/media/cache volumes, start application services, call
MemoryService or create application records. Owner/privacy integration is not
established by these direct synthetic calls; earlier offline security tests remain
separate evidence.

The sole user data item in both cases was the approved synthetic UUID
`96b55c85-0acf-4d1c-a3ed-4d3422138d79`, subject synthetic_probe_7,
preferred_instrument value cello and its full normalized text. No real memory
UUID, private evidence or production cuisine answer entered the experiment.
The exact copy-control instruction was checked against the approved proposal.
The only generation-body difference was the system message and its consequent
input token count; no assistant prefix, source mutation or schema variant was used.

| Fingerprint (canonical SHA-256) | Value |
| --- | --- |
| Unchanged output schema | c00c8906679d6a5f12183131b756912785502285746903b3ed2dc0a905aa6640 |
| Case A generation body | 38b793e3f6771116da37a33f6a5a78e51749fd15aa947e2d01b013e718e58be1 |
| Case B generation body | fa32eac1d08d2e373602641a6e11bcc21bf7f650ea7017fdf3d40c388325b2da |
| Shared synthetic user data | e9d5bb38df84767be90700c3ef4d51524ef3c1772a0284f437f4bc3a83596e81 |

### Preflight, integrity, authority and runtime restrictions

Initial host check: **1170.88 MiB used swap**, **16,768,122,880 bytes free disk**,
8 GiB RAM, unchanged Docker allocation **4,106,604,544 bytes / eight CPUs**.
No running containers, resident Ollama/llama-server binary or model/controller
listener was present. Each acquisition had a new passing disk/swap observation,
fresh private scoped attestation, tensor/blob verification and alias-parameter
checks. A passing threshold alone was not treated as model-load authorization.

Existing Qwen tensor size **986,048,512 bytes** and SHA-256
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`
were verified repeatedly before each acquisition and after both cases. All
referenced blob sizes/digests and both alias manifests compared unchanged:

- Original 32-token alias manifest:
  `dafd3dc8e500e0774baaf6dc50d5792374815c013e8de4a3a98ac026b1473271`.
- Existing rag96 manifest:
  `af492c94e96e620796e53faeccc48230c42eb81afec1141cfeb7b32af352fa64`.

Only the existing **nova-qwen-phase9-rag96** profile executed, using Ollama
**0.35.1**. Alias parameters and runtime show/log checks retained context 512,
output <=96, CPU threads 2, GPU layers 0, temperature 0 and concurrency one.
Memory remained capped by the existing 2048 MiB sampled watchdog; startup
30 seconds, inference eight seconds, admission, lease and queue limits stayed
unchanged. Runtime logs show both CPU launches with -c 512, -np 1, -ngl 0, -t 2.

A new mode-0600 scoped operator config/key/attestation under
`.secrets/phase9g-isolation` enabled only this provider experiment. Existing BGE
and both application Qwen configurations remained disabled throughout. Private
controller bearer authentication succeeded without a lease/model acquisition.
The existing loopback-only sandbox profile matched its expected contents; an
actual sandboxed external TCP attempt received PermissionError before connecting.
Loopback transport then worked. This checks the scoped OS denial, not a packet
capture or comprehensive network certification. Offline/no-cloud flags stayed in
place. No new package/runtime/model, alias, image build or image pull occurred.

### Actual outcomes and measurements

| Measurement | A — mechanical copy | B — production grounded instruction |
| --- | --- | --- |
| Provider request UUID | 1a7a992c-d7ed-4ab6-b424-12282fa17064 | d05a762d-f693-4819-9439-6bf3f27b81e9 |
| Result | **SUPPORTED COPY / PASS** | **VALID ABSTENTION / FAILED POSITIVE DIAGNOSTIC** |
| Actual model | nova-qwen-phase9-rag96 | nova-qwen-phase9-rag96 |
| Finish reason | stop | stop |
| Input / output / total tokens | **136 / 63 / 199** | **216 / 12 / 228** |
| Direct provider call wall time | **6882.945 ms** | **5827.147 ms** |
| Controller-forwarded inference HTTP | **5724.931 ms** | **5040.862 ms** |
| Client-container wall time | 9461.164 ms | 8624.282 ms |
| Server readiness (not weight load) | 0.596 s | 0.217 s |
| Peak sampled process-tree RSS | **1,523,089,408 bytes / 1452.53 MiB** | **1,433,321,472 bytes / 1366.92 MiB** |
| Verified runtime shutdown | 28.285 ms | 26.143 ms |

Case A returned abstain=false and exactly one claim. Its evidence_id matched the
synthetic UUID and quote matched the full approved text exactly. Unchanged strict
JSON parsing, schema, finish-reason, token and UUID/full-quote checks passed. The
validated quote SHA-256 is
`668ed773554ca31289c4c05f5213239ac4c16cb653c7710acb02cf36b0650fe2`.
This is mechanical copying of a known synthetic instrument fact, not real memory
retrieval, factuality, prompt-injection resistance or application privacy acceptance.

Only after A passed and terminated, B ran with identical synthetic user data,
schema and limits. It returned abstain=true, claims=[]; structured abstention
passed the unchanged parser/validator but did not meet the positive diagnostic.
There was no invalid response to repair, no fabricated citation accepted and no
second attempt at B. Empty claims do not establish successful positive citation
validation. No raw private data was involved or retained.

Runtime logs independently report 136 input tokens for A and 216 for B, context
512 and truncated=0 at release for both. These inputs match the offline counts.
Neither output exhausted 96 tokens. The prior 61-token offline positive estimate
was a particular serialization count, not a promised output length; A's actual
63-token completion is preserved as measured. No exact raw serialization is
inferred from token count or substituted for the observed usage.

Provider timings include acquisition, actual inference and release; forwarded
HTTP includes lazy model loading; container timings also include startup/import/
configuration/construction. There was no authenticated application HTTP benchmark
or database model-call accounting in this experiment. Readiness is server readiness,
not model weight residency. No TTFT, controlled cold-cache load or throughput was
measured. RSS was sampled/aggregated by the existing approximately 0.1-second
watchdog; it is not an instantaneous hardware memory quota.

### Sequential residency and resources

The controller recorded exactly two Qwen-only residency intervals, both stopped.
A terminated at timestamp 1792266191.342078 before B started at
1792266195.5958662. There was no overlapping model instance or BGE acquisition.

| Boundary | Free disk bytes | Used swap MiB |
| --- | --- | --- |
| Initial preflight | 16,768,122,880 | 1170.88 |
| Before A acquisition | 16,767,807,488 | 1170.88 |
| After A termination | 16,763,756,544 | 1170.88 |
| Fresh check before B acquisition | 16,765,607,936 | 1170.88 |
| After B termination | 16,765,521,920 | 1170.88 |
| Final stopped snapshot | 16,765,321,216 | 1170.88 |

All observations passed disk >=5 GiB and swap <2048 MiB; both sampled RSS peaks
were below 2048 MiB and each actual inference completed within eight seconds.
No resource/security/authentication/shutdown violation was recorded. Final macOS
reported free percentage was 49%, not guaranteed allocatable model RAM. No gate,
resource allocation or deadline was changed.

### What this isolates, and what remains unresolved

**Verified new capability evidence:** this installed model/runtime/schema path
can produce a positive supported UUID/full-quote object within the existing limits.
A categorical inability to represent/copy that structure under this schema is
therefore not an explanation sufficient for every abstention. The same synthetic
evidence with production instructions returned abstention outside retrieval,
application authentication, database state and cache. Those components are not
necessary for the abstention observed in case B.

**Still unresolved:** which part of the production instruction, answerability
judgment, prompt length/content or model/grammar interaction induces abstention.
This was one ordered, unrepeated pair, not a randomized causal or quality study.
It does not prove the internal reason for historical cuisine failures, exclude
all source-specific/application issues there, or establish general reliability.
Copy instructions explicitly request copying; they do not measure answerability.
No further instruction/schema/required-field/ordering change or experiment was
performed after B failed. The existing application validators remain unchanged.

**Phase 9 remains NOT COMPLETE.** The synthetic A pass does not supply the missing
owner-authorized positive cuisine RAG acceptance. The separate insufficiency
acceptance remains unexecuted. Real LLM judging, vision and general production/
model-quality qualification remain outside this result; historical retrieval,
fixture and Phase 8 Kubernetes/NetworkPolicy qualifications are unchanged.

### Final cleanup, preservation and Git

Both Qwen process trees were released/terminated and listeners disappeared after
each case. The task-owned controller and ephemeral clients are stopped; Docker
reports zero running containers. Model/controller/application ports have no
listener and no resident Ollama/llama-server binary remains. The scoped private
config is resource_approved=false; its attestation is closed with resource/model
approval false. All existing application BGE/Qwen private configs remain false.
No remaining execution authorization is implied by this experiment.

No database connection, MemoryService/RAG call or application volume mount occurred;
existing vectors/namespaces and application data were not touched. Tensor/blob
content and both alias manifests verified unchanged. No cache or volume was deleted.
Production provider, contracts, service and residency-controller source digests
compared identical before/after. Only this additive audit/banner changed in the
source candidate during execution.

Safe client/controller logs, the reviewed operator harness, construction/request/
schema fingerprints, integrity records, residency and result summaries remain
ignored under `.local/phase9/phase9g-authorized-20261017`; mode-0600 scoped private
configuration/key/closed attestation remain ignored under `.secrets/phase9g-isolation`.
Historical evidence was not overwritten. The earlier 613-backend/13-controller
passes retain their original offline scope and were not rerun as new passes.
Harness syntax and offline construction checks passed before activation; no
production code change required another broad regression suite.

Candidate remains **50 text files, 19 modified / 31 added**, index empty, main at
`f4c430cbf42a1168c3e167780dc8ade8844d450f`. All eight checkpoints and historical
reports preserved; no commit, push or remote configuration. No new model,
dependency installation, cloud/paid inference, external message, resource increase
or Phase 10. Required external service spend $0; host compute/electricity unpriced.
**STOPPED after the authorized conditional two-case diagnostic. Phase 9 NOT COMPLETE.**

## PHASE 9H — OFFLINE PRODUCTION PROMPT DIFFERENCE ISOLATION

October 18, 2026 (America/New_York). Continued under the master Phase 9 mission,
which explicitly requires a stop before new model execution. **Phase 9H offline
success criteria met; Phase 9I awaits fresh explicit approval. Phase 9 remains
NOT COMPLETE.** Zero model loads, Qwen generations, BGE embeddings or RAG API
calls occurred. The previous Phase 9G authorization was not reused.

### Exact comparison, findings and evidence boundaries

Read the actual Phase 9G execution audit, retained safe results/operator client,
current provider instructions/schema and output-validation path. Historical A
remains supported mechanical copy: 136 input / 63 output tokens, 6882.945 ms,
1452.53 MiB sampled RSS. Historical B remains valid abstention / failed positive
diagnostic: 216 / 12 tokens, 5827.147 ms, 1366.92 MiB. Both ended with stop,
without truncation. No historical failure, score, threshold or quality claim changed.

The new [instruction comparison](phase-9h-prompt-analysis.md) documents every
clause difference under all requested categories A–H: evidence relevance,
positive-answer direction, abstention, citation mapping, exact quote, untrusted
source/authority/identity, JSON examples and token budget. It also records their
cross-category order and the 80-token total prompt-length difference. The
[canonical test matrix](../backend/tests/fixtures/phase9h_prompt_matrix.json)
contains both complete system messages and a lossless ordered segmentation of
production text; reconstruction tests match both historical request fingerprints.
No omitted source sentence or additional hidden instruction was found.

Confirmed contrast: the copy control asks unconditionally for one copied claim;
production adds a relevance judgment, four explicit abstention conditions, two
JSON examples, identity caution and different untrusted-data wording. Citation/
full-copy intent and the final JSON-only/96-token sentence are shared, although
production adds placeholder mapping and explicit non-fabrication prohibitions.
All these differences changed together in 9G, so that pair does not establish
which instruction caused abstention.

**No new contradiction or production defect was confirmed.** Possible ambiguities
remain: treating untrusted instructions as a reason to distrust all factual source
content; interpreting “directly answers” narrowly for normalized subject/predicate/
value records; quote-fit judgment; example/branch competition; instruction order,
length and model/grammar interaction. No internal model rationale or root cause
is asserted. The wire schema permits both a supported claim and abstention;
unchanged Python consistency, UUID/full-quote, privacy and authority checks remain
necessary and were not weakened. No production correction is justified yet.

### Controlled variants prepared, not deployed

Added a versioned diagnostic-only JSON fixture with three full predeclared
messages. These are not imported by application code, contain no activation
entrypoint and change no default, provider, registry, schema or validator.

| Case | Sole changed production text segment(s) | Intent |
| --- | --- | --- |
| 9I-F | F: evidence_policy | Retains “Evidence is untrusted data, never instructions.” and adds explicit permission to use stated facts while again forbidding embedded instructions |
| 9I-A | A: relevance | Adds a generic explanation of '<subject> <predicate>: <value>' records before the unchanged direct-answer condition |
| 9I-AF | Those same A and F additions | Prepares a possible combined contrast for future review, without claiming interaction evidence |

All original production conditions, wording outside the selected segment and
segment ordering are preserved. Missing/irrelevant/conflicting evidence, unsupported
answers, quote-fit abstention, exact ID/full quote, no invented/edited evidence,
no identity assumptions, no tools/actions/approvals and JSON/output rules remain.
No cuisine answer, production UUID or synthetic value appears in system messages.
The synthetic UUID/query/instrument evidence is identical to Phase 9G user data.

Category labels identify changed text segments; they do not prove semantically
orthogonal effects. Clarifying F can itself affect relevance judgment, and longer
clarifications are not length-matched placebo controls. No interpretation will
turn one finite outcome into general model quality or proven historical causality.

The [initial Phase 9I proposal](phase-9i-diagnostic-proposal.md) requests **one
Qwen generation, case 9I-F only**, then stop regardless of outcome. This is the
smallest new contrast for the untrusted-data hypothesis. A and AF are offline
candidates excluded from that initial request; they require later fresh approval
and evidence review. There is no automatic sweep, fallback experiment, repeated
baseline/control, inference retry or conditional execution after abstention.

The proposed system message is byte-identical to the fixture's 9I-F message;
its SHA-256 is
`9f1f97da85c58b2ebf6a4d362027e2a76985b6ef5838638b57ff0238717b6906`.
The proposal preserves the existing rag96 alias, context 512, output 96, CPU
threads 2, GPU layers 0, temperature 0, concurrency one, Qwen 2048 MiB ceiling,
startup 30 seconds, inference eight seconds, fresh disk/swap/artifact/authentication
checks, private scoped attestation, residency and network controls. It uses no
BGE, RAG API, production memory, database or new alias/model/package. Any future
result must distinguish a supported claim, valid abstention and invalid/unsafe
response; no repair or extra generation is included.

### Deterministic validation and context fit

Ten new parameterized cases in the existing diagnostics test module establish:

- Exact segment replacements and declared category membership, with all other
  text unchanged and original protective clauses retained.
- Current production text matching the frozen baseline, plus historical A/B
  generation-body fingerprint reproduction without inference.
- Only the system message differing in candidate bodies; identical roles, user
  data, alias, schema, temperature, stream and output budget.
- Scripted positive and abstention responses using unchanged strict decoding and
  exact citation/full-quote validation; these do not predict learned behavior.
- Initial proposal scope restricted to one case, one generation, no BGE/RAG/retry,
  with every fixture case explicitly NOT APPROVED / NOT EXECUTED.

Full current-source PostgreSQL-backed offline suite: **623 passed, one explicit
real-model skip, 60.57 seconds**. Ruff lint/format and pip compatibility passed,
107 app/test files. **13 host controller tests passed in 0.053 seconds**. Initial
formatting adjusted new test layout before validation; no failing test or inference
was retried and no assertion/expected output was weakened. All prior owner/privacy,
expiry/lifecycle, conflict, citation, action-field, idempotency and failure checks
in the full suite remain passing deterministic evidence, not new real-model
security or quality claims.

Only bounded disposable test PostgreSQL/Redis and backend test processes ran,
using existing images, current-source read-only mounts, offline flags and empty
real-registry settings. Resource-heavy suites were not overlapped. No image build,
pull or dependency installation occurred. No application/model/controller service
started. Test services were stopped afterward with no volume/cache deletion.

A bounded tokenizer-only reconstruction read 5,931,697 bytes of existing GGUF
header/tokenizer metadata, zero tensor bytes, with the installed tokenizer library
and no model-loader import. Numeric results, including ChatML framing:

| Message | Offline input tokens | Input + full 96 output reserve |
| --- | --- | --- |
| Historical control | 136 | 232/512 |
| Current production baseline | 216 | 312/512 |
| 9I-F | 236 | 332/512 |
| 9I-A | 249 | 345/512 |
| 9I-AF | 269 | 365/512 |

Only the historical control/baseline counts have corresponding earlier runtime
measurements; new variant counts are offline estimates, not executions or a
promise of completing within eight seconds. No context/token/deadline ceiling
was raised. Safe helper/counts/test logs remain ignored under
`.local/phase9/phase9h-offline`. No private raw prompt/evidence was logged.

### State, resources and required stop

| State | Phase 9H actual boundary |
| --- | --- |
| IMPLEMENTED | Diagnostic test fixture, construction tests, comparison and exact proposal |
| CONFIGURED | Application defaults/registries unchanged; all private real configs remain disabled |
| EXECUTED | Offline backend/controller checks and bounded tokenizer metadata reconstruction only |
| MEASURED | Test durations, offline token counts and host resource snapshots |
| EVALUATED | Deterministic construction/security contracts; no new learned-model evaluation |
| FAILED | Historical positive failures and 9G production abstention remain failures |
| BLOCKED | Phase 9I execution awaits fresh explicit approval |
| UNVERIFIED | Variant effects, exact abstention cause and final positive/insufficiency acceptance |

Initial host snapshot: **1050.88 MiB used swap**, **15,626,956 KiB free disk**,
8 GiB RAM, zero running containers. Final snapshot October 18 at 23:38:12 local:
**15,994,265,600 bytes free disk**, **1050.88 MiB used swap**, unchanged 8 GiB RAM
and Docker allocation **4,106,604,544 bytes / eight CPUs**. macOS reported 42%
free percentage, not guaranteed allocatable model RAM. These snapshots do not
constitute a future load attestation. No model-load approval/configuration was
enabled or resource ceiling/allocation changed.

Model/controller/application ports have no listener; no running containers remain.
BGE and both application Qwen configs, plus the previous isolated Qwen config,
remain resource_approved=false. Production provider/contracts/service/controller
source digests match the closed Phase 9G snapshot exactly. No application data,
real/fixture vector, namespace, alias, artifact, cache or volume was modified or
removed. Historical metrics and Phase 8 deployment qualifications are preserved.

Current candidate: **53 text files, 19 modified / 34 added**. This continuation
changed the existing deterministic tests and additive audit, and added the test
matrix, analysis and initial proposal. Main/HEAD remains
`f4c430cbf42a1168c3e167780dc8ade8844d450f`, index empty, eight checkpoints
preserved; Git whitespace checks pass. No git add/commit/push or remote change.
No new model/download/dependency, paid/cloud API, external message or Phase 10.
Required external spend $0; host compute/electricity unpriced.

Phase 9J production correction is not started: it requires justified Phase 9I
results. Phase 9K real acceptance is not authorized. Final 9L regression/security
and 9M checkpoint preparation are not represented as completed; the master mission
requires stopping here before those dependent stages. The current full offline
suite is Phase 9H evidence, not a premature final 9L certification.
**STOPPED at the explicit Phase 9H authorization boundary. Phase 9 NOT COMPLETE.**

## PHASE 9I-F — EXPLICITLY AUTHORIZED SINGLE-GENERATION EXECUTION

October 19, 2026, approximately 01:18 America/New_York. **Result: VALID ABSTENTION
/ FAILED POSITIVE DIAGNOSTIC; proposed F clarification remains INCONCLUSIVE.**
The operator explicitly approved only the frozen 9I-F case. Exactly one actual
Qwen generation ran. No retry, 9I-A/9I-AF, BGE load/embedding, RAG API request,
database connection/write, additional model probe or follow-up experiment occurred.
The scoped approval is consumed and closed. Phase 9 remains NOT COMPLETE.

### Authorization, drift checks and harness

Read the new execution authorization and compared it with the reviewed proposal
and immutable test fixture. The exact approved system message adds only the
F-category clarification allowing stated facts to be used as evidence while
again forbidding embedded instructions. Wording, ordering, synthetic user JSON,
schema, settings and validators were not changed to seek a passing result.

Adapted the existing ignored operator LocalProvider harness to expose only
`offline` construction and one executable case, 9I-F. Its actual call replaces
only the outgoing system message and asserts the complete body equals the
prepared expected body. It rejects a different case, a second transport call,
changed schema/user data/baseline or changed prepared request fingerprint.
The stored system and baseline fingerprints were checked against the reviewed
values and the historical production-body fingerprint. The proposal's code block
was byte-identical to the frozen 9I-F system message; no proposal regeneration.

| Verified input fingerprint (SHA-256) | Value |
| --- | --- |
| Approved 9I-F system message | 9f1f97da85c58b2ebf6a4d362027e2a76985b6ef5838638b57ff0238717b6906 |
| Exact 9I-F generation body | cea26e16ddb753bde5ffc231649db8172b37709252fa0d4bb28581382ce36820 |
| Reconstructed unchanged production body | fa32eac1d08d2e373602641a6e11bcc21bf7f650ea7017fdf3d40c388325b2da |
| Unchanged GroundedOutput schema | c00c8906679d6a5f12183131b756912785502285746903b3ed2dc0a905aa6640 |
| Shared synthetic user data | e9d5bb38df84767be90700c3ef4d51524ef3c1772a0284f437f4bc3a83596e81 |
| Canonical 9I-F case definition | 5ba0a65423cf09e771bf21c66f531c99dacba3938785d521a08df4374c8cc4f7 |

Offline harness construction passed before activation, using a scripted capture
with no HTTP or model lease. This is not another real generation or inference
warmup. Syntax checks passed. The unchanged provider performed strict decoding;
verified_output used only the approved synthetic item as the exact-citation set.
No application/database run or ModelCall ledger row was created. The UUID below
identifies a direct provider request, not an application acceptance run.

A database connection guard observed zero connection attempts. The ephemeral
client mounted only current app source, the diagnostic client/matrix, scoped
private settings and the existing Qwen artifact read-only, without application
database/media/cache volumes. It did not call MemoryService or the RAG API.
Direct synthetic validation is not authenticated application ownership or
post-generation memory-privacy acceptance. Historical offline security evidence
retains its separate scope.

### Fresh safety and integrity checks

Initial observations: **15,012,167,680 bytes free disk**, **1050.88 MiB used swap**,
8 GiB host RAM; Docker allocation unchanged at **4,106,604,544 bytes / eight CPUs**.
No running container, resident Ollama/llama-server binary or model/controller
listener was found before startup. Fresh host checks were repeated immediately
before the sole acquisition, with a new scoped private one-hour attestation.

Qwen tensor size **986,048,512 bytes** and approved SHA-256
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`
passed before execution and afterward. Referenced alias blob sizes/digests and
bounded parameters were verified; both legacy/rag96 manifest digests compared
unchanged. No new alias, weight or runtime was created or downloaded.

The scoped private provider used **nova-qwen-phase9-rag96**, existing Ollama
**0.35.1**, context 512, output <=96, CPU threads 2, GPU layers 0, temperature 0
and concurrency one. Runtime show/log checks retained those bounds. Qwen's
sampled RSS ceiling stayed 2048 MiB, startup 30 seconds and inference eight
seconds. Existing controller lease, zero queue, admission and watchdog protections
remained in place. No production provider or runtime parameter changed.

Private controller bearer authentication passed via read-only inventory, which
does not acquire/load a model. The loopback-only sandbox profile matched its
expected contents and rejected an actual external TCP attempt with PermissionError
before connecting. Offline/no-cloud flags remained set. This is a scoped OS denial
check, not a full network capture/certification. Existing private BGE/Qwen configs
stayed disabled; only the fresh scoped isolation config was temporarily enabled.

### Actual response, validation and timing

- Case: **9I-F only**.
- Provider request UUID: `17db3ac5-a610-4e4f-92d8-3b899896bc4c`.
- Actual model: **nova-qwen-phase9-rag96**.
- Finish reason: **stop**.
- Classification: **VALID ABSTENTION**, failed positive diagnostic.
- Validated result: **abstain=true, claims=[]**.
- Real generations / retries / other matrix cases: **1 / 0 / 0**.

Strict structured JSON and claim/abstention consistency validation passed. No
claim or citation was returned, so successful positive UUID/full-quote validation
was not exercised; the positive criterion was not met. No invalid response,
fabricated citation, repair or substituted output was accepted. The safe summaries
do not retain or infer a precise raw serialization from token count.

| Actual measurement | Value / scope |
| --- | --- |
| Provider-reported input / output / total tokens | **236 / 11 / 247** |
| Direct provider call wall time | **6655.646 ms**, acquisition/inference/release scope |
| Controller-forwarded inference HTTP | **5467.775 ms**, includes lazy model load |
| Client-container wall time | **9428.220 ms**, includes imports/configuration/construction |
| Controller server readiness | **0.622 seconds**, not weight-load readiness |
| Peak sampled process-tree RSS | **1,356,447,744 bytes / 1293.61 MiB** |
| Verified runtime shutdown | **29.221 ms** |

Runtime logs confirm context 512, one slot, CPU-only two-thread launch,
236 prompt tokens and truncated=0 at release. The input count matches the offline
9I-F reconstruction; the 96-token output allowance was not exhausted. No timeout,
resource watchdog violation or safe validation error was observed. These are
direct provider/runtime measurements, not application HTTP, TTFT, throughput,
controlled cold-cache or general quality benchmarks. RSS is sampled/aggregated,
not an instantaneous hardware memory quota.

| Resource boundary | Free disk bytes | Used swap MiB |
| --- | --- | --- |
| Initial preflight | 15,012,167,680 | 1050.88 |
| Fresh check before Qwen acquisition | 15,011,610,624 | 1050.88 |
| After verified Qwen termination | 15,009,701,888 | 1285.06 |
| Final stopped snapshot | 15,009,464,320 | 1285.06 |

All recorded gates passed disk >=5 GiB and swap <2048 MiB; sampled RSS stayed
below 2048 MiB and actual inference finished within eight seconds. Final macOS
reported 47% free percentage, not guaranteed allocatable model RAM. No host/Docker
allocation, token/context/deadline or memory limit was increased.

### Interpretation, cleanup and remaining boundary

The F clarification alone did **not** resolve this synthetic positive case under
the approved settings. The result is INCONCLUSIVE for the proposed clarification,
not evidence supporting a production correction or a claim that untrusted-data
wording can never matter. Phase 9G's supported copy remains valid historical
evidence that this runtime/schema can produce the required positive structure.

Still unresolved: normalized-record relevance interpretation, combinations of
A/F instructions, explicit abstention/quote-fit conditions, example competition,
instruction ordering/length and model/grammar interaction. This single negative
observation cannot establish the historical cause or general model quality.
9I-A and 9I-AF were not executed and have no new approval. No Phase 9J production
change was justified or made. No additional experiment was added after the result.

Qwen was released and its runtime process/descendant termination and listener
checks passed. The controller and ephemeral client are stopped. Docker reports
zero running containers; model/controller/application ports have no listener.
The scoped isolation config is resource_approved=false; its mode-0600 attestation
is closed with operator/model approval false. Original BGE, both application Qwen
configs and the older Qwen isolation config remain disabled. No remaining model
execution authority is implied.

Tensor/blob content and both alias manifests remain verified unchanged. Production
provider/contracts/service/controller source, the reviewed matrix and proposal
compare identical before/after. No database connections or application volume
mounts occurred; application data, vectors and namespaces were not touched.
No model, cache, alias or volume was deleted.

Safe evidence, fingerprints, integrity/resource/result summaries, operator client
and controller logs remain ignored under
`.local/phase9/phase9i-f-authorized-20261019`; scoped mode-0600 private settings,
key and closed attestation remain ignored under `.secrets/phase9i-f-isolation`.
No historical evidence was overwritten. The prior Phase 9H 623-backend/13-controller
passes were not rerun or counted as new results. New harness syntax/offline
construction checks passed; production behavior was unchanged, so no broad suite
was repeated for this one authorized diagnostic.

Only this additive audit/banner changed in the source candidate. Git remains
**53 text candidates, 19 modified / 34 added**, empty index, main at
`f4c430cbf42a1168c3e167780dc8ade8844d450f`. All Phase 1–8 checkpoints,
prior audit results and thresholds remain preserved. No git add/commit/push,
remote change, model/dependency download/install, cloud/paid inference, external
message, resource increase or Phase 10. External service spend $0.

**Phase 9 status: NOT COMPLETE.** A real owner-authorized supported cuisine RAG
answer and separate insufficiency acceptance remain missing. Next required action
is review of this inconclusive result and fresh explicit authorization before
any further isolation; no automatic transition to A/AF, production correction,
acceptance, final regression or checkpoint work occurs under this single-case
approval. **STOPPED after 9I-F as instructed.**


## OCTOBER 19 — OFFLINE GROUNDED PIPELINE CORRECTION

October 19, 2026, approximately 02:40–02:53 America/New_York. **Offline code
corrections and deterministic regression PASS. Real-model acceptance NOT EXECUTED.
Phase 9 remains NOT COMPLETE.** The current mission authorized justified offline
work only. Earlier 9G/9I-F approvals remain closed; no model/runtime activation,
new attestation, generation, BGE embedding or real RAG request occurred here.
Historical measurements, thresholds and failed positive results remain unchanged.

### Confirmed defects and unresolved cause

The current implementations/callers, contracts, routing/cache/diagnostics, memory
eligibility/mutations, visual persistence, grounding/security tests, controller,
immutable 9H matrix and 9I proposal were reviewed before implementation. Main was
at `f4c430cbf42a1168c3e167780dc8ade8844d450f`, index empty, with 53 existing text
candidates preserved. The [implementation plan](phase-9-grounding-correction-plan.md)
separates demonstrated defects, limitations and deferred hypotheses.

Confirmed corrections:

- `decode_local_result` caught ProviderFailure from shared validation and converted
  it to USAGE_INVALID. ProviderFailure now propagates unchanged, and shared result
  validation runs outside the usage parsing catch. Unexpected programmer exceptions
  from that validation are no longer mislabeled as usage. Non-dictionary usage and
  unsupported finish reasons fail closed. Existing JSON/schema/identity/tool/limit
  classifications and diagnostic sanitization remain intact.
- Final memory checks previously compared eligibility IDs only. They now compare
  the original normalized text, subject/predicate/value and a source binding covering
  owner/task/scope/privacy/status/validity/update/source metadata. Production gather
  always captures that binding. This rejects same-ID content edits and revocations.
- Visual gathering previously omitted run privacy/status and processor status;
  final privacy revalidation ignored visual evidence entirely. Both now require
  owned same-task media, eligible run privacy, DONE/PARTIAL run, matching DONE
  processor and unchanged observation/media/run/processor binding. Full description
  text is retained; no quote is silently sliced. Privileged database mutation or
  forged perception facts are not certified trustworthy by these checks.
- Privacy validation previously committed separately before marking the run DONE.
  Current retrieved/sent source checks, fresh relevant-conflict detection, citation
  validation and terminal DONE write share the owner-locked transaction. Relevant
  source rows are locked too. An actual second PostgreSQL connection was refused
  NOWAIT access to that owner immediately before terminal commit, then succeeded
  after commit. This covers cooperating application mutations and existing-row
  writes; it is not a guarantee against arbitrary privileged database writers,
  future clock expiry or mutations after acceptance commits.
- Differing source texts under the same citation UUID cannot be substituted for a
  positive claim. An explicit abstention still remains valid for conflicting data.

**None establishes the cause of Qwen's historical valid abstention.** Historical
9G-A copying passed while 9G-B and 9I-F abstained. The error masking defect does
not explain a valid abstention. Small-model instruction following, production
answerability instructions and contract complexity remain hypotheses. No new
model result, reliability improvement or semantic quality measurement is claimed.

### Bounded selection and independently checked support

LOCAL_REAL no longer takes an arbitrary first retrieved item. A small deterministic
support contract recognizes explicitly named subject cuisine/beverage preference
questions and their conjunction, matching structured subject/predicate/value and
normalized text. No production subject, answer or UUID is hardcoded. No ranking
score or lexical-overlap threshold establishes support. Existing memory policy
unsafe-content markers remain a narrow refusal rule, not an injection detector
with a completeness claim.

Selection scans bounded retrieved evidence in its existing order, retains the
original UUID/full text and server-side retrieval provenance, skips unrelated or
oversized records, deduplicates IDs and supplies only records that fit. It does
not fill context with irrelevant hits or truncate an exact quote. Multiple small
records can fit: the deterministic two-preference test fits with an 80-token
output reservation, within the unchanged 96 ceiling. The approved positive case
fits with its full 96-token reservation. This is capacity evidence, not a promise
that the model can emit every supplied quote within that output budget.

The full retrieved set remains available for original conflict checks and final
source revalidation, even when a record was not sent. Conflicting full sets still
supply empty model evidence and require abstention. Newly visible active conflicts
for those subject/predicate keys are checked at final acceptance too. Unknown,
first-person and visual questions are outside the declared support subset and
receive no asserted supporting context. This intentional narrowing is explicit;
it is not general-purpose semantic RAG or a new identity assumption.

For LOCAL_REAL, final positive claims must independently match this structured
question/source contract as well as the exact authorized UUID/quote. A model may
still abstain on any recognized question. FIXTURE keeps its existing replay
behavior; direct synthetic provider construction tests remain component tests,
not application support/privacy acceptance. Frozen historical wire reconstructions
are now explicitly separate from current application selection tests.

Four boundaries remain distinct: retrieval relevance is ranking; eligibility is
owner/scope/privacy/lifecycle permission; sufficiency is the declared bounded
question/source contract; general semantic entailment is **not established**.
The unchanged GroundedOutput contains quotes and UUIDs, not a separate freeform
answer. The API's answer is still joined extractive quotes. No schema migration,
answer fabrication, forced claim, disabled abstention or general factuality claim
was introduced. Completeness, truth of stored facts and arbitrary paraphrase
understanding remain outside this validator.

### Context budget and unchanged generation behavior

The production system-message text was extracted into a shared helper without
changing its bytes; schema, defaults, required fields and wire format are unchanged.
Immutable matrix/wire tests continue to pass. No speculative prompt rewrite was
made after the failed F-clarification experiment.

Grounded generation now requires the private opt-in budget declaration
`grounded_budget_profile=QWEN2_CHATML_0351`, the pinned Qwen tensor fingerprint,
context 512, output 16–96 and the reviewed prompt fingerprint. Unknown/missing
profiles, artifact/prompt drift or overflow refuse before transport/acquisition.
This adds a configuration prerequisite to older real registries; no existing
private registry was enabled or rewritten in this offline task. The field is
excluded from public model metadata.

For that pinned byte-level Qwen2/ChatML path, the conservative bound reserves
136 system tokens (historically 132 at 96), 32 framing tokens (historically 13),
16 additional margin, one token per serialized user UTF-8 byte including JSON,
and the full requested output allowance. Existing source review established that
Ollama 0.35.1 supplies this schema as grammar rather than appended prompt text;
that zero schema prompt contribution is not transferable to arbitrary runtimes.
The operator must verify the runtime/template before declaring the profile.
A complete public positive context bounds to 455/512 with output 96. The test
with two tiny preference records bounds to 497/512 with output 80. These are
conservative offline bounds, not runtime token counts, measured inference fit,
throughput or evidence that positive output will succeed. Non-grounded operations
retain their existing exposure checks; this profile claims grounded coverage only.

### Executed validation and disclosed intermediate failure

| Check | Result and scope |
| --- | --- |
| Focused inference/provider/diagnostic/source tests, initial snapshot | 166 passed, one real-model skip, 6.20 s |
| Expanded source-safety tests before final ambiguity addition | 47 passed, 2.40 s |
| Full backend, pre-ambiguity snapshot | 670 passed, one skip, 64.23 s |
| Final corrected full PostgreSQL backend suite | **671 passed, one explicit real-model skip, 65.91 s** |
| Backend Ruff lint / format check | PASS; 109 app/test Python files formatted |
| Existing environment pip check | PASS; no broken requirements, no installation |
| Host residency/controller tests | **13 passed**, 0.050 s, no models |
| Test-database Alembic upgrade/head and drift check | PASS through mandatory suite setup, isolated `_test` database |
| Current-source Python/JSON candidate syntax and Git whitespace | PASS |
| Backend static type checker | NOT EXECUTED; none configured in backend pyproject |
| New real embeddings/generation/RAG/quality | NOT EXECUTED; no activation authorized |
| Final Go/frontend/browser/golden/Kafka qualification | NOT EXECUTED; deferred until separately approved real acceptance passes |

After the initial full pass, citation review added ambiguous-ID refusal. The next
full run had **670 passed, one failed, one skipped, 66.32 s**: that refusal was too
broad and rejected a legitimate explicit abstention over conflicting evidence.
It was corrected to reject ambiguous citations only when claims are asserted.
The original conflicting-abstention test/assertion was preserved. The final full
suite above then passed. This intermediate failure is not counted as a pass.
Initial import/line-length formatting findings were also corrected before final
lint/format success. No assertion weakening or test retry mechanism was introduced.

Security coverage includes actual authenticated/foreign-owner policy regressions,
invalid JSON/schema/extra tool/approval fields, fabricated IDs and altered quotes,
malformed usage and sanitized failure persistence, wrong subject/predicate support,
unsafe instruction data, missing/oversized/mixed evidence, owner/privacy/scope/time/
content changes during scripted generation, stale evidence omitted from model
context, visual privacy/status/owner/content/hash changes, newly inserted conflicts,
atomic rollback/reindex recovery and final-commit lock behavior. Deterministic
responses do not measure real model injection resistance or learned answerability.
No external action path or approval authority was added.

Suites used the existing local backend-test image and current read-only source,
dedicated `_test` PostgreSQL and test Redis, offline model flags and empty real
registry settings. Test DB and runner remained bounded to 512 MiB each, DB one CPU,
runner two CPUs; Redis 48 MiB. Heavy suites ran sequentially. No image build/pull,
model/framework load or new dependency was needed. Application data and real
vectors/namespaces were never connected to or modified by these tests.

### Resources, proposal and stop state

Initial read-only snapshot recorded swap 1109.06 MiB, 8 GiB RAM and approximately
14,552,836 KiB free disk. Before focused/full validation, swap measured 898.19 MiB;
Docker allocation remained 4,106,604,544 bytes / eight logical CPUs. No resource
threshold was changed or host/Docker restart, cache pruning or volume deletion used.

Final stopped snapshot, **02:52:55 America/New_York**: free disk
**16,109,039,616 bytes**, used swap **1005.75 MiB**, RAM **8,589,934,592 bytes**,
unchanged Docker allocation. Disk/swap pass the numerical model thresholds, but
this snapshot is **not future model activation authority or allocatable-RAM proof**.
No inference RSS/latency/token measurement exists for this task because no model ran.

Offline test containers were stopped without deleting volumes. Docker reports no
running containers; ports 11434/11435/11436 have no listener and the bounded process
inventory found no Ollama/llama-server/bridge/controller process. The inspected
BGE/Qwen/rag96 and 9I-F private registry flags remain resource_approved=false.
No private config or passing resource attestation was exported to a service.
Safe validation logs and final resource snapshot remain ignored under
`.local/phase9/grounding-correction-offline`; no private prompt logging was added.

The [new acceptance proposal](phase-9-grounding-acceptance-proposal.md) requests
one owner-authenticated named-subject positive cycle, then one spacecraft-code
insufficiency cycle only if positive passes. Same existing task/namespace/models,
96-token alias, CPU/context/memory/deadline ceilings and sequential residency;
at most two BGE embeddings/two generations/two cycles, zero retries. **Not approved
or executed.** The positive wire content may equal the historical failed request:
this proposal does not pretend the over-abstention cause was fixed. Insufficiency
would test explicit model abstention on empty selected evidence under the declared
subset, not general relevance calibration. Stop for fresh explicit approval.

Current continuation changed inference grounding/providers/registry/service,
three inference test files, README/architecture notes, the implementation plan,
new acceptance proposal, this additive audit and staging review manifest. The
[exact staging manifest](phase-9-staging-manifest.md) inventories **58 text files:
19 modified / 39 added**, including all preserved earlier work and five additions
in this continuation. Tracked diff and every untracked candidate's path/text type
were reviewed; Python/JSON additions parse and a bounded credential-shape scan
found no matches. That is not a comprehensive security scan or certification.
Models, venv, logs, private configs/credentials and build outputs remain outside
this candidate. Suggested commit text is review-only; nothing was staged.

Main/HEAD remain `f4c430cbf42a1168c3e167780dc8ade8844d450f`, index empty, no remote;
all eight checkpoint commits and Phase 1–8 audits/golden data remain unchanged.
No commit/amend/push, paid/cloud service, external message or Phase 10. Required
external spend $0, host compute unpriced. Real BGE/reindex/retrieval, structured
Qwen and sequential residency retain historical evidence, while supported real
RAG and conditional insufficiency acceptance remain open. Final cross-stack
qualification follows only after separately approved real acceptance passes.
**PHASE 9 NOT COMPLETE. STOPPED AT THE REAL-MODEL APPROVAL BOUNDARY.**


## OCTOBER 19 — AUTHORIZED CONDITIONAL GROUNDED ACCEPTANCE EXECUTION

October 19, 2026, approximately 03:09–03:10 America/New_York. **REAL GROUNDED
ACCEPTANCE FAILED. PHASE 9 NOT COMPLETE.** The operator explicitly approved the
frozen [conditional application proposal](phase-9-grounding-acceptance-proposal.md).
Its original NOT APPROVED title remains preserved as preparation history; the
new authorization applied to this execution only and is now closed. Production
code and the proposal were fingerprinted before execution and verified unchanged
afterward. No prompt experiment, code correction, retry or extra generation occurred.

### Authorized versus executed scope

Maximum approval was two authenticated LOCAL_REAL HYBRID application RAG cycles,
two BGE query embeddings and two Qwen generations, zero retries; the second cycle
was conditional on the first passing. **Actual execution: one application RAG
request, one BGE embedding and one Qwen generation.** Positive acceptance failed,
so the insufficiency request was **NOT EXECUTED**. No diagnostic generation,
embedding probe, reindex, model warmup or additional RAG request was made.
Preflight authentication/task/memory/inventory reads were metadata checks only.
The native empty Qwen unload command was cleanup, not another generation.

- Task: `70b45f12-b509-4443-a66f-81b86caf872c`.
- Query: `Which cuisine does review_fixture prefer?`.
- Request/trace: `cde98e23-250b-4ee1-9f3e-bf03b3e8b728`.
- Inference run: `c21a6402-f82e-4163-ada0-90d692fb1d02`.
- Retrieval snapshot: `a874793e-ef38-41b3-aa11-3d553998a8b1`.
- Model call: `737e4e45-e0ce-484f-835e-8faa17196f11`.

The request used direct authenticated FastAPI application HTTP, not a direct
provider-only probe or browser inference claim. A short-lived local token was
renewed for the existing identity/device without changing roles, grants or
versions; owner/task/device identity and enabled registration were checked.
Authenticated task and ACTIVE cuisine-memory reads passed. The source's subject,
predicate, value and normalized text matched the public pinned fixture. Private
credentials were never placed in URLs, source or execution output.

### Preflight, artifacts and pinned configuration

Fresh checks found no resident/unowned model processes or model/controller/app
listeners and no running containers. BGE and Qwen tensor sizes/SHA-256 passed
before and after execution:

| Model | Bytes | SHA-256 |
| --- | --- | --- |
| BGE-small-en-v1.5, revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` | 133466304 | `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad` |
| Existing Qwen2.5-1.5B | 986048512 | `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4` |

Both 32-token and 96-token alias manifests and every referenced blob size/hash
matched prior verified evidence, including the existing ChatML template. No alias
was created or modified. Existing Ollama client reports 0.35.1; runtime metadata
and logs verified the bounded alias settings. The new scoped private copy declared
`grounded_budget_profile=QWEN2_CHATML_0351`; application-side verification confirmed
that profile, context 512, pinned tensor and unchanged production prompt-at-96
SHA-256 `1a722aaf032c5aa2949f0ea576d781870ea18bce6cbb0354b2d4447cccffda76`.
The unchanged GroundedOutput schema fingerprint was
`50ae8981a99f3830462b85606e19e2fc5c40c91edd374dc11070a6f95b669594`.

BGE remained CPU float32, batch one, two threads, 384 dimensions and <=128 input
tokens, sampled RSS ceiling 1024 MiB. Qwen retained the existing
`nova-qwen-phase9-rag96`, context 512, output <=96, two CPU threads, GPU layers 0,
temperature 0, one slot/concurrency one and 2048 MiB ceiling. Runtime logs confirm
CPU buffers, n_ctx 512, two threads and one slot. Startup 30 seconds and inference
eight seconds were unchanged. The recorded 214 prompt tokens plus 96 output
allowance fit 512; no output truncation occurred.

Private controller bearer authentication from the backend container passed via
`host.docker.internal`. The existing loopback-only sandbox profile matched its
reviewed hash; an actual sandboxed external TCP attempt was denied with
PermissionError. Runtime processes inherited that sandbox and offline/local-files-only
settings. This is a bounded syscall check, not packet-capture/security certification.
No cloud/paid inference, download or dependency installation was used.

### Retrieval, final validation and precise failure boundary

Retrieval used the exact existing namespace
`bge-small-en-v1.5@bd60ce951a6ec4edab8518c1b3301686`, with non-simulation vectors.
The actual persisted ranking was:

| Rank | Owned memory UUID | Semantic similarity |
| --- | --- | --- |
| 1, cuisine | `4d4b4842-c804-4e72-90c9-7162d6436c37` | 0.8214419101 |
| 2, beverage | `83850485-9c3c-43d5-ba5d-c71573b6e294` | 0.7816376220 |
| 3, deadline | `3b1d6f94-383e-4276-863c-432ca6c0dc1f` | 0.5767709532 |

These are retrieval measurements, not entailment or a calibrated relevance gate.
The frozen deterministic selector matches the named subject/preferred_cuisine
record, preserves its UUID/full text and excludes unrelated predicates. The
application completed the new retrieved/sent source-binding and privacy-validation
transaction. Final validation duration was **9.720 ms**.

The response was a valid explicit abstention: `abstain=true`, `claims=[]`, with
empty citation IDs. Application/ledger state was **DONE**, LOCAL_REAL,
simulation=false, no fallback; the sole attempt was invoked with cache **MISS**,
finish_reason **stop**, safe_error=null. Application DONE describes valid schema
and policy handling, **not** passing the positive acceptance criterion.

**Failure boundary: no supported positive claim was produced.** This was not a
JSON/schema/citation failure, exhausted token limit, resource refusal or failed
handoff. A valid abstention fails this positive case. Final source/privacy checks
passed for the retrieved/supplied sources; positive citation/quote acceptance was
**NOT EXERCISED**, because claims were empty. No fabricated citation or unsupported
claim was accepted. This abstention is not the separately requested insufficiency
acceptance; Case 2 was skipped exactly as required.

### Measured timing, RSS and sequential residency

| Observation | Actual measurement |
| --- | --- |
| Provider-reported Qwen tokens | **214 input + 11 output = 225 total** |
| Application model-call latency | **6499.811 ms** |
| Authenticated RAG HTTP wall time | **11833.300 ms** |
| BGE controller inference transport | **39.461 ms** |
| Qwen controller inference transport | **5308.167 ms** |
| BGE readiness / shutdown | **3.901 s / 0.032 s** |
| Qwen server readiness / shutdown | **0.496 s / 0.030 s** |
| BGE peak sampled process-tree RSS | **464044032 bytes / 442.55 MiB**, below 1024 MiB |
| Qwen peak sampled process-tree RSS | **1440628736 bytes / 1373.89 MiB**, below 2048 MiB |

The controller recorded exactly BGE then Qwen, both fully stopped. BGE terminated
at 03:09:42.719; a fresh resource check preceded Qwen acquisition at 03:09:42.792.
No model overlap occurred. Qwen readiness is server readiness, not weight-load
latency; weights load lazily during generation. The timing scopes differ and
must not be combined into an invented TTFT/throughput measurement. RSS is sampled
aggregated resident process memory, not a hard hardware quota or instantaneous peak.

| Resource boundary | Free disk bytes | Used swap MiB |
| --- | --- | --- |
| Initial verified preflight | 15072473088 | 983.38 |
| Before BGE acquisition | 15075844096 | 983.38 |
| After BGE termination | 15075479552 | 983.38 |
| Fresh check before Qwen acquisition | 15075475456 | 983.38 |
| After Qwen termination | 14001168384 | 1835.88 |
| Final stopped snapshot | 14000562176 | 1835.88 |

All recorded boundaries passed disk >=5 GiB and swap <2048 MiB; no resource
watchdog violation was recorded. RAM remains 8 GiB; Docker remains
4106604544 bytes / eight logical CPUs. Neither allocation nor thresholds were
changed. These snapshots are not future activation authority or guaranteed
allocatable RAM. No cache pruning, host/Docker restart or volume deletion occurred.

### Preservation, cleanup, regression scope and remaining status

Read-only SQL snapshots before and after matched all six existing vector rows:
three 384-D non-simulation namespace vectors and three original 32-D fixture
vectors, with identical row IDs, vector digests, timestamps and namespaces.
The existing reindex job remained DONE, processed=3, with the same cursor. No
reindex/vector replacement occurred. Application writes were limited to normal
inference/routing/retrieval metadata; existing task/memory data were preserved.

The controller released/terminated both task-owned runtime trees; subsequent
independent process inventory and listener checks passed. Ports 11434/11435/11436
and 8000/8080 have no listener; Docker reports no running containers. Task-owned
PostgreSQL/Redis/backend/gateway services were stopped, volumes preserved.
Scoped private model flags are resource_approved=false and the scoped attestation
was explicitly closed with approval flags false. There is no active lease or
future activation authority. Original private registry files were not enabled;
execution used separate mode-0600 copies under an ignored private directory.

Safe evidence remains ignored under
`.local/phase9/grounding-acceptance-authorized-20261019`, including frozen-input
fingerprints, artifact/alias verification, auth/profile/sandbox checks, actual
run/ledger summaries, residency records, resource boundaries and cleanup proof.
Private token/key/config/closed attestation remain ignored under
`.secrets/grounding-acceptance-20261019`. No raw rejected output/private prompt
logging was added; no private evidence was added to Git.

The preceding **671 backend passes/one real-model skip and 13 controller passes**
remain the applicable unchanged-source offline evidence. Those suites were not
rerun or relabeled as new real-model quality results here. No final Go/frontend/
browser/golden/Kafka qualification ran: the positive prerequisite failed. No real
LLM judge or vision model was configured. Earlier Phase 8 deployment qualifications
and all historical measured results remain unchanged.

This result again demonstrates valid abstention and safe sequential application
handling, not successful positive grounding. Why Qwen abstains despite supporting
evidence remains unresolved; no new causal claim or corrective experiment is
inferred. The insufficiency cycle remains NOT EXECUTED. Future execution requires
a new, separately scoped operator instruction; this approval is closed, not a
remaining retry allowance.

Only this audit changed in the source candidate during execution. Main remains
`f4c430cbf42a1168c3e167780dc8ade8844d450f`, index empty, no remote; candidate remains
58 text files, 19 modified / 39 added. Frozen production/proposal fingerprints
match, Git whitespace checks pass, and Phase 1–8 checkpoints remain intact.
No staging, commit, push, remote change, external message, cloud/paid service or
Phase 10. Required external spend $0, host compute unpriced.
**REAL GROUNDED ACCEPTANCE FAILED. PHASE 9 NOT COMPLETE. STOPPED.**


## OCTOBER 19 — OFFLINE SELECTION-BASED GROUNDING IMPLEMENTATION

October 19, approximately 03:25–03:35 America/New_York. **Offline implementation
and regression PASS; real execution NOT AUTHORIZED / NOT EXECUTED. Phase 9 NOT
COMPLETE.** The new mission authorized simpler grounding implementation and offline
validation, with an explicit stop before real-model execution. No earlier approval
was reused. Existing source, audit history, vectors, artifacts and checkpoints were
preserved. Initial candidate was 58 text files, index empty on the Phase 8 HEAD.

### Root-cause findings: observation versus hypothesis

Existing code/callers and tests, contracts/parser/validator/routing, prior 9G/9H/9I
analysis and the latest failed application acceptance were reviewed without
repeating a real experiment. 9G-A demonstrated exact UUID/full-quote output under
the legacy schema. 9G-B changed the system instruction on the same synthetic user
data/schema and abstained; F wording clarification and later application positives
also abstained. The latest application attempt had correct top-ranked cuisine,
214 input / 11 output tokens, normal finish, safe sequential residency and valid
source/privacy acceptance. Retrieval, truncation and absolute inability to express
the old schema are therefore not adequate explanations of that recorded behavior.

The evidence associates abstention with the production answerability task, not
with a proved single schema/quote-copy/prompt defect. Prompt complexity, abstention
decisions, interactions among instructions and small-model limitations remain
hypotheses. Copying is possible in one control; that does not prove general
question understanding. No latent model reasoning or root cause was invented.
The new design is explicitly authorized task simplification, not a demonstrated
fix for over-abstention or a repetition of an old prompt-only experiment.

### Implemented design and compatibility

The existing deterministic named-subject cuisine/beverage support subset remains
unchanged. A private opt-in `grounded_generation_contract=SELECTION_V1` selects
internal purpose GROUNDED_SELECTION. Default EXTRACTIVE_V1 and FIXTURE retain their
legacy prompt/schema/output behavior. No database migration, new endpoint,
dependency, model, namespace or approval authority was added.

Application evidence validation still handles owner/task/privacy/lifecycle,
full-retrieved-set and newly visible conflicts, bounded selection, original source
bindings and context size. For the new contract only, model-facing evidence is
projected to index/subject/predicate/value. Indices refer exclusively to that
request's selected list; no UUID/full quote must be generated by the model.
Full source text, UUID, binding and provenance remain server-side for validation.

GroundedSelection has three required fields: abstain, evidence_index and answer.
A positive requires a bounded integer index and nonempty answer. An abstention
requires both selection and answer to be null. Boolean indices, missing fields,
extra citation/quote/tool/approval fields and inconsistent output fail closed.
The short system message asks the model to interpret the question using matching
subject/predicate and return the exact value with its index, or abstain. It does
not contain a production subject, answer or real evidence UUID. All evidence
remains untrusted data; tools/actions/approvals remain forbidden.

Independent `verified_selection` checks the selected item exists, matches the
existing structured query/source support contract, and the model answer exactly
equals that item's complete stored value. Only then does it construct the public
claim using the original UUID/full quote and call the unchanged `verified_output`
validator. Source/privacy revalidation, fresh-conflict refusal and terminal DONE
commit remain in the owner-locked transaction. A wrong answer/index, unrelated
source, altered source text, stale source or privacy change cannot acquire a
citation through this mapping. The model still may abstain on a supported case.

Public claims/abstain/extractive answer retain their existing shape; a new response
field carries the verified model answer or null. Metadata explicitly labels
`grounding_contract=SELECTION_V1` and
`citation_origin=APPLICATION_VERIFIED_SELECTION`. These are application-derived
citations, **not** model-generated UUIDs/quotes. No model claim is inferred when
there is no valid selected answer. The private configuration choice is excluded
from public inventory; the actual executed contract is labeled on run metadata.
The internal purpose also separates new requests in existing routing/cache keys.

Modified production files: inference/contracts.py, grounding.py, providers.py,
registry.py, service.py, model_routing/contracts.py and providers.py. Added
`backend/tests/test_grounded_selection.py`. Updated README, Phase 9 architecture,
this additive audit and staging manifest; added the
[selection acceptance proposal](phase-9-selection-acceptance-proposal.md).
The immutable 9H matrix, legacy prompt fingerprint and previous tests/expected
outputs were preserved. No assertions were weakened to accommodate the new path.

### Budget and deterministic validation

The new prompt-at-96 fingerprint is
`7529089aa6ff8c7700b7c497ac04021c5af7d5b02849efd2d467b6f2922127b2`.
Both prompt fingerprints, pinned artifact/context/profile and output 16–96 remain
checked before provider transport. The same conservative 136-system/32-framing/
16-margin plus serialized-user-byte and output bound applies. Selection projection
is budgeted before inclusion; oversized values/quotes are never sliced. No context,
output, CPU, memory, concurrency, startup or inference ceiling was increased.

Offline tokenizer reconstruction used the already installed tokenizers package
and read **5,931,697 GGUF metadata bytes / zero tensor bytes**, importing no model
loader or ML framework. New system: **97 tokens**. Public positive request:
**154 input + 96 output allowance = 250/512**, conservative bound **451/512**.
Its compact controlled positive output is **22 tokens**, compared with the earlier
long UUID/full-quote contract. These are offline counts, not runtime usage,
completion likelihood, load fit or latency measurements. The new nullable-field
schema/contract remains unexercised in actual Qwen generation.

| Executed check | Actual result |
| --- | --- |
| New focused selection regressions | **29 passed**, 1.32 s |
| Complete current-source PostgreSQL backend suite | **700 passed, one explicit real-model skip**, 64.80 s |
| Backend Ruff lint / format | PASS; 110 app/test Python files formatted |
| Existing environment pip compatibility | PASS; no broken requirements, no installation |
| Host controller/resource/process tests | **13 passed**, 0.055 s, no models |
| Dedicated `_test` DB migration/head/drift setup | PASS as mandatory full-suite setup |
| Git whitespace / added Python syntax / text candidate review | PASS |
| New real inference / acceptance | NOT EXECUTED; fresh approval required |
| Final Go/frontend/browser/golden/Kafka qualification | NOT EXECUTED; follows successful separately approved real acceptance |

New tests cover positive index/value validation and original citation attachment,
insufficiency/conflict abstention, wrong value/subject/predicate, invented index,
invalid schema/missing/null/boolean fields, attempted fabricated UUID/altered quote,
extra approval/tool fields, injection-bearing source data, resource/profile/context
refusal, model refusal, malformed JSON and actual application transaction refusal
when owner/expiry/value changes during scripted generation. Existing full-suite
coverage retains deletion/scope/privacy/time, visual source integrity, exact quotes,
owner isolation, fresh conflict and commit-lock tests. Deterministic responses do
not measure learned model quality or real model injection resistance.

No test failed. An initial import-order lint issue was automatically corrected
before the passing checks. The focused and full suites ran sequentially using the
existing backend-test image, read-only current source, isolated `_test` PostgreSQL
and test Redis, offline flags and empty real registry environment. DB/runner caps
remained 512 MiB each; no resource increase or application data connection was
needed. No image/model/package download or installation occurred. There is no
backend static type checker configured; none was installed or claimed executed.

### Resources, remaining boundaries and next approval

Before offline work, used swap measured 1507.88 MiB. Final stopped snapshot at
03:35:03: **14,065,217,536 bytes free disk**, **1483.88 MiB swap used**; physical RAM
8 GiB and Docker allocation remain unchanged. No host/Docker restart, protected
cache deletion or volume pruning occurred. No model/controller/app was started;
only dedicated offline test containers ran and were stopped with volumes retained.
There are no running containers or model processes. Private real model registries
were not modified/enabled and no activation attestation was issued. Model RSS,
runtime tokens/latency and real quality are NOT MEASURED in this task.
Safe test/count/resource evidence is ignored under
`.local/phase9/selection-contract-offline`. No private raw prompt logging was added.

The new proposal requests exactly the existing owner-authenticated named-subject
positive and conditional spacecraft-code insufficiency cases, existing task and
BGE namespace, same artifacts and 96-token Qwen alias, at most two BGE embeddings,
two Qwen generations/two application cycles, zero retries. The new contract must
be explicitly selected in private config. Require fresh operator approval,
resources/artifact/profile/owner/controller/sandbox checks, sequential unload and
verified cleanup. The prior failed approval is closed; **no execution is authorized
by this offline mission**. The frozen earlier proposal is not silently amended.

Unknown/first-person/visual questions remain outside the independently checked
support subset. An insufficiency run would test explicit abstention on empty
selected evidence, not general relevance calibration. Exact value matching rejects
paraphrases rather than guessing entailment. Completeness and truth of stored facts
are not established. Success under the new model-facing contract is still unknown;
no deterministic test or shortened token count substitutes for real acceptance.

Phase 9 remains NOT COMPLETE. After separately approved positive and insufficiency
acceptance passes, final backend/Go/frontend/browser/golden/Kafka/security/privacy
qualification and cleanup are still mandatory before completion. The README
roadmap is broad rather than an implementation-ready Phase 10–12 specification.
Following the requested ordering, formal next-phase planning is deferred until
Phase 9 acceptance. Its minimum sequence is reuse existing proactive/agent flows
for Phase 10, close measured reliability/security/performance gaps for Phase 11,
and local release/runbook/deployment qualification for Phase 12. No phase changes
or deployments are authorized; each needs explicit operator approval.

Candidate now **60 text files: 19 modified / 41 added**, including two additions
in this continuation. The [staging manifest](phase-9-staging-manifest.md) was
refreshed for review only. Main remains
`f4c430cbf42a1168c3e167780dc8ade8844d450f`, index empty, no remote; Phase 1–8
checkpoint history and historical audits/datasets remain intact. No staging,
commit, push, paid/cloud API, external message or Phase 10 implementation. Required
external spend $0; host compute unpriced. **STOPPED FOR FRESH REAL ACCEPTANCE
AUTHORIZATION. PHASE 9 NOT COMPLETE.**


## OCTOBER 19 — AUTHORIZED SELECTION_V1 REAL ACCEPTANCE

October 19, approximately 04:04–04:06 America/New_York. **REAL GROUNDED ACCEPTANCE
PASSED for both specified cases. Phase 9 remains pending final cross-stack
qualification; this is not Phase 9 completion or a general model-quality sign-off.**
The operator explicitly approved the frozen
[selection proposal](phase-9-selection-acceptance-proposal.md). Its preparation
NOT APPROVED title remains historical; this execution used the new explicit
approval, which is now closed. Earlier failures and measurements remain unchanged.

### Scope, preflight and unchanged configuration

Actual execution exactly matched the approval maximum: **two authenticated
LOCAL_REAL HYBRID application RAG requests, two BGE query embeddings and two Qwen
generations, zero retries**. Case 2 was submitted only after all positive checks
passed. No warmup generation, extra model probe, alternative prompt, schema change,
output repair, reindex or further application RAG request occurred.

Before activation, the frozen proposal, current production sources, model/prompt/
schema fingerprints, resource profile, task/owner/device identity, private controller
bearer authentication and absence of resident/unowned models/listeners were checked.
The preceding unchanged-source offline evidence remains 700 backend passes/one
real-model skip and 13 controller passes; those tests were not rerun or relabeled
as new model-quality results here. A network-disabled metadata-only container
computed the schema/prompt fingerprints without any inference or model load.

Both artifact sizes/hashes passed before and after:

- BGE-small-en-v1.5 revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`,
  133466304 bytes, SHA-256
  `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.
- Existing Qwen2.5-1.5B, 986048512 bytes, SHA-256
  `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.

All referenced alias blob sizes/hashes and both original/96-token manifests
matched earlier verified evidence, including the ChatML template. No alias or
artifact was created or modified. Existing Ollama reports 0.35.1. Scoped private
configuration explicitly enabled SELECTION_V1 and QWEN2_CHATML_0351; application
verification confirmed the actual configuration and exact BGE namespace.
Prompt-at-96 SHA-256:
`7529089aa6ff8c7700b7c497ac04021c5af7d5b02849efd2d467b6f2922127b2`.
GroundedSelection schema SHA-256:
`23f32279107f6d1070873532f0d35c31c40d7ba651e36b0792ac06ae68330ab8`.
Frozen proposal/source fingerprints matched again after execution. Production
code, prompts, schemas and the frozen proposal were not edited during execution.

BGE retained CPU float32, two threads, batch one, <=128 input tokens, 384 dimensions
and 1024 MiB sampled RSS ceiling. Qwen retained nova-qwen-phase9-rag96, context 512,
output <=96, CPU threads two, GPU layers zero, temperature zero, concurrency/slot
one and 2048 MiB ceiling. Existing startup 30 seconds, inference eight seconds,
lease/admission/watchdog and zero-queue restrictions were unchanged. Runtime
processes used the existing loopback-only OS sandbox and offline/local-files-only
settings. A sandboxed external TCP attempt was refused with PermissionError;
loopback/controller reachability and bearer authentication passed. This is a
bounded enforcement check, not packet-capture/security certification.

Application calls used direct authenticated FastAPI HTTP with the existing owner
and task `70b45f12-b509-4443-a66f-81b86caf872c`. Only the existing local identity's
short-lived token was renewed; roles/grants/versions were unchanged. Task ownership,
enabled identity/device registration and the ACTIVE cuisine record were verified;
subject/predicate/value/full normalized text matched the public pinned fixture.
Private credentials stayed out of URLs, source and printed execution output.

### Case 1 — supported positive PASS

Query: `Which cuisine does review_fixture prefer?`

- Request/trace: `2f8da404-95dd-497f-b06e-219047b2251e`.
- Inference run: `5d1174d0-4fc7-47d0-a627-9f46163e3427`.
- Retrieval: `82b5b631-369e-4d58-9094-600b42f3c46a`.
- Model call: `83c8afb9-6a5e-4ae9-903b-1d0da9cff0d7`.

Actual model-selected index was **0**, abstain=false, with model-generated value
**Italian pasta**. Application response preserved that model answer. The selected
owned cuisine UUID was `4d4b4842-c804-4e72-90c9-7162d6436c37`; the application attached
and verified its complete original quote:
`review_fixture preferred_cuisine: Italian pasta`.
Final citation IDs contained exactly that UUID. This was an **application-derived
citation**, not a model-generated UUID or model-copied quote.

The bounded operator observer recorded the actual returned index, abstention flag,
nullness and answer fingerprint without changing the request/response or issuing
any additional call. Its answer hash matched the application response:
`aa11617ef16a748b1dc08b6748ae2e29264a9ecaba5aa0e300990bf06b0da090`.
No private raw prompt or rejected output was logged. The new wire schema and
cross-field checks accepted the actual model response; the application independently
verified selected index, exact value and structured subject/predicate/text support.
Original UUID/full quote checks, retrieved/sent source bindings, fresh conflict
checks and final privacy validation completed under the existing acceptance
transaction. Validation duration was **14.799 ms**. No unsupported claim was accepted.

The persisted ranking in the exact non-simulation BGE namespace
`bge-small-en-v1.5@bd60ce951a6ec4edab8518c1b3301686` was cuisine first (similarity
0.8214419101), beverage second (0.7816376220), deadline third (0.5767709532).
The deterministic support selector supplied the cuisine tuple only. Scores were
not used as truth or a new relevance threshold.

### Case 2 — conditional insufficiency PASS

Executed only after Case 1 PASS.
Query: `What is review_fixture's spacecraft launch authorization code?`

- Request/trace: `5fb411b6-34ea-4179-9c5e-110807173dbb`.
- Inference run: `52552730-cb09-475f-a81a-334fa5a9cd76`.
- Retrieval: `25c70d68-2297-44de-9a73-ea1ccd1e25b9`.
- Model call: `1a76bd35-db13-466a-957a-c7d6e564b434`.

Actual model output had **abstain=true, evidence_index=null, answer=null**. The
public result had claims=[], response=null and empty citation IDs; its compatible
legacy extractive answer string was empty. No answer, selected model evidence,
fabricated citation, unsupported claim or external action was produced. Schema,
source-binding and privacy validation passed in **4.870 ms**.

Real retrieval still returned the three unrelated owned memories, ranked deadline
(0.6362050148), beverage (0.5892026669), cuisine (0.5462145154), all in the exact real
namespace. The declared deterministic preference subset supplied **empty selected
model context** for this unsupported question. Thus this proves explicit model
abstention on empty selected evidence in this contract, **not general unknown-answer
detection, calibrated relevance or model understanding of arbitrary irrelevant
facts**. No threshold was introduced or tuned to force abstention.

### Actual measurements and sequential residency

Both application runs were DONE, LOCAL_REAL, simulation=false, fallback_used=false,
SELECTION_V1, citation_origin=APPLICATION_VERIFIED_SELECTION. Each model ledger
had exactly one invoked phase9-local attempt, cache MISS, finish_reason=stop and
safe_error=null. No earlier completion was replayed or substituted. Actual model:
**nova-qwen-phase9-rag96**, pinned Qwen fingerprint above.

| Measurement | Positive | Insufficiency |
| --- | --- | --- |
| Provider-reported input / output tokens | **154 / 19**, total 173 | **130 / 18**, total 148 |
| Input plus reserved 96 output | 250/512 | 226/512 |
| Application model-call latency | **6683.123 ms** | **5498.805 ms** |
| Authenticated RAG HTTP wall time | **12311.788 ms** | **8991.005 ms** |
| BGE controller inference transport | 36.083 ms | 33.874 ms |
| Qwen controller inference transport | 5268.045 ms | 4643.103 ms |
| BGE readiness / shutdown | 4.193 s / 0.032 s | 3.257 s / 0.036 s |
| Qwen server readiness / shutdown | 0.591 s / 0.027 s | 0.205 s / 0.028 s |
| BGE peak sampled process-tree RSS | 467091456 bytes / **445.45 MiB** | 483917824 bytes / **461.50 MiB** |
| Qwen peak sampled process-tree RSS | 1290190848 bytes / **1230.42 MiB** | 1488830464 bytes / **1419.86 MiB** |

The controller recorded exactly BGE → Qwen → BGE → Qwen, with every runtime stopped
before the next acquisition and a fresh host resource check at each boundary.
For Case 1 BGE stopped at 04:05:01.303 before Qwen acquired at 04:05:01.369;
Case 2 BGE stopped at 04:05:12.256 before Qwen acquired at 04:05:12.294. No model
residency overlap occurred. Qwen server readiness is not weight-load latency;
weights load lazily during inference. HTTP totals include sequential acquisition,
retrieval and application work, so are not the eight-second model-inference
scope. No TTFT/throughput or general capacity measurement is claimed. Sampled
aggregated RSS is not an instantaneous hard hardware quota.

| Resource boundary | Free disk bytes | Used swap MiB |
| --- | --- | --- |
| Initial fresh preflight | 17001848832 | 579.88 |
| Case 1 before BGE | 16999124992 | 579.88 |
| Case 1 after BGE | 16998100992 | 579.88 |
| Case 1 fresh before Qwen | 16998096896 | 579.88 |
| Case 1 after Qwen | 16997732352 | 1347.56 |
| Case 2 before BGE | 16997638144 | 1347.56 |
| Case 2 after BGE | 16996573184 | 1347.56 |
| Case 2 fresh before Qwen | 16996573184 | 1347.56 |
| Case 2 after Qwen | 16996298752 | 1331.56 |
| Final stopped state | 16995946496 | 1331.56 |

Recorded boundaries passed disk >=5 GiB and swap <2048 MiB; no resource/security
watchdog violation was recorded. RSS remained below BGE 1024 / Qwen 2048 MiB.
Physical RAM remains 8 GiB; Docker allocation remains 4106604544 bytes / eight
logical CPUs. No ceiling, host/Docker allocation, context, thread count or timeout
was increased. These measurements are snapshots, not future activation authority.

### Preservation, cleanup and status

Read-only before/after snapshots matched all six original vector rows, their
UUIDs, values' digests, timestamps, dimensions and namespaces: three real 384-D
and three fixture 32-D embeddings. The existing reindex job remained DONE,
processed=3, cursor unchanged. No reindex, vector replacement, memory mutation or
application data deletion occurred. Normal run/model-call/retrieval metadata was
added by the two authorized application operations.

Both native unload/process termination and independent subsequent checks passed.
No model/controller process or task-owned listener remains on 11434/11435/11436
or 8000/8080. All task-owned PostgreSQL/Redis/backend/gateway services were stopped;
Docker reports no running containers and application volumes were preserved.
Scoped mode-0600 private configurations again have resource_approved=false; the
fresh private attestation was explicitly closed with approval flags false. There
are zero active leases. Existing original private configs/defaults were preserved.

Evidence remains ignored under `.local/phase9/selection-v1-acceptance-authorized-20261019`:
frozen source/proposal fingerprints, artifact/alias verification, auth/profile/
sandbox checks, actual run/ledger results, bounded response-selection observations,
resource/residency records, before/after vector snapshots and independent cleanup
proof. Private credentials/configs/closed attestation remain ignored under
`.secrets/selection-v1-acceptance-20261019`. The operator-only observer retained
bounded index/nullness/answer-digest metadata, forwarded the original runtime
result unchanged and made no additional model requests. No production code was
modified to collect these observations.

This is the first successful owner-authenticated positive and conditional
insufficiency acceptance for the new narrow SELECTION_V1 contract. It demonstrates
that this simpler contract can work for these cases; it does not establish why
historical legacy prompts abstained, repeated-run reliability, general semantic
entailment, truth of stored facts or production readiness. Application-derived
citations must not be represented as model-copied citations. Historical legacy
failures and fixture/real evaluation scores remain preserved.

**REAL GROUNDED ACCEPTANCE PASSED. Phase 9 remains pending final cross-stack
qualification and is not marked COMPLETE.** Final backend/Go/frontend/browser/
golden/Kafka/security/privacy qualification was **NOT EXECUTED** here: the latest
operator instruction explicitly required stopping after this execution and cleanup.
The earlier 700 backend passes/one skip and 13 controller passes retain their
original offline scope. No vision or real LLM judge was enabled; earlier Phase 8
Kubernetes/NetworkPolicy qualifications are unchanged. Phase 10 was not started.

Only this audit changed in the source candidate. Main remains
`f4c430cbf42a1168c3e167780dc8ade8844d450f`, index empty, no remote; candidate remains
60 text files, 19 modified / 41 added. Frozen production and proposal fingerprints
match; Git whitespace check passed. No staging/commit/push/remote change, model or
dependency download, cloud/paid API, external message, cache/volume deletion or
Phase 10. Required external spend $0, host compute unpriced. This scoped approval
is closed. **STOPPED AFTER ACCEPTANCE AND VERIFIED CLEANUP.**


## OCTOBER 19 — FINAL CROSS-STACK QUALIFICATION AND COMPLETION

Executed October 19, 2026, approximately **04:13–04:25 America/New_York**. Final
service/process cleanup completed at approximately 04:25:24. **PHASE 9 COMPLETE
for the specified bounded local implementation, real acceptance and qualification
scope.** The operator explicitly authorized offline qualification and justified
Phase 9 corrections, while prohibiting additional real inference, downloads,
resource increases, deployment, commits/pushes and Phase 10. Those boundaries
were preserved. All earlier measured results and failures remain historical.

### Mandatory gates and completion decision

| Required gate | Evidence / disposition |
| --- | --- |
| Real BGE inference, owned real reindex, semantic/hybrid retrieval | Earlier authenticated real execution retained; no additional load required or performed |
| Real Qwen structured generation and sequential residency | Earlier authenticated evidence retained, including the accepted SELECTION_V1 runs |
| Real supported grounded answer | PASS, run `5d1174d0-4fc7-47d0-a627-9f46163e3427`, actual model value Italian pasta at index 0, original UUID/full quote application-verified |
| Real conditional insufficiency | PASS, run `52552730-cb09-475f-a81a-334fa5a9cd76`, null answer/index, explicit abstention and no citations |
| Backend, migrations, routing/cache/retrieval/grounding/privacy/security | PASS, 700 tests, one separately marked real-model opt-in skip |
| Controller/resource/process regressions | PASS, 13 tests; no model loads |
| Go race and vet | PASS, two gateway tests plus vet; Go does not implement Kafka workers |
| Configured frontend lint/typecheck/build | PASS with existing installed dependencies |
| Browser replay, strict local-auth and actual local OIDC | PASS, 51 + 3 + 2 across separate profiles |
| Kafka/outbox/duplicate/failed-event/HITL/recovery | PASS, actual dedicated local broker/workers and outage recovery |
| Golden baseline FULL / SMOKE / REGRESSION | PASS, 104/104 / 10/10 / 25/25, critical violations zero |
| Source/credential/artifact review and required cleanup | PASS; no staged/private/runtime artifacts, services stopped, dedicated volumes preserved |

There is **no unresolved mandatory blocker** under the requested gate list. The
real-model opt-in pytest skip does not replace real acceptance: those two actual
application cases already passed separately. The deliberately cautious candidate
is an expected negative control (23/25, gate FAIL), not the mandatory baseline.
Optional or out-of-scope capabilities below remain explicitly unqualified; they
were not silently relabeled as passing completion gates.

### Environment and isolation

Source: main at `f4c430cbf42a1168c3e167780dc8ade8844d450f`, current unstaged/untracked
Phase 9 candidate. All eight Phase 1–8 checkpoint commits, historical audits and
golden dataset/baselines remain intact. Current backend source/migrations were
mounted read-only into existing images; no image rebuild/pull or dependency
installation was performed. Model tests remain opt-in/off by default, real
provider registries empty and local model/embedding execution disabled.

Full backend used the dedicated `_test` PostgreSQL and test Redis, existing
nova-backend-tests:latest, DB/runner 512 MiB each (one/two CPUs), Redis 48 MiB.
The autouse test guard refuses cleanup against a non-`_test` database. Browser,
Kafka, authentication and golden integration used a separate Compose project
**nova-phase9-finalq**, with fresh dedicated PostgreSQL/Redis/media/auth/Kafka/
Keycloak volumes. The protected application database, real embeddings, model
artifacts, private real registries and original identity services were never
mounted into that qualification application.

The application used existing nova-backend:latest, nova-gateway:local, local
PostgreSQL/Redis, Apache Kafka 4.0.1 and Keycloak 26.4.2 images with pull=never.
Application DB/backend/Redis/gateway caps were 192/384/64/64 MiB; Kafka and Keycloak
768 MiB each, workers 384 MiB each. Kafka workers were stopped before starting
OIDC to keep stages separate. Docker allocation stayed unchanged. Native frontend
used installed Node **26.10.0**, npm **11.19.1**, Next.js **16.4.0**, existing browser
binaries and production build. Build/server Node heap ceilings were bounded to
768/512 MiB; these are heap settings, not claims of hardware-enforced RSS quotas.
Go used the existing compiler image, **Go 1.25.14 linux/arm64**, network disabled,
GOPROXY=off and GOTOOLCHAIN=local, memory 384 MiB/two CPUs. The host lacks `go`
on PATH; no toolchain download/install was necessary.

### Exact qualification commands and results

The actual temporary overlays were preserved as ignored evidence copies:
`.local/phase9/final-qualification-20261019/backend-test-overlay.yaml` and
`qualification-overlay.yaml`. The former uses dedicated backend-test services;
the latter binds current read-only source, disables real configuration, applies
the caps above and selects demo/local/oidc via QUAL_AUTH_MODE.

Backend:

```sh
docker compose -f compose.yaml -f /tmp/nova-phase9-final-offline.yaml --profile test run --rm backend-tests sh -c 'pytest -q && ruff check app tests && ruff format --check app tests && pip check'
python3 scripts/test_phase9_residency.py
```

**700 passed, one explicit real-model skip, 64.44 s**. Ruff lint and format check
passed, **110 app/test Python files** formatted; pip check reported no broken
requirements. Controller **13 passed, 0.048 s**, with deterministic callbacks and
a small non-model child-termination check. No configured backend mypy/pyright
runner exists; none was installed or claimed executed. Mandatory suite setup
upgraded/checks the isolated test DB. Dedicated application `alembic current`
reported **0011_inference_registry (head)** and `alembic check` reported no new
upgrade operations. No application downgrade or migration rewrite occurred.

Go, from gateway mounted read-only at /src:

```sh
docker run --rm --pull never --network none --memory 384m --cpus 2 -v /Users/pragnyathreddie/NOVA/gateway:/src:ro -w /src -e GOPROXY=off -e GOTOOLCHAIN=local nova-gateway-compiler:local sh -c 'go version && go test -race -count=1 -json ./... && go vet ./...'
```

**Two tests passed with race detection**, package duration **1.023 s**, vet exit 0.
This covers the existing gateway/proxy/rate-limit tests. It is not Go Kafka,
outbox, consumer-recovery or approval coverage; those components are Python and
were exercised separately below. An initial host invocation failed because Go
was not installed on PATH; relative log paths also used the wrong working directory.
Correcting runner/paths used the existing compiler image. No source fix, download
or failed race test was hidden by that environment correction.

Frontend, in frontend with NEXT_TELEMETRY_DISABLED=1 and bounded Node heap:

```sh
npm run lint
npm run typecheck
npm run build
```

All PASS using installed dependencies. There is **no separate configured unit/
component runner**; npm's configured test command is Playwright. No npm ci/install,
package upgrade or fresh advisory scan was performed. Production source did not
change during this qualification; the current source build was used for browsers.

Browser commands used the dedicated COMPOSE_PROJECT_NAME and COMPOSE_FILE inherited
by operator hooks, E2E_BASE_URL default localhost:3000, retries=0 and trace=off:

```sh
npm run test:e2e -- --trace off
npm run test:e2e -- tests/security.spec.ts --grep 'authenticated local stack' --trace off
npm run test:e2e -- tests/security.spec.ts --grep 'local OIDC provider' --trace off
```

| Profile | Final result |
| --- | --- |
| Replay/full browser profile | **51 passed, five explicit auth/OIDC profile skips, 46.9 s** |
| Strict local-auth profile | **3 passed, 2.2 s** |
| Actual local Keycloak OIDC profile | **2 passed, 3.0 s** |

Coverage is **56 cases across three profiles**, not one 56-pass invocation. The
new browser case explicitly uses scripted FIXTURE transport to check visible
UUID/quote and abstention/null-response fields, without a model call. It is UI
rendering evidence, not application grounding or real inference acceptance.
Other browser cases retain their established real-service/scripted-route scopes.
Local auth checks HttpOnly/Strict cookies, login/logout and cross-origin refusal;
OIDC uses the dedicated local authorization-code/PKCE provider and rejects forged
callback state. No external login or production identity service was contacted.
Tokens/passwords stayed mode-0600 in ignored files or dedicated private volumes;
auth traces were disabled and logs redact runtime credential values.

The first replay attempt had **50 passed, one failed, five skipped, 47.2 s**.
The operator-only critical-fault Python hook targeted the default Compose project
because the browser runner lacked the qualification COMPOSE environment. It did
not reach the stopped protected backend. Passing the correct dedicated project/
files fixed this environment mismatch. The affected test then passed alone, and
the unchanged full replay suite passed as above. No assertion, fault injection
or expected critical violation was removed. No automatic retry was enabled.

For integration, let **C** denote:

```sh
docker compose -p nova-phase9-finalq -f compose.yaml -f compose.phase8.yaml -f compose.oidc.yaml -f /tmp/nova-phase9-final-qualification.yaml
```

Services were started only with `C up -d --no-build --pull never --wait` and the
required service names. Existing local CLI provisioned dedicated owner/other-owner
identities and private tokens; actual application grants were never changed.
The existing local OIDC provisioner was invoked with its private output directory
redirected to the qualification folder, preserving original runtime credentials.

Kafka/HITL and recovery:

```sh
python3 scripts/acceptance_phase8.py --inject-duplicates
python3 scripts/reliability_phase8.py --tasks 1 --outage
```

NOVA_TOKEN_A/B were private dedicated tokens; COMPOSE_PROJECT_NAME/COMPOSE_FILE
pointed only to qualification. For the recovery script's explicit Compose stop/up
commands, an operator wrapper added the same OIDC/qualification overlays, preserving
all existing caps rather than restarting Kafka with unconstrained base settings.
No production script or event policy was modified.

Actual acceptance task **2f6c6014-7218-4bdc-92be-8311b3a4aeaf** retained its UUID
through Mobile: **nine outbox events, three consumer groups, one proactive job**,
proposal **57c4c1fc-0487-4691-b7f1-ecfbe564be4d**. Three duplicate deliveries caused
no extra effect; a forged approval-like envelope produced **three dead letters**.
The approval hash remained bound to the proposal payload and simulated execution
returned external_message_sent=false. Foreign owner reads returned 404 and no
bearer returned 401. No actual external message was sent.

The minimal recovery probe used one continuity task (four HTTP samples, not a
capacity benchmark). During the actual dedicated Kafka outage, task
**5e31fa5f-22aa-4292-851c-e68bca201243** committed pending outbox work and persisted.
After broker restart, **two events** reached all groups in **28.033 s** from the
restart command, same task retained. This verifies this bounded broker recovery,
not HA, disk loss, sustained load or arbitrary distributed-failure correctness.
Atomic rollback, namespace isolation and partial reindex recovery are covered by
the full PostgreSQL suite; no interrupted real-model batch was added here.

Golden, through `C exec -T backend`:

```sh
python -m app.evaluation.cli --suite FULL
python -m app.evaluation.cli --suite SMOKE
python -m app.evaluation.cli --suite REGRESSION
python -m app.evaluation.cli --suite REGRESSION --configuration CAUTIOUS_THRESHOLD
```

| Suite/configuration | Run UUID | Actual result |
| --- | --- | --- |
| FULL baseline | f4f32455-60d6-4473-87f1-d41941322ca1 | **104/104**, critical=0, gate PASS, CLI exit 0 |
| SMOKE baseline | 35ea8901-656e-4db9-9ded-71dc78d43b11 | **10/10**, critical=0, gate PASS, CLI exit 0 |
| REGRESSION baseline | 3fa185a5-0460-41b3-99a5-7ab1f85fcdef | **25/25**, critical=0, gate PASS, CLI exit 0 |
| Deliberately cautious negative control | 7d3c8797-a45b-412f-acb5-551e43233556 | **23/25**, critical=0, gate FAIL, expected CLI exit 1 |

The candidate's two utility losses remain failures; it was not promoted or
relabeled as passing. Original scenarios, expected labels, baseline files and
thresholds were not changed. These are deterministic fixture evaluations, not
real-model quality scores or human judgments.

### Security, database and source review

The complete backend suite retains legacy EXTRACTIVE_V1 and new SELECTION_V1,
routing/cache owner isolation, malformed/extra tool/approval authority refusal,
prompt-injection boundaries, fabricated UUID/altered quote rejection, structured
support/conflict gates, source bindings, memory and visual owner/task/privacy/
lifecycle checks, revalidation during generation, atomic terminal acceptance,
reindex transaction/recovery, resource refusal and safe diagnostics. Controller
checks cover admission, expiry, cancellation, invalid leases and process cleanup.
No cloud fallback or externally enabled model tests were configured. These finite
regressions are not a comprehensive security, penetration or advisory certification.

Final qualification SQL confirmed no leftover nova_eval_ schemas, empty real
registry settings and **zero DONE LOCAL_REAL runs** in this dedicated application's
inference metadata. Its six inference rows were fixture results or honest refusals,
not newly executed real models. Real application data and the six earlier real/
fixture vectors were not connected to or modified by qualification.

Volume inspection confirmed **six dedicated named volumes and five fresh anonymous
Kafka image volumes**, all exclusively mounted by qualification containers. An
initial operator check incorrectly required every volume name to carry the project
prefix. Inspection found the exceptions were image-created anonymous volumes,
created with the new qualification Kafka/Kafka-init containers. Their anonymous
labels, creation times within two seconds of those containers and exclusive project
usage were independently verified. This corrected the inspection's naming assumption;
no shared/original application volume was accepted or deleted. Existing security
assertions and user-data isolation requirements were not weakened.

Every tracked diff and untracked candidate path/text type was reviewed. Added
Python/JSON parse checks and a bounded credential-shape scan passed; no unexpected
binary, symlink, model weight, private registry/token/key, runtime log/database,
browser trace/screenshot, dependency or build output is in the source candidate.
This scan is not a general secret-detection guarantee. Generated evidence and
operational overlays remain ignored under `.local/phase9/final-qualification-20261019`;
new qualification credentials remain private under `.secrets/final-qualification-20261019`.

### Resources and verified cleanup

Initial preflight: disk **16,573,296 KiB free**, swap **1123.56 MiB**, physical RAM
**8,589,934,592 bytes**, Docker **4,106,604,544 bytes / eight logical CPUs**, macOS
reported **64%** system-wide free percentage. The percentage is not guaranteed
allocatable model RAM. No model process, active container or unauthorized runtime
was used. Heavy suites ran sequentially, with a task-owned two-second resource
watcher for the integration stages; violating disk/swap gates would stop only
qualification containers and its native frontend process group.

The watcher recorded **232 snapshots**: free disk minimum **16,517,509,120 bytes**;
swap range **1083.56–1356.06 MiB**, below the unchanged strict 2048 MiB limit. Final
stopped snapshot: disk **16,522,108,928 bytes**, swap **1284.06 MiB**, RAM and Docker
allocation unchanged; macOS reported **35%** system-wide free percentage. No
resource-stop condition occurred. No host/Docker restart, model activation,
allocation increase, model/cache deletion or Docker volume prune was used.

`C stop` stopped all task-owned services. Native production frontend and resource
watcher process groups were terminated/finished. Independent checks found no
running Docker containers or task listeners on **3000/8000/8080/8180/5432/6379**
or model/controller ports **11434/11435/11436**; no model process remained. All
original application volumes and the inventoried dedicated named/anonymous
qualification volumes were preserved. No real registry was enabled, model lease acquired or
model activation attestation issued in this qualification. Previous scoped model
configurations and closed approvals remain inactive. Model RSS/tokens/latency were
not measured here because **zero additional real inference occurred**.

### Final documentation, Git and retained limits

This continuation added one explicitly scripted citation/abstention rendering
case to `frontend/tests/inference.spec.ts`; no production implementation defect
required a code correction. Test environment/project targeting and volume
inspection assumptions were corrected in ignored operator harnesses. README,
architecture notes, this additive audit and staging manifest now reflect actual
Phase 9 completion and its limits. No previous audit was rewritten.

Candidate remains **60 text files: 19 modified / 41 added**, all preserved prior
work included. Main/HEAD remain `f4c430cbf42a1168c3e167780dc8ade8844d450f`, index
empty, no remote; no staging, commit, amend, push or remote operation. The
[exact staging manifest](phase-9-staging-manifest.md) and suggested checkpoint
message are review artifacts only. Required external spend $0; host compute unpriced.

Retained limits include the narrow structured support subset, exact-value matching
rather than general entailment, model abstention on empty selected context rather
than calibrated unknown-answer detection, application-derived citation provenance,
finite two-case real acceptance, single-host/process assumptions, sampled memory
rather than hard model quotas, untested real vision/LLM judge, no sustained/streaming
model benchmark or general quality claim, and unverified actual interrupted real-
vector batch recovery. Existing deterministic recovery coverage is not relabeled
as a real-model crash experiment. No new hosted CI, advisory/container scan,
Kubernetes/Terraform deployment or production qualification was performed. Phase 8
Kubernetes rollout/NetworkPolicy limitations remain unchanged.

**PHASE 9 COMPLETE (specified local acceptance and final qualification).** No
mandatory blocker remains. Phase 10 has **not started**. Next action is operator
review of the manifest/checkpoint summary and explicit Git checkpoint authorization;
no commit is implied by completion, and subsequent phase work requires its own
approval. **STOPPED WITH CLEANUP VERIFIED; NO REAL MODELS ACTIVE.**
