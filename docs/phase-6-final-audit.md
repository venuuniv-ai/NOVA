# NOVA Phase 6 final audit

Date: October 14, 2026 (America/New_York).

**Disposition: PASS within the documented deterministic local/fixture scope.
Remaining Phase 6 blockers: none identified. REAL EMBEDDING MODEL NOT CONFIGURED.**
Fixture embeddings exercise persistence, isolation and rank fusion; they are not
a real semantic model. Real CLIP, DINOv2, SAM and VLM inference remain unconfigured
and were not exercised. Phase 7 was not started.

## Baseline and compatibility audit

The workspace began clean on main at the Phase 5 checkpoint
`8c5e2b80a305779be1723ddded750424064ff30e`. README, architecture and Phase 2–5
architecture/audit documents, intelligence/kernel/fixture/perception/routing/
proactive modules, migrations, task ownership, frontend guards and tests were
reviewed before implementation. MemoryPlugin previously read two hard-coded
DemoFixtureRepository preferences: Sarah → Italian and dinner after 6 PM. There
was no persistent memory lifecycle, vector storage or correction interface.

Both preferences now have stable PostgreSQL UUIDs and FIXTURE origin/explicitness.
Their source references and wording preserve existing dinner acceptance. Seeding
does not resurrect deleted/superseded fixture memories. The old repository methods
remain a compatibility reference; registered kernel tools now use MemoryService.
Legacy `explicit_preference` provenance describes an explicit fixture annotation;
it does not turn a fixture into a USER_EXPLICIT memory.

## Architecture and requested report

Browser → Next.js same-origin gateway → FastAPI → owned MemoryService → PostgreSQL.
Policy controls candidate lifecycle before embedding. Eligibility filters precede
independent structured/full-text/vector rankings and RRF fusion. Read-only kernel
MemoryPlugin supplies typed MemoryHit context to MemoryAgent, Planner and Critic.
Redis does not own memory state. See [architecture](phase-6-architecture.md),
[lifecycle/provenance ADR](adr/0008-memory-lifecycle-and-provenance.md) and
[retrieval ADR](adr/0009-memory-hybrid-retrieval-and-pgvector.md).

| Requested item | Implemented behavior / verified boundary |
| --- | --- |
| 1. Memory architecture | Policy-managed PostgreSQL records, embeddings, mutation claims, lifecycle audits and retrieval snapshots; no parallel task system |
| 2. Fixture compatibility | Stable FIXTURE seeds preserve Sarah/Italian and dinner-after-6 behavior; all prior tests retained |
| 3. Types | PREFERENCE, FACT, EPISODIC, TASK_CONTEXT with bounded structured predicates |
| 4. Explicit vs inferred | Safe USER_EXPLICIT stores; all inferred personal candidates require confirmation; confirmation retains inferred origin |
| 5. Visual boundary | Owned coffee-cup observation creates only a possible preference, PENDING_CONFIRMATION; no automatic belief or ownership/employment inference |
| 6. Candidate policy | STORE, ASK_CONFIRMATION, REJECT, TASK_ONLY; server chooses lifecycle; no model-generated inference call is implemented |
| 7. Provenance | Explicit statement, fixture, linked correction, owned visual observation/perception, agent run or task event references; immutable origin |
| 8. Privacy/scope | Server-owned user, USER/TASK scope, owned task checks, PERSONAL minimum floor, privacy ceiling; only local embedding transport |
| 9. Temporal validity | Timezone-aware validity; immediate retrieval exclusion outside bounds; lazy EXPIRED state/audit |
| 10. Contradictions | Same subject/predicate/scope/task plus different active value asks confirmation; narrow structured logic |
| 11. Correction | New USER_CORRECTION record linked by supersedes_id; predecessor SUPERSEDED; no history overwrite |
| 12. Deletion | Soft DELETED immediately excludes record/embedding from subsequent searches; audit/history retained |
| 13. pgvector | Actual vector extension 0.8.7 and VECTOR column, dimension check, exact cosine search; PostgreSQL 17 Alpine base/volume preserved |
| 14. Fixture embeddings | Deterministic normalized 32-dimensional token-hash vectors, fixture-token-hash-v1, simulation=true; NOT A REAL SEMANTIC MODEL |
| 15. Optional adapter | Disabled bounded local OpenAI-compatible /embeddings HTTPX adapter; model/dimension/finite-vector validation, no proxies/redirects/cloud fallback |
| 16. Availability | No configured embedding model/endpoint; no model download, runtime launch or ML stack installation; existing text-model cache untouched |
| 17. Structured retrieval | User/task/type/subject/predicate/state/privacy/time filtering and separate structured ranking |
| 18. Lexical retrieval | Actual PostgreSQL simple-dictionary full-text matching with ts_rank_cd |
| 19. Vector retrieval | Actual pgvector cosine operator within provider/model/dimension namespace; fixture similarity is not truth confidence |
| 20. Hybrid retrieval | Independent source rankings fused by sum(1/(60+rank)); deterministic UUID tie break |
| 21. Explainability | Typed source ranks, fused rank/score, similarity, namespace, provenance and safe reason codes; bounded historical snapshots |
| 22. Agent integration | Registered read-only MemoryPlugin uses MemoryService and existing capability allowlists; bounded typed hits; Critic checks ownership/lifecycle/confirmation |
| 23. Cross-task personalization | New dinner task retrieves explicit preference; another new task receives the Japanese correction |
| 24. Continuity | Original task remains the same UUID through Desktop → Wearable → Mobile and refresh/restart |
| 25. HITL | Memory cannot approve/execute; Phase 3 canonical approval hashes and adapters preserved; acceptance proposal remains PENDING_APPROVAL |
| 26. Migration | 0006_memory_personalization adds five tables; isolated downgrade/upgrade passes; application remains forward-only |
| 27. APIs | Twelve versioned memory routes below; schema validation, owned idempotency and useful 409/422 responses |
| 28. UI | /memory, actual overview counts, lifecycle/provenance cards, confirmation/edit/reject/correct/delete, history, retrieval explorer, Command Center and Task Detail context |
| 29. Tests added | 70 backend cases and seven browser tests, plus an eight-case defined retrieval fixture |
| 30. Backend total | 322 passed: 252 retained + 70 Phase 6 |
| 31. Browser total | 39 passed: 32 retained + seven new; retries=0 |
| 32. Evaluation | Fixture-system Recall@5=1.0 and MRR=1.0 on four positive cases; four exclusion/isolation cases pass; no general semantic quality claim |
| 33. Acceptance | Full script and browser acceptance passed against real backend/DB state |
| 34. Restart | Phase 6 IDs/lifecycles/embeddings/history retained; representative Phases 1–5 passed; retrieval works with Redis stopped |
| 35. Adversarial review | Confirmed findings fixed and regression-tested; details below; no remaining identified blocker |
| 36. Spend | Required external API/infrastructure spend $0; local compute/electricity not priced |
| 37. Limitations | Single-user unauthenticated local demo, heuristic policy, exact bounded search, soft-delete retention; details below |
| 38. Files | 46 changed/new text files: 24 modified, 22 additions; manifest below |
| 39. Git | main; same five checkpoint commits; empty index; Phase 6 unstaged/untracked; no commit/push/remote |
| 40. Blockers | None identified within the tested deterministic local scope; real embeddings remain optional and unverified |

## Database, lifecycle and API

Migration adds memory_records, memory_embeddings, memory_audits, memory_mutations
and memory_retrievals. UUIDs/FKs, bounded text, timezone-aware timestamps, state/
scope/confidence/validity checks, unique owned mutation keys and embedding namespaces
enforce core invariants. Embeddings are VECTOR, not JSONB. Retrieval snapshots
contain bounded typed hits and query hashes, without query text or vectors.

User-row and record locks serialize duplicate creation, contradiction handling,
correction, confirm/reject and delete/read races. Exact key retries return the
original result; changed operation/payload/identity returns 409. A read ordered
before deletion may contain its earlier snapshot; reads after committed deletion
exclude it. Confirmation of a conflicting value requires correcting the active
record instead of silently replacing truth. Edited confirmation creates a linked
record while preserving inferred provenance. No autonomous consolidation runs;
canonical deduplication, current successors and expiration provide bounded
deterministic consolidation.

| Method | Route under /api/v1 |
| --- | --- |
| POST / GET | /memory |
| GET | /memory/candidates |
| POST | /memory/candidates/visual |
| POST | /memory/search |
| GET | /memory/{id} |
| GET | /memory/{id}/history |
| POST | /memory/{id}/correct |
| DELETE | /memory/{id} (JSON idempotency key body) |
| POST | /memory/candidates/{id}/confirm |
| POST | /memory/candidates/{id}/reject |
| GET | /tasks/{id}/memory |

Public clients cannot set user, status, origin authority, confidence, embedding,
source/audit authority or arbitrary supersession links. Internal inferred
candidates require owned persisted source evidence. No provider-generated memory
inference is invoked; a future such path must use Phase 4 routing before policy.
Memory text remains data and cannot expand kernel tool permissions or action rights.

## Actual validation

| Executed check | Final result |
| --- | --- |
| Full PostgreSQL-backed pytest in rebuilt backend-tests image | **322 passed**, 14.79 seconds |
| Separate Phase 6/adversarial suite | **70 passed** |
| Defined eight-case fixture retrieval evaluation | Recall@5 **1.0**, MRR **1.0**; four negative cases pass |
| Backend ruff check / format --check | Passed; 74 Python files formatted |
| Backend pip check | No broken requirements |
| Frontend lint / TypeScript validation | Passed |
| NEXT_TELEMETRY_DISABLED=1 npm run build | Passed; /memory included |
| npm audit --audit-level=high | Zero reported vulnerabilities |
| PostgreSQL/pgvector, backend, backend-tests, frontend Docker builds | Passed |
| docker compose config --quiet | Passed |
| Entire Chromium suite, retries=0 | **39 passed**, 30.4 seconds |
| 390px responsive check and screenshot inspection | No horizontal overflow; actual fixture disclosure/ranks visible |
| Isolated Alembic downgrade 0005, upgrade head, check | Passed; no schema drift |
| Application Alembic current / check | 0006_memory_personalization (head); no new operations |
| Application SQL vector extension / acceptance embeddings | 0.8.7; three persisted 32-dimensional fixture vectors |
| py_compile scripts/acceptance_phase6.py | Passed |
| Phase 6 acceptance and restart verification | Passed; same IDs before/after restart |
| Representative Phases 1–5 and historical Phase 4 key replay | Passed after restart |
| Memory retrieval with Redis stopped | Passed; no authoritative memory dependency on Redis |
| git diff --check | Passed |

Full final backend command:

```sh
docker compose --profile test run --rm backend-tests sh -c \
  'alembic downgrade 0005_multimodal_perception && alembic upgrade head && alembic check && pytest -q && ruff check . && ruff format --check . && pip check'
```

The round trip used the isolated ephemeral test database only. The application
database was never downgraded. Final tests used rebuilt images; native frontend
compilation was also executed. Final browser suite ran the production Compose
frontend with real API state. Held-response tests delay delivery of actual
backend responses, without fabricated task data. The final kernel description
change only corrects preference provenance wording; backend checks were repeated
against the resulting image. Test retry configuration remained zero.

## Acceptance and persistence evidence

Final Phase 6 task: `778aaaf3-b102-47ba-93ad-2bd858099660`.

- Explicit Italian memory: `2b230009-7e6c-48fa-992a-1427fbc86742`, now SUPERSEDED.
- Japanese correction: `ad71c5ab-2daa-412f-a830-f11b8372a5f7`, now DELETED.
- Independent active deadline fact: `04d353a3-22d3-48a2-9a0f-1a1b97931a1a`.
- Unconfirmed visual candidate: `e2d5c9aa-be6b-47aa-b8a4-03ded273e2ac`.
- Perception: `5660a245-1f31-4659-bd90-7301e8be2539`.
- Media: `e656f2fd-2708-4fa7-ae96-141e57775b9e`.
- Pending proposal: `e6a157d5-7990-4ae9-bc61-1493af01a00c`.

The preference was created before a NEW dinner task. Planner captured its typed
USER_EXPLICIT / USER MemoryHit, source ranks and memory-ID constraint provenance.
Critic passed. An owned Wearable coffee-cup observation produced a pending
candidate, excluded from established preference retrieval. Correction made a new
active Japanese memory; another new dinner task retrieved it and completed.
Deletion excluded both inactive preference records from new searches. Historical
plan context retains the original explanation. The original task continued to
Mobile; its proposal has no approval or execution.

After backend/frontend/PostgreSQL restart, --verify-task passed with exactly the
same reported IDs, active fact, pending candidate, correction/deletion history,
historical plan, media/perception and pending proposal. SQL confirmed the original,
corrected and active memories' fixture embeddings survived; inactive embeddings
remain physically retained but ineligible. Stopping Redis separately did not
prevent active memory retrieval. No application volume was deleted or flushed.

Representative existing records also passed after restart:

| Phase | Task | Preserved evidence |
| --- | --- | --- |
| 5 | 85f85ceb-9129-4ea3-942e-29f34fe4516f | Media hash, five observations, plan, vision call, pending proposal, Mobile |
| 4 | 8b85f8dd-cdf7-470f-a7f6-7880cd0a39c8 | Seven requests/traces, decisions, pending proposal; historical key replay |
| 3 | 2efed4f2-1ecf-4e4f-8b56-eca91c910ec0 | Approval/execution hashes, simulation receipt, four audits, Mobile |
| 2 | 495411fd-b1ad-4890-90e3-0c679b7078e8 | Six runs, five tools, Critic PASS, plan, Mobile |
| 1 | 0251cb6e-c92c-4aee-acfa-9ecf7fd4a80e | Same task, Mobile, three continuity events |

## Adversarial review and resolved findings

The separate review covered forged client/provider authority, owned source IDs,
visual auto-storage, unconfirmed trust, instruction-like memory/query content,
credentials/profiling, user/task/privacy isolation, lifecycle eligibility,
mutation/correction/candidate races, namespace/dimension/nonfinite vectors,
local URL/output/error handling, logging, planner/Critic trust, HITL and stale UI.
The temporal regression also races expiry against correction: expired data cannot
be corrected into an active successor in either serialization order.
The focused Phase 6 suite reran all 70 new backend cases after fixes.

- **P6-A01 — Fixture seed identity, CLOSED.** An initial record identity was assigned
  after embedding/audit construction. Assign the stable UUID before dependent
  writes. Persistence and non-resurrection regressions pass.
- **P6-A02 — Rejected sensitive content retention, CLOSED.** Initial rejection kept
  the unsafe value despite excluding it from embeddings. Store a policy tombstone
  in record and replay response. Secret/profiling persistence/log regressions pass.
- **P6-A03 — Valid acknowledgment lost during polling, CLOSED.** Same-task refresh
  temporarily disabled mutations and could also discard an authorized response.
  Separate selected identity from current permission for acknowledgment handling
  across task-keyed workspaces. Held-response regression and old switching tests pass.
- **P6-A04 — Restored approval retry readiness, CLOSED.** Retry could appear enabled
  before its owned proposal snapshot loaded, while the handler refused it. Disable
  retry until that snapshot exists. Delayed-read regression and old Phase 3 retry pass.
- **P6-V01 — Dinner-tomorrow calendar compatibility, CLOSED.** New flagship wording
  requested calendar context but the fixture matcher recognized only meeting text.
  Recognize tomorrow as well; new-task planning and prior dinner acceptance pass.

Early lint/type/format findings were corrected. Intermediate browser runs exposed
the acknowledgment/readiness findings above; no earlier failure is treated as a
pass. A later memory test encountered an active preference left by an earlier
duplicate-click test: contradiction policy correctly returned pending. That test
now deletes its own generated preference. Another assertion matched multiple
retained rejected coffee records; it now asserts the specific candidate UUID.
The final complete suite passed 39/39 without hidden retries. Clearly generated
test records were cleaned through audited API deletion; unrelated user data was
not removed. Final acceptance ran after browser checks to avoid shared candidate
deduplication changing its pending status.

## Evaluation, cost and limits

The versioned eight-case fixture set defines exact preference, paraphrased query,
task-scope isolation, superseded, deleted, expired, contradictory candidate and
cross-user cases. Four positive cases calculate Recall@5 and MRR from expected
IDs; four negative cases assert exclusion. Both metrics are 1.0 in this defined
fixture system. Structured filtering and deterministic hash embeddings contribute
to these results; they do not benchmark semantic models or unseen paraphrases.

Required external API/infrastructure spend: **$0**. pgvector is built from a
SHA-256-verified upstream source archive, not model weights. No paid embedding,
cloud service, managed vector database, inference download/runtime launch or ML
stack installation occurred. Optional local embeddings use an existing configured
endpoint only; MockTransport tests prove protocol behavior, not real inference.
Real CLIP, DINOv2, SAM and VLM inference remain unconfigured and unexercised.

This is an unauthenticated single-user local demonstration with loopback ports.
Policy/profiling/injection markers and structured contradictions are narrow
heuristics, not comprehensive PII detection or privacy/security certification.
No penetration test, Python advisory scan or container vulnerability scan was
performed; npm audit and pip compatibility do not certify security.

Soft deletion keeps local plaintext content/embeddings and historical retrieval
snapshots; physical erasure, encryption and retention automation are absent.
as_of_time filters currently ACTIVE records rather than replaying historical
lifecycle. Lists cap at 100, eligible ranking candidates at 200, hits at 20;
there is no UI pagination or ANN index. User locking serializes memory work and
can span bounded optional local embedding I/O. A trusted local runtime's upstream
behavior cannot be attested. No general model-generated candidate pipeline or
automatic namespace re-embedding is implemented. Redis outage was exercised,
not Redis data deletion. No later-phase learning, external accounts, telemetry,
deployment infrastructure or Phase 7 work was added.

## Files, Git and local operation

46 Phase 6 files: 24 tracked modifications and 22 additions. All candidate files
are bounded UTF-8 source/configuration/test/documentation text; largest is the
approximately 30 KB backend memory test file. Credential/private-key/token scans
found no matches. `.env.example` contains disabled local settings only; no actual
.env, personal images, weights, screenshots, caches, dependencies, database files
or runtime media enter the change set. Existing ignore rules were checked for
test-results, media_data, model weights, node_modules, bytecode and actual .env.
Generated browser screenshots were inspected in ignored test-results.

```text
.env.example
README.md
backend/app/config.py
backend/app/fixtures/personal_context.py
backend/app/intelligence/agents.py
backend/app/intelligence/contracts.py
backend/app/intelligence/orchestrator.py
backend/app/intelligence/plugins.py
backend/app/intelligence/policy.py
backend/app/intelligence/provider.py
backend/app/logging.py
backend/app/main.py
backend/app/memory/__init__.py
backend/app/memory/api.py
backend/app/memory/contracts.py
backend/app/memory/embeddings.py
backend/app/memory/models.py
backend/app/memory/plugin.py
backend/app/memory/policy.py
backend/app/memory/service.py
backend/app/seed.py
backend/migrations/env.py
backend/migrations/versions/0006_memory_personalization_memory_personalization.py
backend/tests/conftest.py
backend/tests/fixtures/memory_retrieval_cases.json
backend/tests/test_memory.py
compose.yaml
docs/adr/0008-memory-lifecycle-and-provenance.md
docs/adr/0009-memory-hybrid-retrieval-and-pgvector.md
docs/architecture.md
docs/phase-6-architecture.md
docs/phase-6-final-audit.md
frontend/app/api/[...path]/route.ts
frontend/app/globals.css
frontend/app/memory/page.tsx
frontend/components/approval-workspace.tsx
frontend/components/intelligence-workspace.tsx
frontend/components/memory-workspace.tsx
frontend/components/model-workspace.tsx
frontend/components/nova-workspace.tsx
frontend/components/perception-workspace.tsx
frontend/lib/memory.ts
frontend/styles/memory.css
frontend/tests/memory.spec.ts
infrastructure/postgres/Dockerfile
scripts/acceptance_phase6.py
```

Git branch main; HEAD remains `8c5e2b80a305779be1723ddded750424064ff30e`.
All five Phase 1–5 checkpoint hashes remain unchanged. Index empty; Phase 6 files
are unstaged/untracked for review. No commit/amendment, push or remote configuration.
Acceptance/browser checks create real demo records; backend tests use only the
isolated test database. After validation, containers are stopped with application
PostgreSQL/media/Redis volumes preserved.

```sh
docker compose up --build -d --wait
python3 scripts/acceptance_phase6.py
python3 scripts/acceptance_phase6.py --verify-task 778aaaf3-b102-47ba-93ad-2bd858099660
```

Open http://localhost:3000/memory and http://localhost:8000/docs. The acceptance
script creates and deletes its preference as part of the demonstrated lifecycle.

**Final result: Phase 6 accepted within deterministic local scope. No remaining
identified Phase 6 blocker. No real embedding inference or Phase 7 work.**
