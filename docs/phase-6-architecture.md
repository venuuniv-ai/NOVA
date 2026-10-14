# Phase 6: controlled persistent memory and hybrid retrieval

Extends checkpoint `8c5e2b80a305779be1723ddded750424064ff30e`, without replacing
tasks, Semantic Kernel, model routing, visual evidence or human approval.

## Baseline memory audit and compatibility

Before Phase 6, MemoryPlugin delegated directly to DemoFixtureRepository:
Sarah prefers Italian and the demo user prefers dinner after 6 PM. Those were
static fixture annotations, not persisted personal memory. No lifecycle,
expiration, correction, ownership-filtered retrieval or vector storage existed.
The repository fixture methods remain a pure compatibility reference; the
registered MemoryPlugin now reads MemoryService instead.

Two stable fixture UUIDs are seeded into PostgreSQL with origin FIXTURE and
explicitness FIXTURE. Seed never resurrects deleted/superseded records. Source
references and original wording remain compatible with the Phase 2 dinner test.
Legacy `explicit_preference` means an explicit fixture annotation, not an actual
USER_EXPLICIT statement; the MemoryHit retains the true FIXTURE origin. New user
or confirmed inferred records carry PERSISTENT_MEMORY provenance and memory IDs.

## Architecture and policy

User statement / owned observation / owned agent or task evidence → typed
candidate → deterministic MemoryPolicy → ACTIVE, PENDING_CONFIRMATION or REJECTED
record → embedding only when ACTIVE → owned eligibility filters → independent
structured/lexical/vector rankings → reciprocal rank fusion → typed MemoryHit
→ read-only kernel MemoryPlugin → MemoryAgent → Context/Planner/Critic.

PREFERENCE, FACT, EPISODIC and TASK_CONTEXT support narrow structured predicates:
preferred_cuisine, preferred_beverage, dining_preference, dinner_time,
project_deadline, task_note, task_outcome. These are application demonstrations,
not general knowledge logic or universal natural-language contradiction detection.

Public create is an explicit local user statement. The server assigns user,
origin, explicitness, confidence, status, timestamps, source reference and policy.
Clients cannot supply authority, embedding vectors/provider, arbitrary source,
supersedes identity or audit fields. Source candidates are a typed internal
contract; model output cannot include STORE/ACTIVE/approval authority. An
AGENT_INFERRED candidate must reference an owned AgentRun, TASK_OUTCOME an owned
TaskEvent, and VISUAL_OBSERVATION an owned observation. No model-generated
candidate inference is invoked in Phase 6; a future inference path must use
ModelRouter before handing its untrusted candidate to this policy.

Explicit safe records STORE. Task-scoped explicit context is TASK_ONLY. All
inferred/visual/task-outcome personal candidates ASK_CONFIRMATION regardless of
confidence. Same subject/predicate/scope/task with a different active value asks
confirmation; explicit correction is the only automatic supersession path.
Unsafe instruction/credential/profiling markers REJECT. Rejected payload text
is replaced by a policy tombstone, never embedded; keys/hashes preserve retry
identity without retaining that value in mutation responses. This narrow policy
is not comprehensive secret/PII detection or sensitive-attribute inference.

The public visual candidate operation binds an actual coffee_cup_present
observation to a possible coffee-related preference. It never writes an ACTIVE
preference automatically, never infers ownership/employment and never grants
action authority. A human confirmation retains VISUAL_OBSERVATION / INFERRED
origin, with confirmed=true; it never becomes USER_EXPLICIT. Edited confirmation
creates a linked new record, preserving origin and the old record's history.

## Lifecycle, scope and concurrency

Memory identity/content is stable; status may become ACTIVE, PENDING_CONFIRMATION,
SUPERSEDED, DELETED, EXPIRED or REJECTED. Correction creates a new USER_CORRECTION
record and marks the old record SUPERSEDED. A successor links to its predecessor;
clients cannot create arbitrary or circular supersession. Deleted or expired
memories cannot be corrected/confirmed, and superseded memories cannot be deleted
as though still active. Soft deletion keeps historical audit content; it is not
a physical erasure feature.

Equivalent canonical structured values, subject, predicate, type, scope, privacy
and validity deduplicate within their origin. Normalization covers case and
whitespace, not universal paraphrase equivalence. Deterministic consolidation
selects active successors and excludes expired context; no autonomous rewriting
agent or background LLM runs. Candidates remain separate from established beliefs.

USER memories support other tasks for the same owner. TASK memories require an
owned task UUID and cannot appear in another task. PERSONAL is the minimum
storage privacy floor; SENSITIVE_LOCAL_ONLY restricts normal search by ceiling.
All embedding transport is local-only in Phase 6, including sensitive content;
there is no cloud provider or paid embedding path.

valid_from/valid_until use timezone-aware timestamps. Expired values are excluded
from searches immediately by validity, and list/mutation operations lazily commit
EXPIRED state and an audit event. as_of_time evaluates bounds on currently ACTIVE
records; it is not full historical state replay and cannot reactivate deletion
or supersession. Validity is explicit; memories with no expiry remain user-managed.

Memory mutations require idempotency. Unique owned keys bind operation, ID and
payload; exact retry returns the original response, changed intent returns 409.
The service locks the owned User row to serialize canonical deduplication,
contradictions, confirmations, corrections, deletion and reads. Record locks
protect lifecycle transitions. Retrieval sees a consistent owned lifecycle cut;
a result that linearizes before deletion may still contain that earlier snapshot.
After committed deletion, new retrieval cannot return the embedding.

This simple lock deliberately serializes one user's memory work. Optional local
embedding calls can hold that transaction for their bounded HTTP operation; this
is a local demo, not a distributed high-throughput memory service. No Redis state
owns memory, embeddings or mutation decisions.

## pgvector and embedding namespaces

The PostgreSQL image extends the existing postgres:17-alpine base with pgvector
0.8.7, built from a SHA-256 verified upstream source archive. The original named
application volume and PostgreSQL major/libc family remain in place. The isolated
test DB uses the same extension image with ephemeral data. No managed vector DB,
new cloud storage or Python ML stack is required.

Migration 0006_memory_personalization enables vector and adds memory_records,
memory_embeddings, memory_audits, memory_mutations and memory_retrievals. UUIDs,
FKs, lifecycle/scope/confidence/validity checks, key/namespace uniqueness and
owned lookup indexes enforce core invariants. Embedding uses the PostgreSQL
VECTOR type with vector_dims equal to its declared dimension. Vectors do not
enter JSONB. A small SQLAlchemy extension type handles binding/reflection, without
installing a model SDK. Migration downgrade drops only Phase 6 tables and leaves
the shared extension installed; application data is never downgraded.

FixtureEmbeddingProvider deterministically hashes tokens into a normalized
32-dimensional vector. It is FIXTURE EMBEDDING / NOT A REAL SEMANTIC MODEL, with
no tokenizer/model probability or semantic quality claim. Storage records
provider, model, dimension, simulation and time. Namespaces are never mixed in
vector retrieval. Exact pgvector cosine search is sufficient for this small demo;
no ANN index is added for portfolio terminology.

LocalEmbeddingProvider implements optional bounded OpenAI-compatible /embeddings
transport, model identity, finite/nonzero vector and dimension validation,
loopback/Docker-host URL restrictions, no redirects or ambient proxies, and safe
normalized failures. Defaults disable it. No credential is required or exampled.
Missing/invalid enabled providers fail closed, without switching model namespaces
or silently downloading weights. Existing fixture records have fixture embeddings;
changing providers does not automatically re-embed them. Structured/lexical
retrieval can still use them; semantic matching requires the configured namespace.

No real embedding endpoint/model was configured or exercised. Host caches held
only an existing qwen2.5:1.5b text model, left untouched; no embedding weights or
sentence-transformer/torch/transformers stack was installed. A trusted local
runtime's upstream behavior cannot be attested; operators must configure a
truly local embedding endpoint. Local compute/electricity is not priced.

## Hybrid retrieval and explanation

MemoryQuery carries task, text, types, subject/predicate, scope, privacy ceiling,
limit and validity time; owner is server-owned. SQL eligibility first excludes
other users/tasks, deleted/superseded/expired/rejected/pending records and disallowed
privacy. Up to 200 eligible records are considered; results are limited to 20.

Independent source ranks:

- Structured eligibility with explicit subject/predicate/scope filters.
- PostgreSQL simple-dictionary full-text matching and ts_rank_cd.
- Exact pgvector cosine ranking in the configured provider/model/dimension namespace.

RRF score is sum(1/(60+source_rank)), with deterministic UUID tie breaking. It
never averages vector similarity and inference confidence. Hits preserve each
source rank, fused rank/score, actual similarity when used, origin, explicitness,
confidence, source and namespace. Fixture cosine is an infrastructure test value,
not real semantic confidence. JSONB retrieval snapshots contain bounded hits and
query hashes, not query text or vectors. Stored snapshots preserve historical
planner explanation even when a memory later changes; normal retrieval still
excludes its inactive current record.

## Agents, HITL and frontend ownership

KernelRuntime binds the registered read-only MemoryPlugin to server-owned task/
user context. Its existing allowlisted functions use MemoryService, exposing no
mutation tool or arbitrary SQL. Default dinner tool counts remain unchanged.
MemoryOutput/SharedContext carry typed MemoryHit objects alongside compatible
preferences. Facts/episodes/task context remain typed evidence; preferences keep
attributable sources. Planner assumptions distinguish user-controlled memory
from synthetic data; Critic rejects inactive, unconfirmed or foreign memory.
Memory text is data, never a system prompt or new tool permission.

Phase 3 approval policy/canonical hashes/execution adapters are unchanged. Memory
can inform a plan but cannot approve, execute, edit an approved action or authorize
external communication. No real communication is sent.

/memory shows actual counts, source/lifecycle/scope/validity, pending confirmation,
correction/deletion, edited confirmation/rejection, audit history and retrieval
source ranks. Command Center summarizes actual API state. Task Detail includes
memory captured by a recorded plan, explicitly labeled historical, plus current
eligible context. No fake universal relevance percentage or semantic benchmark.

Task-keyed children cancel old reads and guard mutation starts. Request intent
alone is stored locally; records/ranks come from FastAPI. A confirmed browser
overlap found that transient same-task polling could make an authorized response
look stale. Identity ownership is now separate from temporary mutation permission;
acknowledgments apply only to the same selected task, without dropping valid
responses during refresh. This preserves F-01 switching protections.

## APIs, limits and scope

POST /api/v1/memory; GET /memory; GET /memory/{id}; POST /memory/search;
GET /memory/candidates; POST /memory/candidates/visual;
POST /memory/candidates/{id}/confirm or /reject;
POST /memory/{id}/correct; DELETE /memory/{id}; GET /memory/{id}/history;
GET /tasks/{id}/memory. All paths use /api/v1. DELETE carries a JSON key body.

This remains an unauthenticated single-user loopback demo. No production privacy
compliance, perfect PII/contradiction detection, multi-tenant certification,
human-like memory or real embedding quality is claimed. Memory/embeddings and
historical audit snapshots are local plaintext, with no erasure/encryption or
retention automation. Lists are limited to 100 and retrieval candidates to 200.
There is no general learned inference, cloud embedding, real account integration,
background consolidation, bandit, telemetry/deployment stack or Phase 7 feature.

References: [pgvector exact search and installation](https://github.com/pgvector/pgvector),
[pgvector SQL operators](https://github.com/pgvector/pgvector/blob/master/README.md).
