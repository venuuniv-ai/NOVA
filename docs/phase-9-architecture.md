# Phase 9: explicit local inference and grounded evidence

**Qualified local Phase 9 COMPLETE — October 19, 2026.** Both real SELECTION_V1
application cases and mandatory offline cross-stack qualification passed. Real
configuration remains disabled; no runtime auto-starts. See the dated final audit
for precise scopes, historical failures and unchanged deployment/quality limits.

Reference: [implementation scope](phase-9-implementation-spec.md).
Resource gate: [measured preflight](phase-9-resource-preflight.md).
Results: [final audit](phase-9-final-audit.md).

Browser → same-origin Next gateway → Go → independently authenticating FastAPI →
owned inference service → existing ModelRoutingService (single explicitly selected
provider, existing pricing/privacy/circuit/cache ledger) → fixture or bounded
local OpenAI-compatible transport. No cloud adapter or downloader is enabled.

FIXTURE preserves deterministic defaults. LOCAL_REAL uses only a server-configured
provider; missing configuration/resources/capability is a recorded failure, never
a fixture success. DISABLED records explicit refusal. Existing Phase 4 routes keep
their own documented routing/fallback behavior; this strict mode is explicit.

Private INFERENCE_CONFIG_FILE selects text/vision; INFERENCE_EMBEDDING_CONFIG_FILE
selects embeddings. Both use ModelConfig: model_id, runtime OPENAI_COMPATIBLE,
base_url, declared capabilities, fingerprint, read-only artifact_path, license,
version, dimension, context_window, quantization, estimated_memory_mib,
resource_approved and backend. JSON is bounded to 16 KB. Local paths/endpoints and
approval flag never appear in public inventory. Artifact SHA-256 must match the
configured file (max 2 GiB); verification is cached by path/size/mtime. This is not
cryptographic attestation of a runtime's internal model selection/upstream behavior.
The operator and local runtime remain trusted. Ollama's existing /v1 compatibility
surface is reused. A separately approved private host environment runs the minimal
CPU embedding bridge; ML frameworks are not dependencies of the application image.

A fresh operator host attestation is required (INFERENCE_HOST_PREFLIGHT_AT Unix
seconds, INFERENCE_HOST_SWAP_MIB, INFERENCE_HOST_FREE_GIB); missing/stale values fail
closed. Local disk must also have 5 GiB headroom, host swap <2 GiB, declared model
memory <=2048 MiB. Attestations are operator configuration, not client claims or a
replacement for live host inspection. One process-wide generation/embedding slot,
zero pending queue (immediate refusal when busy), 8-second deadline, byte bounds,
loopback/Docker-host allowlist, no proxy/redirect, no retries. Async cancellation
closes the transport before releasing admission. Managed residency explicitly starts/releases task-owned model processes with
verified sequential termination and expiring leases. Acquisition/startup is bounded
separately from the eight-second inference scope. Inference is nonstreaming; no
streaming TTFT or energy measurement is claimed. Server readiness and weight-load
latency remain distinct timing scopes.

Typed structured outputs reuse Phase 2/3/5 schemas. Additional fields/tool calls
are rejected. Local output is untrusted; independent Planner/Critic/action policy
still owns tool permission and approval. Strict routed agents reuse Kernel plugins;
strict proactive drafting reuses Phase 4 preparation and Phase 3 canonical hashes.
The new /inference/agents and /inference/proactive endpoints select modes explicitly.
Existing fixture-only event workers are unchanged and never gain approval rights.

MemoryService remains owner/lifecycle/privacy/time authority. HYBRID keeps RRF
sum(1/(60+rank)); LEXICAL skips embedding entirely; SEMANTIC uses only the selected
namespace. Real embeddings have a model/version/dimension/fingerprint-derived
namespace, finite normalized vectors and bounded batches (10). Old fixture vectors
are not overwritten. EmbeddingVersion stores the mapping and creation timestamp;
MemoryEmbedding.created_at supplies per-vector indexing time. ReindexJob owns a
fixed task and upper UUID bound, private mode, per-batch cursor and processed-row
count. Explicit step calls lock owner/job, recheck eligibility, write at most ten
vectors and commit the cursor together. Failure rolls back that batch, marks a
safe error and permits explicit resume with the same namespace. DONE retries are
no-ops. New records/corrections outside the captured scan need another job; this
is not a globally frozen database snapshot or automatic re-embedding daemon.

Grounding retrieves bounded owned memory plus up to four persisted owned visual
observations. IDs, provenance and retrieval timestamps stay attached. Evidence is
untrusted source data; no text becomes instructions/tools. Output is an extractive
list of evidence UUID/exact quote pairs, or abstention. Unknown IDs/changed quotes
are refused. Conflicting structured subject/predicate facts require abstention.
Memory eligibility is checked again after generation. Citation validity does not
prove contextual relevance or real-world truth. No free-form answer is silently
"repaired" into an authorized action. Historical model content is not replayed on
retry: only original metadata is returned. Queries/completions are not persisted
by InferenceRun; Phase 4 retains its documented transient exact-result cache.

The optional local vision transport reads only owned, verified normalized media
through MediaIngestionService, caps image payload at 2 MB, and sends an inline
image to the allowlisted local endpoint. PerceptionOrchestrator persists LOCAL_VLM
provenance separately from FIXTURE_VLM; no confidence is treated as calibrated.
InferenceRun links perception ID to configured artifact fingerprint and metadata.
CLIP/DINOv2/SAM continue using existing local-files-only interfaces. No real vision
model has been configured or executed. Visual memories still require confirmation.

Migration 0011 adds inference_models (safe catalog snapshots), inference_runs
(owned request intent/status/metadata), embedding_versions and reindex_jobs. It
reuses ModelCall for generation accounting rather than duplicating call records.
RUNNING requests become FAILED/APPLICATION_RESTARTED on single-process startup;
READY reindex jobs retain their last committed cursor for explicit resumption.
No distributed recovery claim. Catalog snapshots are not an installation registry
or a proof that an external runtime loaded a model. Loaded/last-health values are
not invented. Public model metadata is read-only server configuration.

/inference shows modes, model/resource status, approval-needed download estimates,
owned task controls and actual persisted latency/tokens or UNKNOWN. Benchmark
labels/metrics use recorded runs, not GPU/quality claims. The standalone benchmark
script defaults to LOCAL_REAL and refuses without REAL_MODEL_TESTS=1; fixture mode
is explicit. It measures bounded HTTP samples, not cold model load or TTFT.
Separate retrieval-v1 data evaluates actual PostgreSQL ranking; positive denominators
are five, no-answer case has no positive metric denominator. Hash-vector results
are fixture infrastructure measurements. Real model quality remains NOT EVALUATED.
Hard safety regressions are independent of relevance averages. No LLM judge runs.

New routes under /api/v1/inference: GET models, health, runs, runs/{id}, reindex,
evaluation; POST generate, agents, proactive, reindex, reindex/{id}/step. The
operator-only evaluation uses the existing isolated temporary-schema mechanism.
No API accepts URLs, paths, model weights, role grants or arbitrary code. Prior
Phase 8 auth/device/approval/outbox boundaries and Kubernetes qualifications remain.
# October 19 offline grounding correction

Later October 19: optional private `grounded_generation_contract=SELECTION_V1`
adds an internal GROUNDED_SELECTION wire contract. The model receives indexed
structured facts and returns an index plus an answer value, or explicit abstention.
Only after independently verifying selection, exact value, structured support and
current source/privacy may the application attach the existing UUID/full quote.
Public claims/abstain/extractive answer remain compatible; response carries the
verified model answer, and citation_origin identifies application-derived citations.
The legacy EXTRACTIVE_V1 remains default. Subsequent approved execution passed the
positive and conditional insufficiency cases, followed by final local qualification.
The [frozen proposal](phase-9-selection-acceptance-proposal.md) remains historical;
its scoped approval is closed. No automatic future activation is authorized.

LOCAL_REAL grounding now declares a narrow deterministic support subset: explicitly
named subject cuisine/beverage preference questions and their conjunction. Exact
structured subject/predicate/value/text agreement establishes support within that
subset; retrieval scores alone do not. Arbitrary/first-person/visual questions
receive no asserted supporting context. The model may abstain on every question.
FIXTURE remains the existing replay contract. This is not general semantic RAG.

Bounded selection retains original IDs/full text and server-side provenance,
skips unrelated or oversized items without truncating quotes, and preserves
conflict checks across the full retrieved set. A conservative pinned private
Qwen2/ChatML budget profile includes system/framing/user/output exposure. Unknown
profiles fail closed; it is not a generic tokenizer or a runtime authorization.

Final acceptance validates all retrieved and actually supplied sources, including
visual owner/task/run/processor/privacy bindings and memory content/time/lifecycle.
The owner mutation lock and source-row locks remain held through terminal DONE
commit. This serializes cooperating application mutations, not arbitrary privileged
database writers or changes after commit. Newly visible conflicting facts require
abstention. The unchanged schema describes extractive quotes rather than a separate
freeform answer; exact citation validation never establishes general factuality.

See [offline plan](phase-9-grounding-correction-plan.md) and the
[unapproved acceptance proposal](phase-9-grounding-acceptance-proposal.md).
