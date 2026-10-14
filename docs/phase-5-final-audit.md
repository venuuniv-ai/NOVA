# NOVA Phase 5 final audit

Date: October 14, 2026 (America/New_York).

**Disposition: PASS within the deterministic local/fixture scope. Remaining
Phase 5 blockers: none identified. Real visual inference is optional and was
not configured or exercised. Phase 6 was not started.**

## Baseline and scope

HEAD remains `5a4cec77641da80f98976ab258f2f18aa011bf0e`, branch main, with the
four Phase 1–4 checkpoints preserved. The working tree began clean. Existing
architecture, task identity, Semantic Kernel plugins, routing/accounting and
human approval were retained. No previous checkpoint was amended, and no
Phase 5 commit, staging, push or remote configuration occurred.

The implementation is perception/context, not image retrieval or image RAG.
No microphone, camera stream, hardware/account integration, automatic visual
memory, cloud vision, vector warehouse, deployment or later-phase feature exists.

## Implemented architecture and responsibilities

MediaIngestionService independently handles bounded upload/decode/sanitization,
SHA-256 binding, private storage and ownership. PerceptionOrchestrator persists
per-processor outcomes and typed observations, optionally invokes a distinct
VisionLanguageProvider through the Phase 4 ModelRouter, and projects bounded
ContextEvidence. VisualReasoningService delegates to the existing real-kernel
Context/Planner/Calendar/Memory/Critic path, then optionally to Phase 3 policy.

Raw media → processor output → observation → contextual interpretation → plan
→ deterministic action policy → explicit human approval remain distinct.
No image/VLM result authorizes execution, changes tool permissions or routing,
modifies approval hashes, or creates personal preferences/permanent memory.
The optional proposal is justified by the unchanged synthetic travel/calendar
scenario, not by an image instruction or a claimed physical location.

## Ingestion, metadata and persistence

JPEG, PNG and WEBP only. Server limits default to 2 MB input, 2048 pixels per
axis, 4 million pixels, 8 MB normalized output. Streamed uploads have an
8-second deadline; the gateway and backend independently enforce byte limits.
Pillow 12.3.0 verifies decoded format/MIME, image framing, dimensions, pixel
count, decoding, animation and bomb/warning conditions. Explicit EXIF header
validation rejects a malformed case that Pillow otherwise ignored.

Orientation is normalized; a fresh RGB image is encoded to PNG. Original bytes,
filename, EXIF/GPS/XMP/ICC/PNG text are discarded and never persisted or logged.
Malformed ICC is stripped without being interpreted. Detectable PNG/JPEG/WEBP
trailing polyglots are rejected; comprehensive polyglot detection is not claimed.

MediaAsset stores UUID owner/task/device links, normalized hash/MIME/dimensions,
byte size, server-owned reference, source, sanitization metadata flag, key and
time. APIs use opaque UUIDs, verify task/user ownership, reject symlink/path
escape and validate stored byte length/hash. Files use private permissions;
runtime remains non-root. Named `media_data` retains normalized images across
backend/frontend restart. Original upload retention is absent.

Migration `0005_multimodal_perception` adds MediaAsset, PerceptionRun,
ProcessorRun, VisualObservation and MediaArtifact, with UUIDs/FKs, task/key and
processor uniqueness, status/dimension checks and indexes. JSONB contains
bounded validated observations/context and warnings; no huge embeddings,
original media or mask arrays. Actual SAM masks use opaque PNG artifact IDs.

Perception advisory locks serialize same-key requests, reject changed payloads
and preserve exact original IDs. Upload task locks protect duplicate insertions.
Processor failures are independent; surviving results with failures/unavailable
enabled processors are PARTIAL. Disabled optional processors are SKIPPED,
without pretending they ran. Startup terminates abandoned RUNNING runs safely.
Completed visual context retains its captured Wearable source after Mobile handoff.

## Fixture and optional real model assessment

FixtureVisionProvider uses a controlled repository-owned 480×300 programmatic
scene and returns four annotations: meeting-room sign, laptop, backpack, cup.
They are FIXTURE_VISION / fixture-vision-v1 / simulation=true / score NONE.
No geometry is fabricated. Arbitrary uploads, including identical pixels,
cannot obtain controlled fixture annotations. The fixture has no personal
metadata; UI distinguishes this from actual metadata removal on uploads.

CLIP adapter supports actual image/text embeddings and cosine similarity.
DINOv2 computes features and retains only processing/shape metadata. SAM supports
center-point segmentation with at most three opaque mask PNGs and actual IOU
scores; it cannot identify semantic objects from masks. All adapters load lazily
from explicit existing local directories with local_files_only, safe tensor
weights and no custom remote code/download fallback. No optional ML stack was
installed. Standard requirements added only the lightweight image decoder.

Host inspection found no Pillow/torch/transformers/open_clip/segment_anything
packages initially; the application/test images now have Pillow, with no torch,
transformers, open_clip or segment_anything. No Hugging Face or torch checkpoint
cache was present. An existing Ollama qwen2.5:1.5b text model cache was found and
left untouched; it does not supply a configured vision model. No configured
inference endpoint was probed or inference runtime launched.

- REAL CLIP NOT CONFIGURED
- REAL DINOV2 NOT CONFIGURED
- REAL SAM NOT CONFIGURED
- REAL VLM NOT CONFIGURED

Optional adapters were validated through offline-loading and processor protocol
tests, including mask artifact persistence. These are protocol tests, not real
model execution, quality assessment, latency benchmarks or detection evidence.
No models/weights, CUDA, torch variant, Ollama runtime or cloud client was installed.

## VLM, routing, confidence and context

FixtureVisionLanguageProvider is a distinct VISION service, fixture-vlm-v1,
explicitly NOT REAL VISUAL INFERENCE. IMAGE requests bind task/user/trace,
media UUID/hash, device, privacy and VISION capability. Existing ModelRouter,
circuit, budget and ModelCall persistence remain authoritative.

Every cloud/external-priced visual route is forbidden in Phase 5, including
fallback and PERSONAL policy opt-in. Sensitive-local-only also bypasses cache.
The permitted controlled fixture yields FIXTURE_VISION_REPLAY; arbitrary uploads
without an eligible real provider fail safely. No image bytes go to cloud.
Text hash compatibility preserves real historical Phase 4 original-key retries.

Observations retain media/hash/source, processor/model, simulation, captured
device, time, UUID and separate score_type. CLIP_COSINE and SAM_IOU are not a
universal confidence scale. Fixture scores are null; no unrelated scores are
averaged. SAM requires actual bound geometry and a nonnegative score; other
processors cannot claim its mask geometry. Extra fields, forged origin, bad
regions and oversized processor outputs are rejected.

ContextEvidence preserves these references and labels data as untrusted.
Fixture interpretation says consistent with a meeting/work environment, never
verified physical location. The existing Context Agent preserves bounded visual
context; Planner records VISUAL_EVIDENCE constraints and Critic checks them
against the captured context. Calendar/memory fixtures keep their provenance.
Visible text/metadata/VLM claims cannot act as system instructions or tool calls.
Memory remains the read-only explicit fixture preference source.

VisualReasoningService serializes request intent. Exact retry reuses execution;
changing the proposal flag with the same key returns 409. Failed or incomplete
intelligence cannot create a new proposal through this path. Phase 3 still
requires explicit human approval of the exact canonical payload, then a separate
execution request. Tests verify refusal before approval, exact hash binding and
SIMULATED delivery / external_message_sent=false after approval.

## APIs and frontend

| Method | API |
| --- | --- |
| GET | /api/v1/perception/processors |
| POST | /api/v1/tasks/{id}/media/fixture |
| POST | /api/v1/tasks/{id}/media |
| GET | /api/v1/tasks/{id}/media |
| GET | /api/v1/tasks/{id}/media/{media_id}/content |
| GET | /api/v1/tasks/{id}/artifacts/{artifact_id}/content |
| POST | /api/v1/tasks/{id}/perception |
| GET | /api/v1/tasks/{id}/perception |
| GET | /api/v1/tasks/{id}/perception/{run_id} |
| POST | /api/v1/tasks/{id}/perception/{run_id}/reason |

/perception presents actual sanitized media, privacy, processor outcomes,
observations/provenance/score semantics, interpretation and reasoning controls.
Only real output geometry creates overlays or mask links. /models shows the
VISION decision and actual persisted call. Command Center and Task Detail show
restrained real visual summaries. No throughput/quality or paid savings is invented.

Task-keyed components cancel obsolete reads, gate mutations through parent
ownership and ignore late acknowledgments. A posting guard prevents duplicate
clicks. Only request intent is stored locally; visual state comes from FastAPI.
Browser tests verify stale A/B/C reads, late POST acknowledgment, duplicate clicks,
refresh with an original perception key, binary upload validation, handoff and
390px layout. The mobile screenshot was generated in ignored test-results and
visually inspected. No horizontal overflow or fixture boxes were present.

## Checks actually executed

72 backend cases and six browser tests were added. All 180 backend and 26
browser tests from Phases 1–4 remain retained. One earlier browser assertion was
scoped to the intended success notice; its continuity coverage remains intact.

| Executed check | Final result |
| --- | --- |
| Rebuilt-image PostgreSQL backend pytest -q | **252 passed: 180 prior + 72 Phase 5** |
| Separate Phase 5 adversarial/contract/protocol suite | **72 passed** |
| ruff check . | Passed |
| ruff format --check . | Passed; 64 Python files already formatted |
| pip check | No broken requirements |
| npm run lint | Passed |
| npm run typecheck | Passed |
| NEXT_TELEMETRY_DISABLED=1 npm run build | Passed |
| npm audit --audit-level=high | Zero reported vulnerabilities |
| Backend, backend-tests, frontend Docker builds | Passed |
| docker compose config --quiet | Passed |
| Entire Chromium suite, retries=0 | **32 passed: 26 prior + 6 Phase 5** |
| Isolated downgrade 0004_model_routing / upgrade head / check | Passed; no drift |
| Application alembic current | 0005_multimodal_perception (head) |
| Application alembic check | No new upgrade operations detected |
| py_compile scripts/acceptance_phase5.py | Passed |
| Phase 5 real local REST acceptance | Passed |
| Phase 5 verification after backend/frontend restart | Passed; identical IDs/hash |
| Phase 4 representative acceptance and actual historical key replay | Passed after restart |
| Phase 3 representative HITL acceptance | Passed after restart |
| Phase 2 representative intelligence acceptance | Passed after restart |
| Original Phase 1 identity/device/events | Passed after restart |
| git diff --check | Passed |

Full final backend command used isolated ephemeral PostgreSQL/test-Redis:

```sh
docker compose --profile test run --rm backend-tests sh -c \
  'alembic downgrade 0004_model_routing && alembic upgrade head && alembic check && pytest -q && ruff check . && ruff format --check . && pip check'
```

Application data was never downgraded. Browser held-response tests delay delivery
of real backend responses, not fabricate backend state. Final suites passed with
zero configured retries. The non-failing Playwright environment-color warning
remains. Python/container advisory scans and penetration testing were not run.

## Acceptance and restart evidence

Task: `85f85ceb-9129-4ea3-942e-29f34fe4516f`.
Media: `2058baaa-49ea-4eab-b14f-b7a1ed76a070`.
Perception: `502ee541-191c-4f1b-92a1-c986a0310aeb`.
Trace: `59b01803-6080-47ba-b031-80698af92d86`.
Pending proposal: `c6d1e65c-b4a3-43df-a9f4-51d8772cc04f`.
Normalized SHA-256: `e8296f8a6b0bd65d73ff47ded1a9eebe61820dd4017220d5d35e30b1a708787f`.

Four fixture object annotations plus one attributed fixture VLM interpretation
persisted with five ContextEvidence references, one VISION ModelCall and a
successful six-stage dinner plan with Critic PASS. The task continued to Mobile
with the same media/run/trace/observation/proposal IDs. Same-key perception retry
created no duplicate run or observations. The application proposal remained
PENDING_APPROVAL, approval=None, execution=None. Approval/execution simulations
were exercised only in isolated backend tests, not on that acceptance proposal.

Restart verification compared every acceptance ID and normalized hash exactly;
the media file remained readable and hash-valid. Original Phase 4 task
8b85f8dd-cdf7-470f-a7f6-7880cd0a39c8 retained its seven calls and pending proposal,
and an original pre-Phase-5 text request key replayed its original trace.
Phase 3 task 2efed4f2-1ecf-4e4f-8b56-eca91c910ec0 retained exact approval/execution
and four audits; Phase 2 task 495411fd-b1ad-4890-90e3-0c679b7078e8 retained six runs,
five tools, Critic PASS and Mobile. Phase 1 task 0251cb6e-c92c-4aee-acfa-9ecf7fd4a80e
retained Mobile and exactly three ordered creation/handoff events.

## Separate adversarial review and resolutions

All findings are preserved here and closed by validation; no historical failure
is erased. Review covered parsers/metadata, ownership, path/opaque mask access,
size/bombs, provenance/scores, cloud escape, duplicates, stale UI, raw logging,
visual memory, HITL, historical replay and restart. The separate 72-case Phase 5
suite passed after corrections; the final full 252/32 suites also passed.

- **P5-A01 — metadata parser, CLOSED:** Pillow silently ignored a malformed
  EXIF header. Added explicit TIFF/EXIF header checks; malformed EXIF regression passes.
- **P5-A02 — score/geometry semantics, CLOSED:** first draft permitted SAM
  negative IOU or missing artifact/region and other processors' geometry.
  Tightened processor-specific constraints; geometry/score regressions pass.
- **P5-A03 — optional processor health, CLOSED:** availability exceptions were
  outside failure isolation. Normalize them to UNAVAILABLE and report surviving
  output as PARTIAL; independent fixture/VLM results remain valid.
- **P5-A04 — historical Phase 4 keys, CLOSED:** new default media fields would
  change text request hashes. Preserve the pre-Phase-5 hash for TEXT and reject
  visual bindings on TEXT. Unit and actual historical-key replay pass after restart.
- **P5-A05 — reasoning intent, CLOSED:** changed proposal intent with the same
  reasoning key needed explicit protection. A serialized owned intent binds
  that flag, rejects conflicts and never surfaces a new draft after failed reasoning.

**P5-V01 — test/UI selectors, CLOSED:** the initial upload test attempted another
file while the control was busy. After adding the wait, it encountered Next.js's
separate alert announcer. Named the Perception error and scoped its assertion.
A broad pre-existing continuity status assertion also collided with independently
loading panels; it now targets the actual success notice. Entire final suite
passes 32/32. No continuity case was removed and retries remain zero.

**P5-V02 — new test contract assumption, CLOSED:** the new explicit simulation
case initially looked for a payload_hash directly on ExecutionRead; the actual
contract places the hash on the associated approval. Corrected the assertion;
approval hash binding and NOT SENT receipt now pass. Initial imports/formatting
were corrected before final checks. No required failed check remains unresolved.

## Cost, security and limitations

Required external API/infrastructure spend: **$0**. No paid API/cloud storage,
managed service, real image upload to external inference, model download or
runtime installation occurred. Existing mandatory Semantic Kernel dependencies
were reinstalled from their pinned snapshot during Docker builds, but their
commercial clients remain unconfigured. Local compute/electricity is not priced.

This remains one unauthenticated local demo user and simulated devices, with
loopback ports and trusted local filesystem/operator configuration. It is not
multi-tenant security, a decoder/model OS sandbox or a comprehensive PII detector.
Real CLIP/DINO/SAM/VLM inference is unverified; only adapter protocols/offline
loading were tested. Optional ML work is bounded by input/output sizes but lacks
a hard killable compute deadline. Configured large models may exhaust host resources.

Normalized images/cache are local plaintext, not encrypted personal storage.
Original bytes are discarded; normalized media retention is manual. DB/filesystem
commits are not atomic together, so interrupted writes can leave orphan files.
Cross-process signing/circuit/recovery is not implemented; single-process startup
recovery preserves records and reports interruption. Evidence is durable task
context, not an automatic long-term memory. History is limited to 100 records,
polling/separate reads remain, and no hosted CI or deployment was configured.
Pillow safeguards and npm audit/pip compatibility checks are not a security
certification. Media symlink/path checks assume a trusted local operator; they
are not an OS defense against an adversarial host process racing filesystem access.

## Files, Git and local operation

The verified manifest follows. Candidates contain source/configuration/docs/tests
only: no actual .env, credentials, model weights, screenshots/traces, dependencies,
caches, build/bytecode or database artifacts. Controlled images are generated
from small repository-owned code; test screenshots remain ignored.

47 changed/new files.

```text
.env.example
.gitignore
README.md
backend/Dockerfile
backend/app/config.py
backend/app/fixtures/personal_context.py
backend/app/intelligence/agents.py
backend/app/intelligence/contracts.py
backend/app/intelligence/orchestrator.py
backend/app/logging.py
backend/app/main.py
backend/app/model_routing/contracts.py
backend/app/model_routing/policy.py
backend/app/model_routing/providers.py
backend/app/model_routing/registry.py
backend/app/model_routing/router.py
backend/app/model_routing/service.py
backend/app/perception/__init__.py
backend/app/perception/api.py
backend/app/perception/contracts.py
backend/app/perception/evidence.py
backend/app/perception/media.py
backend/app/perception/models.py
backend/app/perception/processors.py
backend/app/perception/service.py
backend/app/perception/vision.py
backend/migrations/env.py
backend/migrations/versions/0005_multimodal_perception_multimodal_perception.py
backend/requirements.lock.txt
backend/requirements.txt
backend/tests/conftest.py
backend/tests/test_perception.py
compose.yaml
docs/adr/0006-multimodal-provenance-and-responsibility.md
docs/adr/0007-media-privacy-and-local-storage.md
docs/architecture.md
docs/phase-5-architecture.md
docs/phase-5-final-audit.md
frontend/app/api/[...path]/route.ts
frontend/app/globals.css
frontend/app/perception/page.tsx
frontend/components/nova-workspace.tsx
frontend/components/perception-workspace.tsx
frontend/styles/perception.css
frontend/tests/continuity.spec.ts
frontend/tests/perception.spec.ts
scripts/acceptance_phase5.py
```

HEAD remains the Phase 4 checkpoint, four preserved commits, branch main.
The index is empty; tracked changes are unstaged and new files are untracked.
No commit, amendment, push or remote configuration occurred. The original NovaAI
file remains unchanged. Local acceptance/regression tasks and sanitized images
remain in preserved application volumes. Validation containers were stopped
at completion; no application volume was deleted.

```sh
docker compose up --build -d --wait
python3 scripts/acceptance_phase5.py
python3 scripts/acceptance_phase5.py --verify-task TASK_ID
```

Open http://localhost:3000/perception?task=TASK_ID and http://localhost:8000/docs.
See [architecture](phase-5-architecture.md) and ADRs 0006/0007 for contracts,
optional local configuration, semantics and trust boundaries.

**Final result: Phase 5 accepted within the documented local fixture scope.
Real visual inference remains unconfigured. No remaining Phase 5 blocking
finding was identified. Phase 5 is uncommitted; Phase 6 was not begun.**
