# Phase 5: multimodal perception and visual context

Phase 5 extends checkpoint `5a4cec77641da80f98976ab258f2f18aa011bf0e`.
It preserves shared tasks, the real Semantic Kernel execution path, Phase 4
routing/accounting, and Phase 3 human approval. Default runtime requires no
vision weights, ML framework, inference service, credentials, or paid API.

## Data flow and responsibility

Browser → same-origin binary/JSON gateway → dedicated MediaIngestionService →
normalized private PNG storage → PerceptionOrchestrator → independent processor
records → optional routed VisionLanguageProvider → typed observations → bounded
ContextEvidence → existing Context/Planner/Calendar/Memory/Critic graph.

Visual inference cannot change routing, tool permissions, task ownership,
canonical approval hashes, execution adapters, or permanent personal memory.
The explicit `/reason` path optionally calls the existing proactive service.
Only its synthetic calendar/travel scenario justifies a communication draft;
visual prose does not decide whether to send. Human approval and separate
simulation execution remain required. No external message is sent.

## Media boundary

Uploads are raw JPEG/PNG/WEBP bodies, with `Content-Type` and `Idempotency-Key`.
No filename, client path, URL or multipart parser is needed. Routes delegate
stream limits, decoding, metadata removal, hashing and storage to the service.
The gateway bounds bodies before forwarding; the backend independently bounds
streamed bytes, with an eight-second upload deadline.

Defaults: MAX_IMAGE_BYTES=2,000,000; MAX_IMAGE_WIDTH/HEIGHT=2048;
MAX_IMAGE_PIXELS=4,000,000; MAX_NORMALIZED_IMAGE_BYTES=8,000,000.
Server settings are bounded. Pillow 12.3.0 verifies supported containers,
checks decoded format against MIME, rejects animation, warnings/decompression
bombs, malformed images and malformed EXIF headers, then fully decodes,
normalizes EXIF orientation and reconstructs RGB pixels in a fresh image.
Only re-encoded PNG is stored. EXIF/GPS/ICC/XMP/PNG text are discarded; no
metadata payload or original filename enters SQL, logging or model context.
Malformed ICC is discarded without color-profile interpretation. Orientation
changes can alter dimensions; hashes bind the normalized bytes.

PNG chunk termination, JPEG end marker and WEBP RIFF length reject detectable
appended polyglots. This is not proof that every possible parser ambiguity is
recognized. Original upload bytes exist only transiently during decode.

Opaque media UUIDs map to server-generated UUID.png names. Stored references
must equal that exact name; root escape and symlinks are rejected. Content reads
verify byte length and SHA-256. Ownership checks bind task, demo user and media;
artifact access repeats parent-media ownership checks. APIs expose IDs and
metadata, never filesystem paths. Responses are image/png, no-store and nosniff.
Files have private permissions; the Docker media volume belongs to the non-root
application user. Normalized media persists across service restart in `media_data`.
Native operation should configure a durable private MEDIA_DIRECTORY: its default
/tmp path is not a promise of persistence across OS cleanup/reboot.

Normalized media and evidence have no automatic deletion policy in this local
demo. Operators must manage retention; original uploads are never retained.
A database/file write interruption may leave an orphan normalized file. The
store is not an encrypted vault or a distributed transactional object store.

## Fixture and optional real processors

The controlled 480×300 meeting scene is generated from repository-owned Pillow
drawing code, with a sign, laptop, backpack and cup. No web imagery is used.
Its source is metadata-free. UI labels it FIXTURE MEDIA / NO PERSONAL IMAGE DATA,
not a claim that GPS was removed from that particular fixture.

FixtureVisionProvider emits four known annotations, FIXTURE_VISION,
fixture-vision-v1, simulation=true, score=null/NONE, without geometry. Fixture
VLM adds a separately attributed interpretation. Uploaded media, even identical
pixels, is source IMAGE and cannot receive those controlled-scene annotations.
Fixture mutation requires Wearable, and content is checked against the current
controlled fixture before each run. No arbitrary image is “detected” by fixtures.

CLIP, DINOv2 and SAM adapters are disabled by default and lazily import optional
`torch`/`transformers`. They require an explicitly configured existing local
model directory, `local_files_only=True`, safe tensors for model weights, and
no remote custom code. They do not install libraries, call torch.hub, download
weights or initialize on application startup. Missing dependencies/directories
produce DISABLED/UNAVAILABLE. Compose passes enablement/model-directory settings;
operators must separately mount existing model directories read-only through
a private override. No model-directory mount or download is automatic. The standard requirements add only Pillow, not ML.

CLIP runs actual image/text representations and cosine semantic comparisons
against meeting room, outdoor park, kitchen, server room. CLIP_COSINE is not
object detection, calibrated probability or physical-location verification.
DINOv2 computes visual features and retains only shape/processing metadata;
no object identity is invented and no large vector enters JSONB.
SAM uses a server-owned center-point prompt and at most three actual binary mask
PNGs, with opaque artifact IDs, regions derived from nonzero masks, and actual
SAM_IOU values. Masks establish segmentation, not semantic object identity.
Real model paths/capabilities remain trusted server configuration. No real
processor was configured or exercised in this implementation session.

Adapters bound image dimensions and output shapes/counts. Optional in-process
ML compute is not a killable OS sandbox or a hard end-to-end compute deadline.
Large/incompatible models can exceed host resources and should not be enabled
without deliberate operator setup. Real inference quality is unverified.

## VISION routing and provenance

ModelRequest activates IMAGE modality, VISUAL_CONTEXT purpose, required VISION,
media UUID/hash, device, privacy, trace, and explicit fixture permission. Missing
media binding fails validation. The existing ModelRouter, eligibility, circuit,
budget and ModelCall ledger handle the request; no parallel routing service exists.
FixtureVisionLanguageProvider is a distinct VISION service, fixture-vlm-v1,
NOT REAL VISUAL INFERENCE. Default text providers do not acquire VISION capability.

Phase 5 forbids every cloud/external-priced visual candidate, even for PERSONAL
input and even if cloud policy/budget allow text. Sensitive visual requests also
retain local-only privacy and bypass Redis result caching. Fallback independently
rechecks these conditions. No image bytes are sent to cloud; there is no production
cloud vision transport or configured real local VLM. The fixture receives only
server-bound media references for a verified scene. Arbitrary uploads have no
eligible fixture VLM and fail in a controlled manner.

Every observation binds media/hash/source/device/timestamp, processor/model,
simulation, separate score semantics, geometry if present, and UUID provenance.
Source media origin and processor simulation are separate: real CLIP on a
controlled fixture still reports real CLIP results, never fixture detections.
Unrelated scores are never averaged. Strict contracts reject extra fields,
inconsistent simulation, invalid geometry, huge outputs and invented fixture
scores/masks. Orchestration checks identity against the selected processor.

## Context, injection and persistence

ContextEvidence carries observation/media IDs, hash, processor/model, source,
simulation, score/type, captured device and timestamp. The controlled meeting
interpretation says “consistent with”, never verified physical location. Other
outputs remain explicitly untrusted evidence. Agent prompts receive typed data,
not new system instructions or additional tool permissions. Visible image text,
metadata and arbitrary VLM prose cannot approve or execute, alter policy or create
preferences. The Memory agent remains the read-only synthetic preference plugin.
Persistent perception audit context is distinct from long-term personal memory.

The explicit reasoning path passes bounded evidence into SharedContext. Context
Agent preserves it, Planner includes attributable VISUAL_EVIDENCE references,
and the existing deterministic Critic validates against the captured context.
Calendar/preference fixtures retain DEMO_FIXTURE provenance. Task ownership is
never changed by perception or intelligence completion.

Migration 0005_multimodal_perception adds MediaAsset, PerceptionRun, ProcessorRun,
VisualObservation and MediaArtifact. UUID/FK links, unique task/key and per-run
processor constraints, state checks and indexes enforce persistence. Bounded
validated observation structures use JSONB; raw media, raw vectors and mask
arrays do not. PostgreSQL advisory locks serialize identical perception keys;
changed requests return 409. Uploads use the task row lock only for storage commit.
Perception releases ordinary read transactions while routed inference executes;
handoffs remain independent. Completed original-key retries preserve IDs,
observations and captured Wearable context after the task moves to Mobile.

Processors persist DONE/FAILED/SKIPPED/UNAVAILABLE independently. Failure of one
does not erase another's valid observations. Failures or enabled-but-unavailable processors with surviving output
produce PARTIAL. Unconfigured optional processors are visibly skipped; DONE means
the selected available work succeeded, not that CLIP/DINO/SAM actually ran.
Startup marks abandoned RUNNING runs FAILED/APPLICATION_RESTARTED and preserves
already committed processor records. Recovery is for one local backend process.

## APIs and UI

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

/perception shows sanitized media, privacy, actual processor state, observations,
score semantics, provenance, interpretation and links to model history/approval.
No fixture geometry is drawn; masks/regions appear only if corresponding output
exists. Command Center and Task Detail show a compact actual visual summary.
Only pending request intent is stored in localStorage; authoritative data is in
PostgreSQL/local media storage. Task-keyed components cancel obsolete reads,
check parent mutation ownership and ignore stale acknowledgments. A synchronous
posting guard prevents duplicate click requests. History lists are bounded at
100 records without UI pagination. Mobile layout targets a 390px viewport.

## Scope and references

This is an unauthenticated, single-user, loopback local demo. No real camera,
wearable, audio, external account, paid API, vector memory, cloud, deployment,
telemetry framework, OAuth or Phase 6 feature is implemented. Security review is
not a penetration test, decoder sandbox or comprehensive vulnerability audit.
Required external spend is $0; local compute/electricity is not priced.

Implementation references: [Pillow security guidance](https://pillow.readthedocs.io/en/stable/handbook/security.html),
[Pillow Image API](https://pillow.readthedocs.io/en/stable/reference/Image.html),
[Transformers local model loading](https://huggingface.co/docs/transformers/main_classes/model),
[DINOv2 responsibility](https://huggingface.co/docs/transformers/model_doc/dinov2).

Text request hashes deliberately exclude the new unused media fields, preserving
historical Phase 4 original-key retries across the schema extension. The visual
reasoning service serializes owned request intent; a changed proposal flag with
an existing reasoning key returns 409. Failed intelligence cannot surface a new
proposal through that path. APIs delegate both perception and reasoning work.
