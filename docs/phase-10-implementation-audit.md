# Phase 10 implementation audit

October 19, 2026 (America/New_York). Baseline main:
`7765b33736c28ccc560fc8269bb5fc4b9b050518` (Phase 9 checkpoint).

**Latest, October 20: R2 real acceptance PASS; PHASE 10 COMPLETE within its defined
bounded local scope.** One authenticated request and one Qwen generation produced
`noodles`, evidence index 0, with original citation/current source/privacy/permission
verification. One DONE job/one PENDING_APPROVAL proposal, no approval or execution.
Final-source offline/cross-stack qualification passed. Cleanup independently
verified; credentials revoked, real configuration disabled, services/models stopped.
The final section records exact measurements and preserved historical failures.

**Source reconciliation prepared:** the [separate R1 acceptance proposal](phase-10-real-acceptance-proposal-revised.md)
explains the four audit-only hunks and preserves the original freeze. All remaining
source/prompt/schema/fixture/artifact checks passed. Ready for explicit operator
approval at that preparation checkpoint; the later authorized-preflight outcome
is recorded below without changing the historical reconciliation evidence.

**Original implementation scope (historical): local fixture qualification, with
real acceptance open.** Later separately approved scopes and the failed R1 real
attempt are recorded below. No external action, download, installation, deployment,
Git checkpoint or Phase 11 occurred. Phase 9 history is unchanged.

## Implemented and reused

Added `backend/app/proactive/drafts.py`: a bounded owner-requested preference draft
workflow. It retrieves eligible cuisine/beverage facts automatically by named
subject/predicate or pins one/two explicit memory references. It preserves original
UUID/full quote/provenance and Phase 9 source bindings. Unknown question forms,
unrelated/ineligible sources, conflicts and unsafe policy-marker content refuse.
This is the declared structured support subset, not general semantic reasoning.

It reuses existing ContextEvent, ProactiveTrigger, ActionProposal, ApprovalDecision,
AuditEvent, Outbox/Inbox and Job; existing InferenceProvider/GroundedFixture and
LocalProvider; Phase 9 support/context-budget/UUID/quote/privacy verification;
and existing local/OIDC authentication, RBAC and Approval Center. No new framework,
broker, tables, migration or dependency was added.

ContextEvent insert emits a metadata-only authoritative event. Existing consumer
deduplication creates one durable job. State updates do not create more jobs.
The existing advisory worker lock serializes processing across workers. Draft
generation runs outside owner locks; source and current authorization checks,
proposal/job completion and audit commit atomically under owner/source locks.
Fixture RUNNING work can recover; interrupted real RUNNING work refuses another
generation. Idempotency rejects changed intent; terminal cancellation/expiry/
failure/rejection cannot be revived by a delayed worker.

The verified principal now carries its identity row ID. Queued local/OIDC grants
bind identity/device versions and are rechecked before generation and finalization.
Revocation or source changes invalidate the draft. Read paths also revalidate;
terminal draft views omit evidence/content and existing proposal views redact stale
Phase 10 content. Historical private records remain retained, not physically erased.

FIXTURE remains default. Private `OWNED_DRAFT_MODE=LOCAL_REAL` is prepared but
disabled. It requires managed SELECTION_V1 and the existing pinned budget/profile,
artifact and resource gates; no API provider/endpoint/authority parameter exists.
The model's selected value is independently checked before original citations are
attached. The real path has offline double coverage only. No queued real-mode job
or real activation attestation was created by qualification.

The new proposal contract stops at PENDING_APPROVAL. Approve/edit/execute refuse;
rejection uses the existing ApprovalDecision record, and cancellation is audited.
No Phase 10 ActionExecution is created. Legacy explicitly labeled communication
simulation remains available to its existing regression scenarios.

Approval Center now shows owned-draft preparation, automatic/pinned context,
evidence/provenance, verification, queued/running/pending and terminal states,
expiry, cancellation and rejection. It exposes no Phase 10 execution control.

## Executed deterministic validation

Final current-source backend command:

```sh
docker compose -f compose.yaml \
  -f .local/phase9/final-qualification-20261019/backend-test-overlay.yaml \
  --profile test run --rm backend-tests \
  sh -c 'pytest -q && ruff check app tests && ruff format --check app tests && pip check'
python3 scripts/test_phase9_residency.py
```

- Backend **747 passed, one explicit real-model skip, 68.38 s**: existing 700 plus
  47 new owned-draft cases. Ruff lint/format passed, 112 app/test files formatted;
  pip check passed. No test dependency installation occurred.
- Controller **13 passed, 0.060 s**, deterministic callbacks/non-model subprocess.
- Go existing compiler image, network disabled, GOPROXY=off/GOTOOLCHAIN=local:
  two race tests passed (package 1.024 s), vet passed. No Go source change.
- Frontend installed dependencies: lint, typecheck and production build passed
  on the final automatic-selection source. No separate unit runner is configured.
- Acceptance harness Python syntax and Ruff checks passed.
- Migration checks run through mandatory isolated test setup; no new migration is
  needed. Existing head remains 0011_inference_registry.

Backend/test DB retained 512 MiB each, runner two CPUs/DB one CPU; Redis 48 MiB.
Current source is mounted read-only into existing test/runtime images. Heavy
suites run sequentially; test guard refuses cleanup outside a `_test` database.
Protected application data and real embeddings were not connected to these tests.

Security coverage includes foreign-owner/task access, role refusal, identity/device
revocation, source deletion/privacy/scope/expiry/content/owner changes, source change
during scripted generation, conflict refusal, unsafe instruction markers, invented
UUID/quote/value/index, invalid JSON/extra tool/approval fields, truncation/timeout,
duplicate event/request, changed intent, RUNNING recovery, atomic rollback,
concurrent worker refusal, cancellation during generation, approval/execution
denial, stale read redaction and interrupted real-job no-retry behavior. Doubles
do not establish learned quality or real-model injection resistance.

## Intermediate failures retained

- Initial focused snapshot: 9 failed / 21 passed. The new request omitted required
  `current_device`, stopping generation; the conflict fixture was pending rather
  than ACTIVE. Device binding was supplied and the fixture explicitly modeled an
  active conflicting fact. Assertions were preserved; then 30 focused cases passed.
- First full run: 735 passed / two failed / one skipped. A new proposal lookup
  preceded existing worker-role and shadow-evaluation guards. Their original guard
  precedence was restored; next full snapshot passed 737/one skip. Subsequent
  additions passed 42 focused, then 744 and 746 full cases. These counts are
  successive snapshots, not additive suites or automatic retries.
- Initial formatting/import findings were corrected before final checks. One host
  stop-command redirection used the frontend working directory; the explicit root
  command stopped only the dedicated test services afterward. Script Ruff config
  initially used a filename interpreted as standalone TOML; the same pyproject was
  mounted under its proper filename, then checks passed.
- An ignored qualification overlay initially duplicated environment keys; Compose
  refused before startup. The overlay was corrected without production changes.
- First browser invocation started before native frontend readiness: 13 failed,
  40 passed, five profile skips. A readiness wait was added to the ignored harness.
- Next rapid replay run: 50 passed / three failed / five skipped after existing
  gateway quota returned 429. A fresh gateway run: 51 passed / two failed / five
  skipped, again reaching the unchanged quota near its final cases. Limits and
  assertions were preserved. Final replay qualification is explicitly split into
  paced batches, not claimed as one full-profile passing invocation.
- The first strict profile started before its Kafka prerequisite: two passed and
  one operations test timed out. With the dedicated broker/workers ready, all
  three passed without changing the test. The Phase 10 harness then correctly saw
  an empty 401 but tried to parse JSON; expected-empty-response handling fixed the
  harness, preserving its exact 401 assertion, and actual fixture acceptance passed.
- Final review identified a stale internal Job read could regress an already
  completed request if a direct caller bypassed the advisory worker lock. The job
  now refreshes after owner serialization. A direct concurrent-call regression
  preserves PENDING_APPROVAL and one proposal. Final full backend: 747/one skip.
  Earlier browser/Kafka qualification precedes that one-line internal hardening;
  no frontend, provider wire or broader integration change was made afterward.

## Local integration, resources and final disposition

Final integration results and measurements are recorded in
[test evidence](phase-10-test-evidence.md). Evidence remains ignored under `.local/phase10`; credentials remain
private under `.secrets/phase10-qualification`. The dedicated Compose project is
`nova-phase10-qualification`, with no protected application/model mounts.

Remaining mandatory gate: a separately approved bounded real draft case and
operator review of this limited Phase 10 scope. See the
[real acceptance proposal](phase-10-real-acceptance-proposal.md). A positive real
case must reach pending approval with independently verified support/current
privacy and no action execution. No general agent quality or production claim
follows from that finite case. External integrations are outside this implementation.

Known limits: explicit opt-in trigger, named preference subset and bounded context,
extractive verification rather than semantic entailment, trusted operator/database,
single advisory worker, read/final-commit privacy snapshot, retained historical
records and finite tests. Cancellation blocks final acceptance; it need not stop
an already executing bounded provider immediately. Fast full browser traffic
exceeded the unchanged local gateway quota; paced results do not qualify capacity.
Full planner/critic real inference, vision, model judging, sustained/streaming load,
deployment and existing Phase 8 Kubernetes/NetworkPolicy caveats remain unqualified.

**PHASE 10 NOT COMPLETE. No new real inference, downloads, installation, paid/cloud
traffic, external message, Git staging/commit/push/remote change or Phase 11.**

## Final local-service evidence and stop

Replay browsers passed in two paced batches, 38 + 15; separate local-auth three
and actual local OIDC two passed: 58 cases over four passing invocations, not one
full-profile pass. The new actual-service case queues/cancels an owned draft; the
other new case uses explicitly scripted responses for evidence/terminal rendering.
The final build used current frontend source and existing installed dependencies.

Authenticated Phase 10 Kafka task `b920261a-8d82-4ead-87db-d86ffd15279b`, draft
`aca5f9e7-1bc2-4a7d-a70f-5aa8ecfc6dba`, proposal
`3fe3d499-92d5-491b-a237-50503b0ac14c`: fixture generation, exact original evidence,
PENDING_APPROVAL, no bearer 401/foreign owner 404, approve/execute denied, explicit
rejection persisted. Three duplicate envelopes had no extra effect; a forged
approval-like envelope produced three dead letters. Another fixture draft survived
a stopped worker while QUEUED, reached pending after restart and was cancelled.
This is queued recovery; actual mid-call process kill is not claimed. Scripted
RUNNING recovery, rollback and concurrency cases passed in PostgreSQL tests.

Legacy Kafka/HITL qualification retained one task through Mobile, nine events,
three groups, one job and payload-bound approval with simulated NOT SENT execution.
Actual broker-outage recovery drained two pending events in 28.591 s. Golden
baselines passed FULL 104/104, SMOKE 10/10 and REGRESSION 25/25, critical=0;
cautious remained 23/25, expected gate FAIL. Exact IDs are in the test evidence.
SQL confirmed zero Phase 10 execution rows, zero DONE LOCAL_REAL inference rows,
zero evaluation schemas and empty real registries. Draft IDs/states/owners/modes
persisted identically across backend/auth-profile restarts.

All qualification ran in `nova-phase10-qualification`, existing images with
pull=never, read-only current source, eleven dedicated named/anonymous volumes,
and existing Phase 9 caps. All mounts were verified exclusive to this project;
protected application/auth/model volumes were not used. OIDC ran after Kafka
workers/broker stopped. Temporary overlays and correction logs remain ignored.

Initial RAM 8 GiB, disk approximately 16,513,150,976 bytes, swap 1304.81 MiB;
Docker remained 4,106,604,544 bytes/eight CPUs. Main watcher: 728 snapshots,
minimum free disk 15,478,239,232 bytes, swap 1152.81–1388.69 MiB. Final hardening
watcher: 45 additional snapshots, swap 1388.69 MiB. No resource gate failed.
Final stopped reading **05:20:17**: disk **15,490,191,360 bytes**, swap
**1388.69 MiB**, unchanged RAM/Docker. No model RSS, model token or inference-speed
measurement exists here. Fixture usage is UNKNOWN, not invented model accounting.

All task-owned containers, native frontend and watchers stopped. Independent
listener checks were empty on 3000/8000/8080/8180/5432/6379/11434/11435/11436;
no model process remained. Data, volumes, artifacts and earlier private configs
were preserved. Real mode stayed disabled, no activation attestation was issued,
and no cache/volume deletion or host/Docker restart occurred. External spend $0;
host compute/electricity unpriced.

Prepared one controlled future task/memory and exact request without submitting
any draft: task `9b363f16-1c38-46ff-a190-b674b7b28ed8`, source
`7d1049cb-06b9-49c4-ad06-a8db5036480a`. The proposal freezes their owner, source
binding, body, prompt/schema hashes and 469/512 offline bound. This is readiness
metadata, not approval or real execution. The roadmap's Phase 10 direction is
broad; the current mission's bounded workflow is specified here. General agent
reasoning is not silently substituted for this scope, and no completion sign-off
is inferred from fixture qualification.

Current candidate: **20 text files, 10 modified / 10 added**, listed in the
[Phase 10 staging manifest](phase-10-staging-manifest.md). Main/HEAD remain the
Phase 9 checkpoint, index empty, no remote or Git write operation. All Phase 1–9
checkpoint commits, Phase 9 audits and golden baselines are preserved. Only a
separately approved real draft case may cross the model boundary described in the
proposal. **STOPPED; PHASE 10 ACCEPTANCE OPEN.**

Final source review matched all 20 manifest paths and checked UTF-8 regular files,
Python syntax, tracked/new-file whitespace and bounded credential shapes. Eleven
inspected private model registries remained resource_approved=false. The final
controller rerun passed 13 tests in 0.047 s (the earlier 0.060 s run is preserved).
Acceptance harness final lint/format/syntax checks passed. No file was staged;
the source inventory/fingerprints remain ignored review evidence, not a commit.

## October 19 continuation — resource refusal and final source review

Reviewed all 20 existing candidate files, the frozen real proposal and the earlier
audit/evidence. The previous Phase 10 real case has **not executed**. The current
mission directs conditional execution of that single frozen scope; its required
resource check refused before activation. Earlier Phase 9 approvals were not reused.
The proposal's preparation title and frozen body/source/prompt/schema were preserved.

Initial fresh read: **2126.81 MiB used swap**, versus the required strict <2048 MiB;
15,220,440 KiB free disk. No containers were running. The later independent stopped
snapshot at **12:23:23 America/New_York** recorded **2102.81 MiB swap** and
**15,579,082,752 bytes free disk**, 8,589,934,592 bytes RAM and unchanged Docker
allocation **4,106,604,544 bytes / eight CPUs**. Both swap readings fail. The cause
of host-wide pressure was not established. No threshold, allocation, cache, volume
or host service was changed to obtain a pass.

**Real acceptance: BLOCKED / NOT EXECUTED**, not a failed model generation.
Exactly zero draft submissions, Qwen generations, BGE calls, retries, model leases,
new passing attestations or external actions occurred. No new request/job/proposal
ID, token/latency/RSS measurement or real result exists. Artifact hashes, scoped
controller/authentication checks and application ownership reads were not performed
after the early resource refusal; preparation metadata is not fresh execution proof.
The frozen source was not substituted or recreated, and the application DB was not
started or accessed. No unused inference allowance was converted into a diagnostic.

### Confirmed correction and lifecycle coverage

Review found owned-draft audit records used `ProactiveService()`'s legacy frozen
demo clock, while draft creation/expiry and proposal dates use real UTC time.
`backend/app/proactive/drafts.py` now supplies the existing `SystemClock` **only**
for owned-draft audit calls. Legacy fixture-clock behavior is unchanged.

Submission additionally records REQUESTED then QUEUED audit milestones in its
existing atomic context/outbox transaction. After independent citation/support
and final current source/permission/conflict validation, EVIDENCE_VERIFIED is
audited in the same transaction as proposal/job/PENDING_APPROVAL completion.
No extra durable state, endpoint, event trigger, generation, prompt, schema or
authority was introduced. A rolled-back proposal cannot leave a committed verified
milestone. Existing durable state equivalents remain QUEUED -> RUNNING ->
PENDING_APPROVAL with terminal FAILED/CANCELLED/EXPIRED/REJECTED.

The existing owned-workflow database regression now checks the five audit
milestones and their wall-clock timestamps. Its rollback regression also requires
no committed EVIDENCE_VERIFIED audit after a failed final transaction. The scripted
browser lifecycle case now explicitly exercises QUEUED, RUNNING, PENDING_APPROVAL,
CANCELLED, REJECTED, EXPIRED and FAILED, checks hidden non-pending evidence/content,
available cancellation, absent terminal rejection controls and the safe failure
message. These added assertions are **NOT EXECUTED** against services in this
continuation; syntax checks alone do not qualify them.

### Checks executed and deferred

- Host controller/process regression: **13 passed, 0.046 seconds**, no model loads.
- Candidate UTF-8/regular-file inventory and Python AST parsing: PASS. All 20 paths
  match the manifest, 10 modified / 10 added; no binary/symlink candidate.
- Installed TypeScript syntax transpilation for the edited browser test and owned
  draft component: PASS with a 96 MiB Node heap ceiling. This is not a typecheck,
  production build or browser run.
- Before the justified correction, production hashes matched the earlier 747-test
  snapshot. The subsequent audit-helper/milestone changes require a fresh backend
  run; **747 passes are historical, not a final-source pass**.
- Bounded credential-shape checks and Git whitespace: PASS; not a comprehensive
  secret or security certification. Eleven inspected private model registry flags
  remain `resource_approved=false`; no real configuration was enabled or rewritten.
- Full PostgreSQL/backend, Ruff/format/pip/migration, Go race/vet, frontend build,
  browsers/auth/OIDC, Kafka recovery/outage and golden suites: **NOT RERUN**, to
  avoid starting heavy qualification services while the resource gate fails.
  Earlier results retain their exact recorded scopes and snapshots.

No new functional security acceptance is asserted. Existing owner/device/source,
privacy, conflict, invalid-output, idempotency, cancellation, HITL and no-action
guards remain in place; the audit correction does not change them. Full regression
must confirm that assessment. No further backend implementation defect was
demonstrated by this review; real usefulness and execution remain unverified.

### Cleanup, inventory and remaining gates

No task-owned application/frontend/model service was started. Independent checks
found zero running containers, zero model/controller processes and no listeners on
3000/8000/8080/8180/5432/6379/11434/11435/11436. No lease or scoped activation
attestation was created; private real flags remain false. Data, aliases, models,
vectors and volumes were preserved without deletion. Safe review evidence is
ignored under `.local/phase10/finish-review-20261019`.

Mandatory blockers: (1) failed swap gate, (2) the single frozen real draft has not
passed, (3) final-source backend and expanded lifecycle/browser qualification plus
the requested final cross-stack reruns remain outstanding. No real model failure
or positive acceptance result is invented. A future continuation must first pass
a fresh resource check, then finish preflight and the one-case scope, with zero
retries; an actual case failure remains a stop for real inference.

Only the existing 20 manifest paths remain candidates. This continuation edits
the owned-draft audit helper, its existing backend test, the existing browser test,
README and Phase 10 documentation. The frozen proposal, inference provider/prompt/
schema and Phase 9 history are unchanged. Main remains
`7765b33736c28ccc560fc8269bb5fc4b9b050518`; index empty, no remote. No Git staging,
commit, push, download, install, cloud/paid call, external message, deployment or
Phase 11. External spend $0; host compute unpriced. **PHASE 10 NOT COMPLETE.**

## October 20 — final-source qualification and frozen-source refusal

Executed approximately **01:08–01:17 America/New_York**, cleanup verified at
**01:17:32**. **Offline/local qualification PASS; real draft BLOCKED / NOT
EXECUTED; PHASE 10 NOT COMPLETE.** The operator authorized safe implementation and
qualification recovery but explicitly required stopping real acceptance on any
frozen source fingerprint drift. No real-model authorization was inferred for
changed source, and the frozen proposal was not updated or bypassed.

### Review and host pressure diagnosis

Reviewed the 20 existing candidates, current audit/evidence/manifest, frozen
proposal, architecture and README/roadmap context. Main/HEAD remains the Phase 9
checkpoint `7765b33736c28ccc560fc8269bb5fc4b9b050518`, index empty. Source review
found the latest audit correction already implemented; no further production
change was necessary in this continuation.

Read-only `sysctl vm.swapusage`, `vm_stat`, `memory_pressure`, process RSS/parent
inventory and Docker inspection found **1935.12 MiB used swap**, below the unchanged
strict 2048 MiB limit, and **14,894,832 KiB free disk**. RAM is 8 GiB. The reported
66% memory-pressure free percentage is not guaranteed allocatable model memory.
No containers were running. Largest visible resident processes were VS Code
renderers (approximately 434/325 MiB), its helpers and other user/system processes.
No task-owned orphan requiring termination was identified. These snapshots do not
establish which process caused the earlier accumulated swap or its later reduction.
Unrelated applications were not killed, and no user-application intervention was
needed while the measured gate passed. If pressure returns, closing unused editor
windows/apps after saving work is an operator option, not an agent action taken here.
No host/Docker restart, purge, allocation change, swap override or deletion occurred.

A task-owned watcher sampled disk/swap every two seconds during qualification and
would stop only qualification services, dedicated test services and the recorded
frontend process group on failure. Heavy workloads ran sequentially under existing
caps. All 243 recorded samples passed: swap **1743.12–1927.12 MiB**, free disk
minimum **14,864,408,576 bytes**. The initial 1935.12 MiB preflight preceded this
watch series. No resource-stop condition occurred.

### Exact real-acceptance boundary

The frozen proposal still points to `.local/phase10/source-review.json`. Comparison
found exactly one changed production file:

| File | Frozen SHA-256 | Current SHA-256 |
| --- | --- | --- |
| `backend/app/proactive/drafts.py` | `8ce187f969f521981b10ea977f264bdad226fd1ad713e0907d5564a3ed67407e` | `b9c239154da11ed8acbbf90816e939c35c96a919184e9f97bb53a6fa0af92881` |

This is the previously documented SystemClock/REQUESTED/EVIDENCE_VERIFIED audit
correction, not a new prompt experiment. All other frozen production fingerprints,
including inference provider/schema/budget source, match. The frozen proposal's
bytes also match. The operator's Section 11 says: **"If any frozen source, prompt,
schema or authorization-bound fingerprint has changed: STOP and report the exact
drift."** Accordingly real preflight stopped at source verification. Model artifact,
controller bearer and activation attestation checks were not completed or presented
as fresh execution proof. No controller/runtime was started or passing model
attestation issued; private real settings stayed disabled.

Read-only checks in the dedicated fixture application independently confirmed the
original task/source ownership, ACTIVE memory and exact frozen source binding. The
frozen idempotency key has **zero ContextEvent rows** and there are **zero LOCAL_REAL
owned-draft rows**. The request/source were not regenerated or substituted. Existing
Phase 9 protected data, vectors and model artifacts were not mounted or modified.

**Actual real scope: zero authenticated real draft POSTs, zero Qwen generations,
zero BGE calls, zero inference retries, zero external actions.** There is no real
request/job/proposal ID, model token/latency/RSS measurement or positive result to
report. This is BLOCKED before generation, not a model failure. The mandatory
positive real acceptance remains open. Passing deterministic checks cannot replace it.

### Final-source checks and actual results

| Check | October 20 result |
| --- | --- |
| Focused owned-draft PostgreSQL suite | **47 passed, 3.31 s** |
| Full PostgreSQL backend | **747 passed, one explicit real-model opt-in skip, 68.65 s** |
| Ruff lint / format / pip check | **PASS**, 112 app/test files already formatted, no broken requirements |
| Controller/process tests | **13 passed, 0.057 s**, no models |
| Go race / vet | **2 tests passed**, package 1.023 s, vet exit 0 |
| Frontend lint / typecheck / production build | **PASS**, existing installed dependencies |
| Replay browser batch A | **38 passed, 41.0 s** |
| Replay browser batch B, including expanded lifecycle | **15 passed, 5 explicit auth/OIDC profile skips, 10.6 s** |
| Separate strict local-auth browser profile | **3 passed, 5.9 s** |
| Separate actual local OIDC profile | **2 passed, 2.4 s** |
| Phase 10 fixture Kafka/draft/duplicates/worker restart | **PASS**, original UUID/quote, one proposal, execution disabled |
| Legacy Kafka/HITL/duplicate/forgery | **PASS**, SIMULATED / NOT SENT |
| Broker outage | **PASS**, 2 pending events, same task, **21.756 s** from restart command |
| Application Alembic current / check | **0011_inference_registry (head)**, no new upgrade operations |
| Golden FULL / SMOKE / REGRESSION | **104/104 / 10/10 / 25/25**, critical=0, gates PASS |
| Cautious negative control | **23/25**, critical=0, expected FAIL/CLI exit 1 |
| Persistence, frozen records, empty evaluation schemas, model-disable | **PASS**, read-only SQL checks |

Browser qualification is **58 cases over four passing invocations**, not one
58-pass suite. All replay files ran in documented paced batches with retries=0
and trace=off; the unchanged gateway quota and assertions were preserved. The
scripted lifecycle case validates rendering for QUEUED/RUNNING/PENDING_APPROVAL/
CANCELLED/REJECTED/EXPIRED/FAILED. Actual application queue/cancel and authenticated
fixture Kafka pending/reject/restart flows are separate service evidence. Scripted
rendering is not real-model or general agent quality evidence.

The latest backend run verifies real UTC audit timestamps, atomic REQUESTED/QUEUED
creation, EVIDENCE_VERIFIED/proposal/job final commit and rollback of uncommitted
milestones. Idempotent/duplicate processing retains one proposal and unique
milestones. Legacy fixture-clock regressions passed without changing their source.
Owner/task/device revocation, source lifecycle/privacy/content/conflict changes,
invalid output/citation/value/index, injection-marker refusal, cancellation,
expiry, rejection, terminal non-revival, RUNNING recovery and no-approval/execution
bypass remain covered. These finite tests do not certify learned injection
resistance, arbitrary entailment or comprehensive security.

The first focused runner invocation used unsupported Compose `run --no-build` and
exited 1 before starting tests. Removing that unsupported option used the existing
image with `--pull never`, without `--build`; the focused suite then passed. No
source or assertion correction was needed. All subsequent qualification commands
completed successfully; the cautious CLI's exit 1 is its predeclared negative
control, not a retried failure. No dependency, image or model was downloaded.

### Actual integration records and persistence

Phase 10 **FIXTURE** task `0972c17c-fe0d-41bb-b3c8-18ae6a2ea73e`, draft
`2b975cda-6641-45eb-ad86-c3db092af85e`, proposal
`2f9ed721-df50-4826-b4f9-2281ad6ce504`: one durable proposal reached
PENDING_APPROVAL with the original quote/UUID independently verified. Missing
bearer returned 401, other owner 404, and approve/execute 409 DRAFT_ONLY. Three
actual duplicate envelopes caused no extra proposal; the forged approval-like
envelope produced three dead letters. Explicit rejection persisted; a second
fixture request survived a stopped worker while QUEUED, reached pending after
restart and was cancelled. This proves queued restart durability, not an actual
mid-generation process kill. PostgreSQL tests separately exercise RUNNING recovery,
concurrency and final-transaction rollback.

A read-only live audit check verified exactly REQUESTED, QUEUED, RUNNING,
EVIDENCE_VERIFIED, PENDING_APPROVAL and then REJECTED, with current UTC timestamps,
no duplicate milestones, one DONE job/proposal, only a rejecting ApprovalDecision
and zero ActionExecution rows. This is fixture integration, not the blocked real case.

Legacy acceptance task `ec93c2b1-837b-4f37-8b13-0c548ab5df05` retained its UUID
through Mobile: nine outbox events, three consumer groups, one job and proposal
`03eec024-d459-45cf-9c88-9002612fbafa`. Approval stayed payload-bound, duplicate
and forged-event checks passed, and delivery remained SIMULATED / NOT SENT.
Actual broker-outage task `cba14508-3288-4146-996e-7575caa509f1` preserved its
pending work; two events drained after restart in 21.756 s. The four continuity
HTTP samples are not a throughput/capacity or HA measurement.

| Golden fixture run | UUID |
| --- | --- |
| FULL | `926541c6-5806-40b2-9e7d-8c29a4fb87df` |
| SMOKE | `d65f8e36-e1e9-4533-bba3-0e64f1e9ad47` |
| REGRESSION | `4079a448-e1da-4ccf-a0d7-878df4927ae4` |
| Cautious expected negative control | `2f28c446-914b-4b25-b89e-7aca45d24bc4` |

Draft IDs/owner/task/mode/state snapshots matched identically before and after
backend/OIDC restarts. SQL confirmed zero Phase 10 ActionExecution rows, zero
DONE LOCAL_REAL inference rows and zero leftover evaluation schemas. No golden
labels, historical thresholds or prior results were rewritten.

### Environment, cleanup and outstanding gate

Reused dedicated `_test` PostgreSQL/test Redis and existing test image with current
read-only source, 512 MiB DB/runner and 48 MiB Redis; test cleanup remains guarded
against non-`_test` databases. Integration reused only `nova-phase10-qualification`
and its independently checked exclusive volumes. Existing images used pull=never
and no builds. Application PG/backend/Redis/gateway caps remained 192/384/64/64 MiB,
Kafka/Keycloak 768 MiB each, workers 384 MiB each. Kafka stopped before OIDC.
Frontend used installed Node/npm/browser binaries, existing 768/512 MiB build/server
heap limits; Go used the existing network-disabled compiler image with 384 MiB.
These are unchanged caps; Node heap settings are not hard RSS guarantees.

At **01:17:32**, independent cleanup recorded **14,935,461,888 bytes free disk**,
**1743.12 MiB swap**, RAM **8,589,934,592 bytes**, unchanged Docker
**4,106,604,544 bytes / eight CPUs**. No running containers, model/controller
processes or listeners on 3000/8000/8080/8180/5432/6379/9092/9094/11434/11435/11436
remained. Native frontend and watcher terminated. All eleven inventoried dedicated
volumes were preserved, together with all other existing data/artifacts/vectors.
Three temporary dedicated qualification identity grants were revoked without
changing device or source records. Eleven inspected private model registry flags
remain resource_approved=false. No model lease/attestation was created to close.
No model RSS/tokens/latency measurement exists because no model ran.

Safe evidence, exact command/exit records, current hashes, drift, SQL snapshots,
resource samples and cleanup proof remain ignored under
`.local/phase10/qualification-20261020`; credentials remain mode-0600/private.
The original frozen hash file and proposal remain preserved, not silently refreshed.

**Remaining mandatory blocker: real draft acceptance requires explicit operator
review/authorization of the corrected source fingerprint above before the existing
single frozen case can execute.** Offline implementation/qualification gates now
pass; numerical resources pass at closure but require fresh checks before any later
activation. No inference retry or extra diagnostic is permitted by these results.
General agent reasoning, real vision, semantic entailment, arbitrary tools/external
actions, sustained load, production deployment and Phase 8 Kubernetes/NetworkPolicy
limitations remain outside the established local scope.

Only README/architecture and the existing Phase 10 audit/evidence/manifest were
updated in this continuation; production, tests and frozen proposal were unchanged
during qualification. Candidate remains **20 text files, 10 modified / 10 added**.
Main/HEAD stays `7765b33736c28ccc560fc8269bb5fc4b9b050518`, index empty, no remote;
Phase 1–9 history and audits are intact. No staging/commit/push, installation,
model download, paid/cloud inference, external message, deployment or Phase 11.
Required external spend $0; host compute unpriced. **PHASE 10 NOT COMPLETE —
STOPPED AT THE EXPLICIT FROZEN-SOURCE AUTHORIZATION BOUNDARY.**

## October 20 — frozen-source reconciliation, no model activation

Operator scope was source reconciliation and revised proposal preparation only.
Reversing exactly four hunks in the qualified `drafts.py` reconstructed the original
frozen `8ce187f969f521981b10ea977f264bdad226fd1ad713e0907d5564a3ed67407e` hash exactly.
Current source remains
`b9c239154da11ed8acbbf90816e939c35c96a919184e9f97bb53a6fa0af92881`.
The hunks import SystemClock, supply it only to the owned-draft audit helper, add
REQUESTED before the existing QUEUED audit, and add EVIDENCE_VERIFIED/comment after
final validation in the existing proposal transaction. QUEUED already existed.
No model prompt/schema, evidence selection, authorization/privacy, routing, budget,
payload, artifact identity or approval/execution authority changed.

Reviewed the preceding actual 47 focused/747 backend passes, controller/browser/
Kafka evidence and live unique UTC milestones. Production/tests match that fully
qualified snapshot; no full suite was rerun for documentation-only reconciliation.
All other original frozen production hashes match, as do all 20 qualified candidate
hashes before these documentation edits. Previously explained test/report changes
are distinct from production changes. No unexplained drift was found.

Fresh checks recomputed the unchanged 96-token selection prompt and GroundedSelection
schema hashes and the 469/512 context bound. An enforced read-only transaction
verified the original owned ACTIVE fixture, exact subject/predicate/value/quote and
`8dbd48c85725bf97c29be220182aa1ae8ff52a2f32165bd745b1dfcd691de827` source binding.
Frozen request and LOCAL_REAL owned-draft counts remain zero. Only the existing
isolated qualification PostgreSQL and one 192 MiB metadata-check process ran;
no application API/worker or model was started. Database/container stopped in
finally; no application rows were written or fixture records recreated.

Fresh read-only hashing matched both original/96-token Qwen manifests, all referenced
blob sizes/digests including tensor/template/parameters, and all seven approved BGE
files. No weights were loaded. Private model configuration was not edited. Initial
swap was 1695.06 MiB and free disk 14,104,352 KiB; this metadata check is not a future
resource attestation. Runtime owner/device/controller authentication, private overlay
freeze and fresh passing resources remain required after a later explicit approval.

Prepared `docs/phase-10-real-acceptance-proposal-revised.md` (R1), with original and
qualified hashes, exact differences, regression evidence, unchanged request/body,
full production freeze and artifact identities. The original proposal retains its
`19319380e993f7e4d9aeb4333e8117457642d917bea55139575a5dfd096d02a7` file hash, and
`.local/phase10/source-review.json` remains historical. R1 proposes replacement of
only the explained source freeze; it does not itself reconcile authorization or
consume/renew any execution allowance. Scope remains one authenticated frozen POST,
at most one Qwen generation, zero BGE/retries/actions and all original safety gates.

Review evidence is ignored under `.local/phase10/reconciliation-20261020`. Candidate
now contains **21 text files, 10 modified / 11 added**, solely from adding R1 and
updating existing audit/manifest notes. No production/test/configuration/model
change, draft submission, paid/cloud call, external message, Git staging/commit/
push/remote or Phase 11. Phase 1–9 HEAD/history are preserved. **R1 READY FOR
EXPLICIT OPERATOR APPROVAL; NOT APPROVED / NOT EXECUTED. PHASE 10 NOT COMPLETE.**

Final reconciliation check at **01:40:03 America/New_York** found no running
containers or relevant listeners, eleven private real registries disabled, empty
index and no remote. Free disk **14,523,179,008 bytes**, swap **1687.06 MiB**;
no passing model attestation was created. R1 proposal file SHA-256 is
`8af356e0b97bb325b896af5b3023ebb1dbfd799159f4097c73efa1ec503e2d95`.
Original proposal hash, identical request body, all qualified production hashes,
21-path inventory, syntax/text checks, bounded credential shapes and Git whitespace
passed. These are integrity checks, not a comprehensive security certification.
**STOPPED AFTER RECONCILIATION; AWAITING EXPLICIT OPERATOR APPROVAL.**

## October 20 — authorized R1 preflight, device-registration refusal

Approximately **02:00–02:02 America/New_York**. The operator explicitly approved
R1 and `drafts.py` SHA-256
`b9c239154da11ed8acbbf90816e939c35c96a919184e9f97bb53a6fa0af92881`: one authenticated
frozen draft POST, at most one Qwen generation, zero BGE/retries/external actions.
**Outcome: BLOCKED / NOT EXECUTED; PHASE 10 NOT COMPLETE.** This approval resolved
the earlier source mismatch; it did not waive device registration or any other gate.

### Passed preflight and precise failure

Verified the approved R1 file hash
`8af356e0b97bb325b896af5b3023ebb1dbfd799159f4097c73efa1ec503e2d95`, all frozen
production/qualified source hashes, four documented audit-only changes and exact
request-body fingerprint. No unexplained source drift occurred. Fresh checks
verified both existing Qwen manifests and every referenced blob, all seven pinned
BGE files, Ollama client 0.35.1 and the unchanged loopback sandbox. An actual
sandboxed external TCP attempt was refused. No model/server was loaded or started;
this does not certify runtime behavior or comprehensive network security.

Initial resource snapshot: **1679.06 MiB swap**, **13,748,121,600 bytes free disk**.
Both thresholds passed. Prepared only a private mode-0600 scoped Qwen config/key
and one-hour attestation, preserving managed SELECTION_V1/QWEN2_CHATML_0351,
context 512/output <=96/CPU threads 2/GPU layers 0/temperature 0/concurrency one,
startup 30 s/inference 8 s and Qwen 2048 MiB ceiling. BGE config stayed empty/disabled.
The approved private overlay bound source/artifact files read-only and retained
existing caps; only PostgreSQL/Redis/backend/gateway were started from existing
images in `nova-phase10-qualification` with pull=never/no build. No workers,
controller, Ollama or model were started before the failed prerequisite.

An enforced read-only transaction recomputed the exact prompt/schema hashes,
469/512 bound and frozen owned ACTIVE fixture binding. Frozen request and real
owned-draft row counts were zero. Identity ownership and existing roles matched.
The subsequent explicit device check failed: the task's owned DESKTOP origin
`00000000-0000-4000-8000-000000000010` has **no DeviceRegistration row**.
The task is still `9b363f16-1c38-46ff-a190-b674b7b28ed8`, owner
`00000000-0000-4000-8000-000000000001`. This is the precise
**DEVICE_REGISTRATION_MISSING** boundary; it is not resource, model, JSON,
citation, privacy-after-generation or source-fingerprint failure.

No existing device was enrolled or altered and no different device was substituted.
The pre-existing dedicated identity remains disabled from prior cleanup, with the
same owner and roles; token renewal had not occurred. Thus authenticated API
execution readiness was not established, and no successful authenticated metadata
read or draft POST is claimed. The original proposal's enabled-grant wording was
an unmet prerequisite, not fresh proof of registration. Legacy application auth
compatibility is not used to bypass R1's stricter enabled-registration requirement.

### Actual scope and verification limits

- Authenticated real draft POSTs **0**; Qwen generations **0**; BGE calls **0**;
  inference retries **0**; external actions/messages **0**.
- No actual draft/job/proposal/request trace ID exists. The frozen idempotency key
  remains unsubmitted; no post-attempt marker was created.
- Model answer/index/tokens/latency/peak RSS are **NOT MEASURED / NOT APPLICABLE**.
  No model attempt or valid abstention occurred.
- Frozen source UUID/quote/binding were verified before execution, but positive
  model citation acceptance and final post-generation privacy/conflict validation
  were **NOT EXERCISED**. No unsupported claim or fabricated citation was accepted.
- No approving ApprovalDecision, ActionExecution or external message was created
  by this scope. No new scoped identity grant/token was issued.

Read-only diagnosis distinguished missing registration from wrong ownership or a
disabled registration. Its first metadata container used `/inspect.py`, shadowing
Python's standard `inspect` module and causing ImportError before querying. The
same read-only check at `/device_check.py` then returned the precise metadata.
This corrected diagnostic tooling only: no acceptance POST or inference was retried,
no production/configuration validation was weakened and no failed check is counted
as a pass. Only the dedicated DB and a 192 MiB read-only metadata container were
briefly restarted for diagnosis, then stopped without application writes.

### Cleanup, retained qualification and next boundary

Verified fresh scoped Qwen `resource_approved=false`; the API/worker overlay was
reset to FIXTURE with empty real config/key and invalidated resource environment.
The approved active overlay was preserved separately before resetting its operational
successor. Scoped attestation is explicitly closed with operator/model approval
false. Prior private configs stayed untouched/disabled. No controller/model lease
existed or unload call was needed. Existing scoped identity remains revoked; there
was no newly issued grant to revoke.

The resource watcher recorded **12 snapshots**, swap **1663.06–1671.06 MiB**,
free disk minimum **13,745,176,576 bytes**, no resource violation. At **02:02:39**
independent cleanup recorded **1663.06 MiB swap**, **13,744,967,680 bytes free disk**,
RAM **8,589,934,592 bytes**, Docker **4,106,604,544 bytes / eight CPUs**, unchanged.
No running containers, model/controller processes or application/model listeners
remained. All eleven inventoried dedicated volumes and all original application
data/vectors/artifacts were preserved. No pruning, restart, download or install.

The unchanged qualified source still matches the latest actual evidence: backend
747/one real skip; focused 47; controller 13; Go race/vet; frontend checks; browsers
38+15+3+2; Kafka/queued-worker/broker recovery; golden 104/104, 10/10, 25/25 and
security/privacy regressions. Those are retained valid qualification results, not
new model measurements; no unnecessary heavy suite was rerun.

Safe evidence remains ignored under `.local/phase10/r1-acceptance-20261020`;
closed private settings/key/attestation under `.secrets/phase10-r1-acceptance-20261020`.
The exact approved pre-execution R1 document is preserved there; its source/request/
criteria remain unchanged, with an outcome appendix added publicly afterward.
Original October 19 proposal and freeze remain historical evidence.

**Remaining mandatory blocker:** enablement/authorization of an actual owner-matching
registration for the existing device, followed by valid scoped owner/device
credentials and a separately authorized frozen real attempt. No such enrollment
or further attempt is authorized by this failed preflight. The real positive
acceptance remains open, so Phase 10 cannot be marked complete. Current scoped
approval is closed and does not imply a retry.

Only existing Phase 10 status documentation/R1 outcome was updated; no production
or test source changed. Candidate remains 21 text files, 10 modified / 11 added;
main HEAD `7765b33736c28ccc560fc8269bb5fc4b9b050518`, index empty, no remote.
Phase 1–9 history/measurements are preserved. No staging/commit/push, paid/cloud
service, external message/action, deployment or Phase 11. External spend $0; host
compute unpriced. **PHASE 10 NOT COMPLETE. STOPPED AFTER BLOCKED R1 PREFLIGHT.**

## October 20 — supported Desktop enrollment recovery, inference excluded

Recovery and checks approximately **02:19–02:21 America/New_York**. **DEVICE
REGISTRATION PASS; CREDENTIAL VALIDATION PASS before cleanup. PHASE 10 NOT
COMPLETE.** The operator explicitly authorized enrollment of the existing Desktop
in the isolated Phase 10 environment, and explicitly required stopping for fresh
real acceptance approval afterward. No earlier real scope was reused.

### Root cause and supported recovery

Reviewed `security/models.py`, `security/api.py`, `security/cli.py`, authentication,
Phase 8 runbook and existing device-registration regression, together with R1 and
latest Phase 10 evidence. Device/identity provisioning and explicit enrollment are
separate mechanisms. Seed/CLI provisioning creates/reuses Device and Identity
records but does not create DeviceRegistration. Until explicit enrollment, the
compatibility view reports enabled/version 0 and the local authenticator accepts
a valid owner-bound version-0 credential. That does not satisfy R1's stricter
requirement for an actual enabled registration row.

The earlier preparation used CLI identity provisioning and existing device contexts;
no supported enrollment was recorded. This omitted step explains the observed
missing registration. Read-only metadata found no registration/version/revocation
row, rather than a disabled or foreign-owned registration. Absence alone does not
prove that no privileged historical deletion ever occurred; no such cause is
asserted. This is a recovery of the missing explicit enrollment step, not a schema
migration, fabricated authentication or new hardware pairing capability.

Used only the existing operator CLI and authenticated API in
`nova-phase10-qualification`, with FIXTURE/default-empty real provider settings:

1. Verified the original task/device/owner and unchanged existing identity roles.
2. Renewed that existing scoped identity through the supported local CLI, using
   the actual server signing key and owned DESKTOP context; no hand-crafted token,
   substituted device or expanded role set.
3. Authenticated `/auth/me` and owned task reads using the bootstrap credential.
4. Submitted exactly one `POST /api/v1/auth/devices/register` with
   `device_id=00000000-0000-4000-8000-000000000010`.
5. API returned enabled=true, version=1, simulation=true and new_token_required=true.
6. The old version-0 credential then correctly returned **401**.
7. Reissued the scoped credential through the existing CLI. Actual API reads and
   the application's `authenticate` path passed with the current identity and
   device versions; no security check was bypassed.

No challenge/interactive pairing is implemented for these documented simulated
local device identities. No device credential was invented. No direct database
insert/update was used to enroll; the existing API committed its supported mutation.
There was no failed enrollment or enrollment retry and no duplicate registration.

### Actual binding, preflight and retained qualification

Read-only verification found exactly one registration, enabled **version 1**, for
Desktop **00000000-0000-4000-8000-000000000010**, owner
**00000000-0000-4000-8000-000000000001**. Principal, Identity, DeviceRegistration,
Device and task all matched. The existing identity row is
`c8492b8d-7b54-4bdd-949e-65b75cad91c1`; its version was 5 at successful credential
validation. It was subsequently revoked/incremented during cleanup, so that
successful token is not claimed to remain valid. Device registration remains
unchanged/enabled at version 1 after cleanup.

Qualified source hashes, original proposal, approved R1 prefix and exact frozen
request body hash still match. Prompt/schema hashes and conservative **469/512**
bound were recomputed. Original owned ACTIVE source
`7d1049cb-06b9-49c4-ad06-a8db5036480a`, subject/predicate/value/full quote and
`8dbd48c85725bf97c29be220182aa1ae8ff52a2f32165bd745b1dfcd691de827` binding remain
unchanged. Frozen request and LOCAL_REAL draft counts are zero; no competing
QUEUED/RUNNING owned-draft job exists. No fixture was regenerated.

Fresh read-only artifact checks verified the existing Qwen tensor, both original/
96-token alias manifests and all referenced blobs, plus all seven pinned BGE
files. The unchanged residency controller was started only for authenticated static
`GET /v1/models` from the backend to verify bearer authentication and host reachability.
No acquire, runtime health/generation/embedding request, lease or model process ran.
The loopback-only sandbox profile bytes matched the reviewed profile. A private
readiness snapshot recorded measurements with model_load_approved=false and
inference_authorized=false; it is now closed and is not model activation authority.
Actual runtime load/fit remains untested by this recovery.

Production/test files did not change, so the latest 747 backend/one explicit real
skip, 47 focused, 13 controller, Go race/vet, frontend/build, browser 38+15+3+2,
Kafka/recovery and golden 104/104, 10/10, 25/25 evidence remains applicable. Existing
`test_phase8.py::test_device_registration_and_revocation_enforced` covers the same
registration epoch/old-token refusal path. No heavy suite was unnecessarily rerun
or falsely reported as new. No new deterministic test failure occurred.

### Cleanup and remaining authorization boundary

Initial measurements: **1655.06 MiB swap**, **13,708,656,640 bytes free disk**.
Five boundary measurements all retained swap 1655.06 MiB and disk >=5 GiB. RAM
**8,589,934,592 bytes**, Docker **4,106,604,544 bytes/eight CPUs**, unchanged.
Independent final cleanup at **02:21:36** recorded **1655.06 MiB swap** and
**13,713,174,528 bytes free disk**. No threshold, model limit or allocation changed.

Revoked the temporary scoped identity through the supported CLI; a final API call
using the refreshed credential returned **401**. Preserved the enabled device
registration, version 1, as required by enrollment lifecycle. Stopped the metadata
controller and all task-owned application/database services. No running container,
model/controller process or relevant listener remained. FIXTURE/empty real configs
were independently verified; all twelve inspected private real flags remain false.
The readiness snapshot is closed, model/inference approval flags false. All eleven
inventoried volumes, existing databases/vectors/artifacts and controlled records
are preserved. No model acquisition, unload or inference attestation was needed.

Evidence is ignored under `.local/phase10/device-recovery-20261020`; private scoped
credentials/key/closed readiness snapshot remain under `.secrets/phase10-device-recovery-20261020`
with credential files mode 0600. No private token/key is in source or request URLs.

**Actual real scope: zero draft POSTs, zero Qwen generations, zero BGE calls,
zero inference retries, zero external actions/messages.** Registration recovery
and preparation are complete. R1 is ready for a **fresh explicit operator approval**,
subject to reissuing scoped credentials and fresh activation-time gates. Temporary
credential revocation at closure is expected cleanup, not a registration failure.
The only remaining mandatory gate is the separately authorized positive real draft
and its required source/privacy/proposal/cleanup checks. This instruction explicitly
does not authorize that request. Do not reuse the previous closed approval.

Current `drafts.py` remains
`b9c239154da11ed8acbbf90816e939c35c96a919184e9f97bb53a6fa0af92881`; request, evidence,
model, limits and acceptance criteria are unchanged. Only status documentation/R1
readiness was updated. Candidate remains 21 text files, 10 modified / 11 added;
index empty, main/HEAD `7765b33736c28ccc560fc8269bb5fc4b9b050518`, no remote or Git
write. Phase 1–9 history is preserved. No downloads/install, cloud/paid inference,
external action, deployment or Phase 11. **PHASE 10 NOT COMPLETE. STOPPED FOR
FRESH REAL-DRAFT AUTHORIZATION, AS EXPLICITLY REQUIRED BY SECTION 4.**

## October 20 — authorized R1 real attempt: resource failure

Executed approximately **02:43–02:44 America/New_York**. **REAL DRAFT ACCEPTANCE
FAIL. PHASE 10 NOT COMPLETE.** The operator explicitly authorized exactly one
R1 draft POST and at most one Qwen generation after device recovery. The current
approved R1 text, SHA-256
`0ee038ebbd97ec4cd01c3d8172a2ff3582131120d281caf351dedff1ca900d67`, was copied
before execution to ignored `.local/phase10/r1-final-acceptance-20261020/approved-proposal.md`.
Earlier blocked attempts/recovery approvals remain closed and historical. The
original proposal is unchanged; no source, prompt, schema, fixture, acceptance
criterion or model parameter was corrected during this attempt.

### Frozen inputs, credentials and prerequisites

All R1 production/dependency fingerprints, qualified Python/TypeScript source,
original proposal, prompt/schema, exact body, original fixture/source binding and
469/512 conservative budget passed. Read-only SQL confirmed zero prior frozen
request rows, zero LOCAL_REAL owned drafts and no competing queued/running owned
jobs. Existing Qwen/alias manifests and every referenced blob, plus unused BGE
files, passed fresh size/SHA-256 checks before and after execution. Qualified
`drafts.py` remains `b9c239154da11ed8acbbf90816e939c35c96a919184e9f97bb53a6fa0af92881`.

Owner `00000000-0000-4000-8000-000000000001`, task
`9b363f16-1c38-46ff-a190-b674b7b28ed8` and original Desktop
`00000000-0000-4000-8000-000000000010` matched. The existing enabled registration
remained version 1. The existing CLI legitimately renewed the revoked identity,
without role expansion; fresh credentials authenticated and matched current
identity version 7/device version 1. Revoked credentials were not reused. A
fresh scoped private one-hour attestation was issued. API/worker private
controller bearer authentication and Docker-to-host reachability passed through
static inventory only, with no acquire or warmup. Read-only mounts, managed
SELECTION_V1/QWEN2_CHATML_0351 configuration and BGE-disabled state passed.

Initial listeners/processes/containers were absent. The reviewed loopback-only
sandbox matched; a bounded sandboxed external TCP attempt was denied. Qwen kept
`nova-qwen-phase9-rag96`, context 512/output 96, CPU threads 2/GPU layers 0,
temperature 0/concurrency 1, RSS ceiling 2048 MiB/startup 30 s/inference 8 s.
Runtime logs confirm `-c 512 -np 1 -ngl 0 -t 2`, offline loading and zero GPU
offload. No model/package/runtime download, alias change or limit increase occurred.

### Exact scope and failure boundary

| Observation | Actual result |
| --- | --- |
| Frozen idempotency/request key | `15d88b00-b223-429e-88cd-c1a6b160daf2` |
| HTTP correlation | `34a7dea9-c2fc-4672-bd28-265da406cff7` |
| Draft/context event ID | `2ac3dd25-5854-443a-8bd7-67f8dc37fa76` |
| Worker/request trace | `57b6aea1-c387-4ac5-b510-8910e1869851` |
| Authenticated exact draft POST | **One**, HTTP **202** |
| Qwen inference request attempts | **One**, interrupted during loading; zero completed responses observed |
| BGE calls / inference retries / extra generations | **0 / 0 / 0** |
| Model answer / evidence index | **Not produced/observed** |
| Expected original citation | `7d1049cb-06b9-49c4-ad06-a8db5036480a`, full quote unchanged |
| Final positive citation/privacy/conflict acceptance | **NOT REACHED** |
| Job ID / proposal ID | Not independently read after shutdown / no proposal observed |

The request was the exact frozen query/body, not a diagnostic or alternate fixture.
The worker logged OWNED_DRAFT_RUNNING, acquired Qwen and sent its sole chat request.
During CPU weight loading host swap exceeded the unchanged strict 2048 MiB gate.
The controller/watchdogs refused the call; worker HTTP returned **409 Conflict**
from the controller and logged **OWNED_DRAFT_FAILED at 02:44:14.657**. The host
operator loop also stopped at RESOURCE_GATE; its watcher stopped only task-owned
services. This is an **executed acceptance failure on resources**, not a pre-POST
block, abstention, invalid claim or successful draft. No inference was retried.

No supported answer/index or validated positive citation exists. The final
proposal/completed-job acceptance checks were not reached. The database was not
restarted to inspect terminal rows while swap still failed; the worker's FAILED
milestone is log evidence, not an independent post-shutdown SQL verification of
job state/count or proposal/decision/execution counts. No approval, execution or
external-message request was issued. The generation failure path precedes proposal
creation in the frozen code; no pending proposal or approving decision is claimed.
The required one DONE job/one PENDING_APPROVAL proposal gate therefore did not pass.

### Measurements and evidence limits

| Measurement | Actual scope/value |
| --- | --- |
| Draft POST HTTP wall time | **925.610 ms** (enqueue, not generation) |
| Server POST latency | **917.950 ms** |
| Input/output tokens / finish reason | **UNKNOWN**, no completed response |
| Model-call latency / end-to-end completion latency | **Not measured to a successful/validated terminal response** |
| Peak sampled runtime RSS | **UNKNOWN / not durably recorded** |

The unchanged controller's stop path signals/checks runtime descendants, then
calls the same resource gate while assembling its final residency record. That
last resource check raised RESOURCE_GATE before `residency.json` was written.
Thus no persisted peak RSS, acquisition/inference timing or usage record survives
for this attempt. A normal model-response observation was also absent. This is
an observed failure-path telemetry limitation; it was not patched during frozen
execution, and missing numbers are not reported as zero. The native empty unload
command was cleanup, not a second generation. Independent process/listener checks
below establish the stopped state despite that final recording exception.

| Resource boundary | Free disk bytes | Swap used MiB |
| --- | --- | --- |
| Initial preflight | 13729370112 | 1647.06 |
| Immediately before single POST | 13724012544 | 1647.06 |
| Last passing watcher sample, 02:44:14 | 13728231424 | 1948.50 |
| Driver stopped snapshot | 13727252480 | **2072.62 — FAIL** |
| Final independent snapshot, 02:45:44 | 13723414528 | **2064.62 — FAIL** |

The first over-threshold sample was not saved with a numeric value by the watcher;
its refusal timestamp is retained separately. Do not infer an instantaneous maximum
from these snapshots. RAM remains 8589934592 bytes, Docker 4106604544 bytes/eight
CPUs. The host-wide cause of swap growth is not established. No resource threshold,
allocation, cache, volume or host service was changed to obtain a pass.

### Cleanup, preserved qualification and remaining gates

Fresh identity credentials were revoked through the existing CLI; the retired
token then returned **401**. The enabled version-1 device registration was not
revoked or replaced. Scoped resource approval is false, attestation closed with
approval flags false, and the scoped API/worker launch overlay returned to
FIXTURE/empty real settings. All **13 inspected private model registry approval
flags are false**. No active controller/lease/model remains. Independent inventory
found no model/descendant/controller process, no running container and no listener
on 3000/8000/8080/8180/5432/6379/11434/11435/11436. All eleven inventoried dedicated
volumes still exist; protected application data/vectors/artifacts were preserved.
No application volume or cache was deleted. An interrupted real job must never be
regenerated by restarting a worker; this authorization is consumed and closed.

Existing final-source qualification remains applicable: **747 backend/one real
opt-in skip, 47 focused, 13 controller**, Go race/vet, frontend lint/typecheck/build,
58 browser passes across four invocations, fixture Kafka/duplicate/recovery and
golden baselines. No production/test source changed, no heavy suite was rerun,
and those deterministic/local-service results are not real model quality evidence.

Safe execution evidence/logs are ignored under
`.local/phase10/r1-final-acceptance-20261020`; mode-0600 scoped private files are
under `.secrets/phase10-r1-final-acceptance-20261020`. A preparation-only harness
syntax error was corrected before any services/submission; it caused no inference
or retry. Operational evidence is not part of the source candidate.

Remaining mandatory gate: successful bounded real draft acceptance and its final
job/proposal/current citation/privacy/authorization/no-action verification, under
fresh passing resources and any separately authorized future scope. This failed
case does not authorize another POST or generation. General reasoning/vision/
production/streaming qualification remains outside the bounded scope, with earlier
limitations unchanged. **PHASE 10 NOT COMPLETE.** No staging/commit/push/remote,
download/install, cloud/paid call, external message, deployment or Phase 11.
External spend $0, local compute unpriced. **STOPPED AFTER FAILURE AND CLEANUP.**

Final reporting recheck at **02:48:50 America/New_York**: disk **13723652096 bytes free**,
swap **2056.62 MiB used**. No containers/model/controller processes/relevant
listeners; scoped flags false/attestation closed/FIXTURE launch settings confirmed.
Git candidate exactly **21 regular UTF-8 files, 10 modified / 11 added**, matching
the reviewed manifest; index empty, no remote, main/HEAD unchanged at
`7765b33736c28ccc560fc8269bb5fc4b9b050518`. Earlier checkpoint history and the
original proposal remain intact. Source syntax, whitespace and bounded credential
shape checks passed; no production/test changes or additional tests/inference.
**STOPPED. REAL R1 ACCEPTANCE FAILED; PHASE 10 NOT COMPLETE.**

## October 20 — R1 resource diagnosis and R2 offline preparation

**Diagnosis/focused offline regression completed. No real inference or draft
submission. PHASE 10 NOT COMPLETE.** R1 authorization remains consumed; this task
permits diagnosis, justified controller correction and a new proposal only.

### Confirmed R1 mechanism and unavailable causal evidence

Reviewed the exact R1 controller/provider/source lifecycle, alias/template/blob
configuration, host watcher, runtime/server/runner logs and worker/audit records.
The Qwen server becomes READY before weights load: the sole chat request triggers
lazy CPU loading. Logs show one Ollama server at 02:44:12.213 and one runner at
02:44:12.706, CPU-only `-c 512 -np 1 -ngl 0 -t 2`; loading status 02:44:12.960.
No evidence of another runner, duplicate loading or BGE activity was found. The
server and runner are separate cooperating processes, not two loaded models.

Swap was **1647.06 MiB at 02:44:12.309**, immediately before lazy loading, then
**1948.50 at 02:44:14.318**. The controller returned chat HTTP 409 at 02:44:14.535;
the worker logged FAILED at 02:44:14.657. The host watcher refused by 02:44:16.331
but saved no numeric violating sample. The stopped snapshot was **2072.62 MiB**:
425.56 MiB above pre-POST and beyond the strict 2048 ceiling. The exact first
crossing time/value, instantaneous maximum and per-process RSS are unavailable.
Recorded disk samples remained above 5 GiB. Eight-second inference, 30-second
startup and 2048 MiB Qwen RSS ceiling were unchanged; no alternative prompt/profile
or retry was used.

Confirmed failure mechanism: resource refusal during loading, followed by worker
failure with no proposal. CPU weight loading plausibly contributed, but absent
contemporaneous process/RSS/host pressure samples prevent assigning the swap
increase quantitatively to Qwen or unrelated applications. No model leak, duplicate
load or sole-cause claim is established. A current bounded process snapshot shows
memory held by the virtualization VM, IDE helpers and Docker; it is not evidence
of their R1 consumption or causality. No orphan model process remained to reclaim.
No user application/process was killed, restarted or modified.

Telemetry defect: Runtime.stop performed termination then evaluated enforcing
resources() while constructing the record. RESOURCE_GATE interrupted that expression
before records were written, field reset and the remaining listener checks. Host
independent checks established termination, but the controller's own final record
and RSS/timing were missing. The failure still poisoned the controller and did not
permit fallback/retry. Safe refusal and independently verified shutdown must not
be confused with a fully recorded successful unload. Historical unknowns remain
unknown; new code does not retroactively supply measurements.

### Read-only isolated database outcome

Started only the existing capped isolated PostgreSQL service, used `BEGIN READ
ONLY`, verified transaction_read_only=on, then ROLLBACK, and stopped it. No API,
worker, broker or model was needed. No failed job/fixture row was mutated.

| R1 object | Independently verified result |
| --- | --- |
| Draft `2ac3dd25-5854-443a-8bd7-67f8dc37fa76` | FAILED, DRAFT_INVALID, LOCAL_REAL |
| Key `15d88b00-b223-429e-88cd-c1a6b160daf2` | Exactly one row for the owned task |
| Job `6bfba979-0483-4c6b-86df-3d5a89fa434e` | DEAD, attempts=1, result_id=null |
| Outbox `15e47750-22d7-4a5e-8dd2-340ffda9a6d2` | ContextEvent.changed, PUBLISHED, attempts=1 |
| Inbox | One completion each: proactive, projection, audit |
| Proposal / ApprovalDecision / ActionExecution | **0 / 0 / 0**, scoped to R1 trace |
| Audits | REQUESTED, QUEUED, RUNNING, FAILED; no EVIDENCE_VERIFIED or pending |

Trace `57b6aea1-c387-4ac5-b510-8910e1869851`; audit times respectively
02:44:08.705926, 02:44:08.706225, 02:44:10.273406, 02:44:14.657356 local.
Residency is host JSON evidence, not a database table; R1 has no final residency
JSON or completed model-observation record. Database failure is terminal and no
orphan pending proposal needs cancellation. Historical prior uncertainty about
these counts is resolved by this new read-only inspection, not rewritten.

A second bounded read-only application import/check reconfirmed the exact controlled
fixture/source binding, prompt/schema and 469/512 budget. It expects the single
historical FAILED real row rather than asserting no prior real requests. It also
found zero rows for R2's newly reserved key. All existing model/alias/blob and BGE
file hashes were freshly verified without importing an ML loader or starting models.
The original/R1 acceptance documents and frozen application production source are
unchanged by this diagnosis.

### Corrections and deterministic tests

Only production correction: `scripts/phase9_residency.py`:

- Recheck resources after acquisition and before inference transport; refuse and
  release without invoking transport when resources have already failed.
- Preserve last sampled numeric resources and a refusal timestamp. Atomically
  replace the JSON record at STARTING/READY/inference start/completion and shutdown,
  rather than relying solely on a successful final stop-time check.
- Terminate and check descendants/listeners before persistence; record the failed
  final resource sample and stopped outcome before propagating resource failure.
  Controller poisoning/refusal remains. Unmeasured sampled RSS is null, not zero.
- An actual filesystem replacement failure still terminates the child and poisons
  acquisition. The last valid record remains; it does not falsely verify shutdown.
  Atomic replacement is not a disk-loss/fsync durability certification.

No model configuration, prompt, schema, supported answer, source selection,
authorization, citation/privacy/conflict, worker generation policy or action
permission changed. Startup/inference/lease/RSS/Docker/CPU/context/output ceilings
are unchanged. New tests are deterministic infrastructure/component/application
checks, not real-model load, instruction-following or quality measurements.

| Executed current-source check | Result |
| --- | --- |
| Final owned-draft PostgreSQL focused suite | **50 passed, 3.52 s** |
| Backend Ruff/format/pip | PASS, 112 app/test files formatted, no broken requirements |
| Final host controller/process suite | **17 passed, 0.125 s**, no models |
| Controller script Ruff/format | PASS, two files formatted |
| Candidate syntax/whitespace/source inventory | PASS, final review below |

Four new host cases cover strict threshold retention, swap change before generation,
loading-time refusal with a non-model child/cleanup/poisoning, and failed record
replacement with preserved prior JSON. Three new backend cases (two parametrized
refusals and one jobs-mode test) establish durable FAILED/DEAD, no automatic or
idempotent/delayed duplicate generation, zero proposals/approvals/executions, no
verified/pending milestone, and jobs-mode polling without opening a Kafka client.
Existing privacy/ownership/authority/rollback tests in the focused suite passed.
Initial 49 focused passes preceded the added topology check; final 50 are the
current focused snapshot, not an additional full backend pass. An inspection-helper
syntax issue was caught and corrected before that helper started any services.
During source review, opener initialization and readiness-write exception placement
were corrected before the final host checks; no real runtime executed.

Tests used existing images/pull=never/current read-only source, dedicated `_test`
PostgreSQL/Redis and fixture/offline settings. DB/runner retained 512 MiB each,
Redis 48 MiB, one/two CPUs; scripts lint ran network-disabled at 128 MiB/one CPU.
Full backend/Go/frontend/browser/Kafka/golden suites were not rerun for this isolated
controller correction; earlier complete qualification remains historical and does
not establish real-model safety for the new controller or staged topology.

### R2 proposal and resource limits

[The new R2 proposal](phase-10-real-acceptance-proposal-r2.md) freezes current
application/controller/test fingerprints and reserves fresh key
`b1e801de-2d30-4444-9341-fb1efcc36df8`. Same owner/task/source/query/expected noodles,
original UUID/full quote and schema/prompt/artifacts; no fixture substitution.
R1 key and failed row must never be resubmitted, revived or edited.

Proposed staged operation queues one authenticated request with the jobs worker
stopped, waits for its unique durable job, stops Kafka/publisher/consumer/API/Redis,
then uses only PostgreSQL/controller/jobs worker for generation. Jobs-mode's source
and deterministic no-broker test support this separation; live staged startup is
not yet qualified. No security or event policy changes; delayed other inbox groups
remain honestly pending. Resolved `--no-deps` launch must not restart dependencies.

Add proposed initial/pre-acquisition swap **<1024 MiB** headroom checks, while the
continuous hard ceiling remains **<2048 MiB**, disk >=5 GiB and Qwen <=2048 MiB.
This stricter operator stop condition is conservative, not a fit guarantee or a
resource-limit increase. The operator may save/close unrelated applications;
no automatic host/Docker restart, swap change, process kill or cache/volume deletion.
Fresh supported credentials/current enabled Desktop registration, private controller
bearer/sandbox/artifact/configuration checks and a scoped attestation remain
mandatory. No new active config or passing attestation was issued here.

R2 is **ready for review, NOT APPROVED / NOT EXECUTED**. Current swap lacks the
proposed headroom, and the exact scoped launcher/overlay must be reviewed/fingerprinted
before approved use. One new authenticated POST/at most one Qwen attempt/zero BGE/
zero retries; success still requires model-produced noodles/index 0, independently
verified UUID/quote/current authorization/privacy/conflicts, exactly one DONE job
and PENDING_APPROVAL proposal, no approval/execution/message, verified cleanup.
No new inference authorization is inferred from diagnosis or changing resources.

**PHASE 10 NOT COMPLETE.** R1 failed; future R2 needs fresh scoped explicit approval,
resource headroom and successful real acceptance. No commit/push/remote, deployment,
external action, download/install, model generation or Phase 11. All prior evidence
and protected data/volumes remain preserved. Safe diagnosis evidence is ignored
under `.local/phase10/r2-resource-diagnosis-20261020`.

Final diagnosis cleanup, **03:06:33 America/New_York**: free disk **13716684800 bytes**,
swap **2016.62 MiB**, RAM 8589934592 bytes, Docker 4106604544 bytes/eight CPUs.
Focused-test watcher swap range 2016.62–2016.62 MiB;
no test resource stop. No containers/model/controller processes or listeners on
3000/8000/8080/8180/5432/6379/11434/11435/11436. Thirteen private model approval flags
remain false; previous attestations/credentials stay closed/revoked. Eleven dedicated
volumes preserved. Current head remains Phase 9 `7765b33736c28ccc560fc8269bb5fc4b9b050518`,
index empty/no remote; **24 UTF-8 regular candidates, 12 modified/12 added**,
matching the updated manifest. Original/R1 proposals unchanged; candidate Python
syntax, whitespace and bounded credential-shape scan passed (not comprehensive).
No real inference or POST in this diagnosis. **STOPPED BEFORE R2 APPROVAL.**

## October 20 — complete current-source offline qualification; R2 boundary

Executed approximately **03:09–03:24 America/New_York**, final checks through
03:24:05. **ALL REQUESTED OFFLINE/LOCAL QUALIFICATION AREAS PASS. PHASE 10 NOT
COMPLETE: R2 real acceptance is NOT AUTHORIZED and startup headroom is BLOCKED.**
The operator authorized continued implementation review and local fixture tests,
explicitly withholding R2 inference. **Zero real model loads/generations, BGE
calls, R2 submissions or external actions occurred in this continuation.** R1
remains consumed/failed; its historical measurements and rows were preserved.

### Review and host/resource recovery

Reviewed the complete implementation/audit/evidence/manifest and original/R1/R2
proposals, README roadmap and relevant architecture, draft/source/privacy/auth/
device/outbox/worker/Approval Center code and tests, controller/residency paths,
source diffs and Git inventory. No further demonstrated production defect required
a correction. The prior pre-transport/resource-recording fixes were retained and
qualified against the current source; no prompt/schema/profile/fixture changed.
Only status/qualification documentation changed in the source tree during this task.

Initial swap **2008.62 MiB**, physical RAM **8589934592 bytes**, Docker allocation
**4106604544 bytes/eight CPUs**. vm_stat showed approximately 341 MiB free pages,
2.37 GiB inactive pages and 771 MiB compressed pages; memory_pressure reported
70% under its accounting, not guaranteed allocatable model RAM. Largest current
visible resident processes included IDE renderers/helpers, ChatGPT Classic and
Docker/system processes. These snapshots do not attribute historical swap or
guarantee model headroom. No running containers, NOVA model/server/frontend orphan
or unnecessary task-owned process was found initially. Nothing unrelated was
killed; no host/Docker restart, cache purge, swap manipulation, volume deletion or
allocation increase was used. Task-owned services were staged and stopped normally.

Qualification used bounded sequential stages and two-second disk/swap watchers;
332 recorded snapshots ranged **2000.62–2008.62 MiB swap**, minimum free
disk **13433856000 bytes**, with no resource-stop condition. Existing model hard
thresholds remain swap <2048/disk >=5 GiB and unchanged model RSS/deadlines. Three
final one-second-separated readings all showed **1992.62 MiB** swap,
so the separate R2 startup condition **<1024 MiB FAILS**. No indefinite wait or
unsafe remediation was attempted. Safe offline checks continued despite that
model-startup blocker; Qwen never started.

### Actual final-source results

| Check | Current-source result |
| --- | --- |
| Full PostgreSQL pytest | **750 passed, 1 explicit real-model opt-in skip, 68.70 s** |
| Backend Ruff lint/format/pip | PASS, 112 app/test files formatted, no broken requirements |
| Host residency/controller/process | **17 passed, 0.141 s**, no models |
| Go race/vet | **2 tests PASS**, package 1.021 s, vet exit 0 |
| Frontend lint/typecheck/production build | PASS, installed dependencies |
| Replay batch A | **38 passed, 44.7 s** |
| Replay batch B | **15 passed, 5 explicit auth/OIDC profile skips, 10.7 s** |
| Separate strict local-auth | **3 passed, 6.1 s** |
| Corrected actual local OIDC | **2 passed, 2.5 s** |
| Application Alembic current/check | **0011_inference_registry (head)** / no new upgrade operations |
| Fixture draft/Kafka/duplicate/worker-restart | PASS |
| Legacy Kafka/HITL/duplicate/forgery | PASS, simulated NOT SENT |
| Actual broker outage recovery | PASS, two events, **31.076 s** from restart command |
| Golden FULL/SMOKE/REGRESSION | **104/104, 10/10, 25/25**, zero critical, PASS |
| Cautious negative control | **23/25**, zero critical, expected FAIL/exit 1 |
| R2 staged topology, separate FIXTURE only | PASS, broker/API/Redis stopped during worker generation |
| R2 integrity/controller metadata/read-only fixture | PASS; zero acquire/model calls/POSTs |
| Source/data/volume/credential/cleanup review | PASS, details below |

Browsers cover **58 unique cases across four passing invocations**, with retries=0
and trace=off, plus the separately retained failed OIDC invocation described below.
Replay batches were paced by a complete existing quota window (62 seconds); the
1200/min limit, assertions and timeouts were unchanged. Actual owned queue/cancel,
local auth, OIDC and fixture Kafka flows remain distinct from explicitly scripted
lifecycle/UUID/quote rendering cases. Neither browser nor deterministic results
are real model quality measurements. Full backend includes transaction rollback,
worker concurrency, idempotency, current source/identity/device/privacy revocation,
HITL denial, unsupported output, no retry/no duplicate/no authority and all prior
regressions. No extra production correction was needed to pass these checks.

### Commands and isolation

Backend, from the repository root:

```sh
# Existing capped _test database/Redis and installed test image, current source RO.
docker compose -f compose.yaml -f .local/phase9/final-qualification-20261019/backend-test-overlay.yaml --profile test run --rm --pull never backend-tests sh -c 'pytest -q && ruff check app tests && ruff format --check app tests && pip check'
python3 scripts/test_phase9_residency.py
```

Go used the existing network-disabled nova-gateway-compiler:local at 384 MiB/two
CPUs, source RO, GOPROXY=off/GOTOOLCHAIN=local: go test -race -count=1 -json ./...
then go vet ./.... Frontend used installed npm lint/typecheck/build, Next telemetry
disabled, the existing 768 MiB build/512 MiB server Node heap ceilings. No toolchain,
package, advisory database, image or model download/build/pull was performed.

Integration used only **nova-phase10-qualification**, full Compose base/Phase8/OIDC
and the existing capped qualification overlay. Every up used --no-build/--pull
never. DB/backend/Redis/gateway caps 192/384/64/64 MiB; workers 384 MiB and Kafka/
Keycloak 768 MiB. Backend-test DB/runner remained 512 MiB each, Redis 48 MiB;
mandatory setup refuses cleanup outside _test and verifies migrations/drift.
Kafka stages stopped before OIDC. Native frontend and browser hooks inherited the
correct isolated Compose project/files. Existing protected Phase 9 application/
identity/model/vector volumes were not mounted into this qualification app.

Browser command scopes and all exact command/exit records remain in ignored
`.local/phase10/finish-offline-20261020`; public command structure is unchanged from
prior evidence. Kafka scripts acceptance_phase10.py --inject-duplicates --recovery,
acceptance_phase8.py --inject-duplicates and reliability_phase8.py --tasks 1 --outage
used private fresh tokens and existing bounded overlay-preserving restart wrappers.
No credential was printed or passed in URLs/browser traces.

### Recoverable environment failures, not hidden passes

The first OIDC invocation had **one failed/one passed, 6.1 s**: native frontend
lacked OIDC_PUBLIC_ISSUER/OIDC_INTERNAL_ISSUER, so /auth/oidc could not redirect.
The existing documented URLs were supplied (both localhost:8180 for the native
server), with the same callback, provider and assertions. Both cases then passed.
No production source/security check or browser retry setting changed.

After that passing OIDC run, an operator helper tried to parse its run() return
(None) instead of the already written JSON snapshot. Cleanup still revoked its
grant and stopped services. The written snapshot was independently parsed and
compared successfully; the helper was corrected, without rerunning or relabeling
the failed wrapper as a passing invocation. An additional staged-fixture restart
check confirmed the same metadata again. Final read-only grant inspection initially
used unprefixed table names; PostgreSQL refused the query in its read-only transaction.
Correct auth_ table names returned the expected data; no application row changed.
These operational errors and original logs remain retained, not counted as passes.

### Actual fixture, broker, golden and staging records

- Phase 10 fixture task `67a26ac6-e4e2-45dc-b992-c7ad80f57024`, draft
  `0ab2bd5f-0907-431c-a70b-768776c5d5c1`, proposal `7fb2eda5-349f-478f-96b0-ee994fbb0055`.
  PENDING_APPROVAL before explicit rejection, original UUID/full quote verified,
  no bearer 401/foreign owner 404, approve/execute DRAFT_ONLY. Three duplicates
  caused no extra proposal; forged authority produced three dead letters. Queued
  work survived worker stop/restart, then cancellation. No mid-call model crash
  is claimed. Live read-only SQL confirmed unique ordered UTC audit milestones,
  one DONE job/proposal, REJECTED-only decision and zero execution rows.
- Legacy task `0b2413cf-355c-457d-90f2-8d94bd7eb4c1`, proposal
  `464db2ea-fad0-4586-8dc5-f253cd13e2b2`: same UUID through Mobile, nine events,
  three groups, one job, payload-bound approval, SIMULATED/NOT SENT. Outage task
  `4b3da2a9-d8cb-42e4-8491-513c3c979e03` preserved pending work;
  two events drained in 31.076 s. Four HTTP samples do not qualify throughput/HA.
- Golden FULL `e9aed1ac-acb4-425c-8441-1f44c1c87b78`, SMOKE `10f3941f-26f5-4592-92dd-238df3ad1f9a`,
  REGRESSION `1497956a-293e-4e6f-b493-3fbf703e6d64`, cautious
  `55e4fcf6-12cf-4120-a8a6-66c7695b6a1d`. Original labels/baselines/thresholds unchanged.
- Separate staged FIXTURE draft `ea3c25bd-0be7-4772-a7b0-63379e8c1aca`, job `16437ceb-1a99-4999-b6f1-7b82149d562d`,
  proposal `07d769f7-2cd1-4883-b65d-067df6cf113b`. A unique PENDING job was created through
  actual outbox/Kafka/inbox with the jobs worker stopped. Publisher/consumer/Kafka,
  backend and Redis were stopped; --no-deps started only the jobs worker alongside
  PostgreSQL. It reached DONE/PENDING_APPROVAL without a broker/API/Redis running.
  After worker shutdown/API restart, exact original quote/UUID verified and approval/
  execution were null. Explicit cancellation persisted; temporary token was revoked
  and returned 401. This qualifies the operational staging **with FIXTURE**, not
  Qwen loading, controller-to-worker transport under load or real acceptance.

R2's source/prompt/schema/artifact/alias and controlled binding still match; fresh
read-only checks confirmed its reserved key has **zero rows**. Controller startup/
private bearer/host reachability were tested with static inventory only: no bearer
401/authorized 200, **zero model acquisition**. All model artifact bytes/hashes
remain intact. A closed readiness record has all model/inference approval flags
false; no passing activation attestation or real configuration was enabled.

### Final database, cleanup and mandatory boundary

Enforced final read-only SQL confirms the original Desktop registration remains
owned/enabled **version 1**; all three temporary NOVA grants are disabled. Local
owner identity version is 12 after revocation. R1 remains FAILED/DRAFT_INVALID,
job `6bfba979-0483-4c6b-86df-3d5a89fa434e` DEAD/attempts=1/result_id=null. It was
not reset/replayed. R2 rows **0**, Phase 10 execution rows **0**, evaluation schemas
**0**. Draft metadata remained identical across local/OIDC/backend restarts. No
unsupported source, model-authorized approval or external action was accepted.

All task containers/frontend/watchers/controller stopped; independent checks found
no processes/listeners on 3000/8000/8080/8180/5432/6379/9092/9094/11434/11435/11436.
Thirteen private model resource flags remain false. Temporary NOVA grants revoked;
readiness snapshot closed/non-authorizing; prior scoped attestations stay inactive.
All eleven named/anonymous qualification volumes exist and are exclusively mounted
by qualification containers; source mounts read-only. All protected data/artifacts/
vectors/aliases and device registration preserved. No physical data erasure claimed.

Final snapshot **03:24:05**: RAM **8589934592 bytes**, Docker **4106604544 bytes/eight
CPUs**, free disk **13641850880 bytes**, swap **1992.62 MiB**.
Hard disk/swap thresholds pass at these snapshots, but **R2 startup <1024 fails**.
No real model RSS/tokens/latency exists for this task. Fixture usage remains UNKNOWN.
The unchanged R2 request/body/source/criteria now have current offline qualification;
R2 remains **NOT AUTHORIZED / NOT EXECUTED**, not another failed model result.

**Remaining mandatory gates:** fresh startup headroom below 1024 MiB, fresh scoped
explicit R2 approval/configuration/attestation/current credentials, then successful
single real draft acceptance and verified cleanup. No approval is requested as if
all prerequisites had passed. Only the operator can close unrelated applications
or otherwise safely reduce host pressure; no automatic host action or indefinite
waiting will be used here. Current resource snapshots cannot authorize future load.
General agent/vision/semantic/production/streaming/security-certification limits and
Phase 8 Kubernetes/NetworkPolicy caveats remain unchanged.

Source candidate remains **24 text files, 12 modified/12 added**, main at
`7765b33736c28ccc560fc8269bb5fc4b9b050518`, index empty/no remote. No staging/commit/
push/deployment/install/download/cloud/paid inference/external message or Phase 11.
External spend $0; local compute unpriced. **PHASE 10 NOT COMPLETE. STOPPED AFTER
OFFLINE QUALIFICATION AND CLEANUP, BEFORE THE R2 RESOURCE/AUTHORIZATION BOUNDARY.**


## October 20 — authorized R2 real acceptance and Phase 10 completion

Executed October 20, 2026, approximately **03:48–03:50 America/New_York**.
**R2 PASS. PHASE 10 COMPLETE for the specified bounded local owned-preference
workflow.** The operator's instruction to complete Phase 10 followed the exact
request for one R2 attempt, at most one Qwen generation, zero BGE calls and zero
retries. This authorization was applied only to R2 and is now closed. No additional
inference or Phase 11 follows from completion. R1 remains a consumed, failed attempt;
its failed job, resource measurements and missing historical records are preserved.

### Frozen inputs, preflight and exact executed scope

The approved R2 document was copied before execution, SHA-256
`b40299f2948a4a26d5a8825eb4b4e2d02d72c125124b264768f761d6d2640ed1`.
Its prior qualification-addendum fingerprint differs because of document formatting;
all 17 source fingerprints and the canonical frozen request remained unchanged.
The original and revised R1 proposals remain unchanged. All frozen production/test
sources were verified before and after execution; no production code, prompt,
schema, fixture, model settings or acceptance criterion changed during R2.

Fresh measurements now passed the required initial swap <1024 MiB headroom and
hard swap <2048 MiB / disk >=5 GiB gates. The earlier 1992.62 MiB reading remains
historical; the cause of the subsequent host-wide reduction was not established.
Docker Desktop was started normally from its stopped state, without a restart or
allocation change. Allocation stayed 4,106,604,544 bytes/eight CPUs; host RAM is
8,589,934,592 bytes. Model/controller listeners and resident models were absent.
Qwen/BGE artifacts and existing alias/template/blob integrity passed before and
after execution. No artifact, alias, package, runtime or dependency was downloaded,
installed, replaced or pruned.

The existing Qwen tensor SHA-256 remains
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.
The alias was `nova-qwen-phase9-rag96`, context 512/output <=96, two CPU threads,
GPU layers zero, temperature zero, concurrency one and RSS ceiling 2048 MiB.
Startup 30 seconds and inference eight seconds were preserved. Private managed
SELECTION_V1 / QWEN2_CHATML_0351 configuration was checked, with prompt SHA-256
`7529089aa6ff8c7700b7c497ac04021c5af7d5b02849efd2d467b6f2922127b2`
and schema SHA-256
`abe361e90105db233c7727baf491643f167b626942be49232da2a6eb84b4da92`.
The frozen conservative bound remained 469/512; it is not a measured token count.
Controller bearer authentication and container-to-host reachability passed using
metadata-only reads. The reviewed loopback-only OS sandbox was preserved; a
sandboxed external TCP attempt was denied. BGE configuration stayed disabled.
These checks are not comprehensive network/security certification.

The first preflight helper failed while parsing a successful worker metadata check:
Compose added status lines ahead of the JSON. Exactly zero draft submissions,
acquisitions or generations occurred in that first scope. Its services/configuration
were cleaned up and temporary credentials revoked. Only the ignored operator
parser was corrected to read the final JSON line, then fresh preflight and credentials
were prepared in a separate evidence scope. This was not an inference retry.

The single exact POST used the authenticated existing owner, task and original
Desktop registration (enabled/version 1), with a fresh version-bound credential;
revoked credentials were not reused. Source binding, role/device/task ownership,
no competing jobs and absence of any earlier R2 request were checked. Queue services
created the unique durable job while the jobs worker was stopped. Kafka, publisher,
consumer, API and Redis then stopped. During generation, the only running containers
were PostgreSQL and the jobs worker, plus the task-owned host controller/runtime.
Three fresh resource samples preceded worker launch and acquisition. This staged
execution retained all existing per-service and Docker caps.

| Identifier | Actual R2 value |
| --- | --- |
| Task | `9b363f16-1c38-46ff-a190-b674b7b28ed8` |
| Idempotency key | `b1e801de-2d30-4444-9341-fb1efcc36df8` |
| Draft/context | `a0571679-0f5c-4b40-8d9a-775f5170c8d8` |
| Trace | `55bf8f74-7b5c-45b4-89ab-37ca8870428f` |
| Durable job | `79782d0e-8ec0-4ebb-acab-9eee51b5c380` |
| Proposal | `af08ea0d-56ab-4db9-aa73-9c90c8c88646` |
| Outbox event | `b84bced0-9ea1-4cc1-8b97-2246cffc3054` |

### Result, source/privacy validation and authority

Exactly **one POST (202), one Qwen generation, zero BGE calls and zero retries**
executed. There was no warmup, diagnostic, second POST, alternate fixture or hidden
repair. Qwen returned a normal stop with **abstain=false, answer=noodles,
evidence_index=0**. The observer recorded the parsed selection and answer digest;
the application independently verified the generated value before attaching the
original UUID and full quote. No UUID/quote was generated or fabricated by the
application to substitute for an unsupported answer.

Source UUID: `7d1049cb-06b9-49c4-ad06-a8db5036480a`.
Exact authorized public fixture quote:
`phase10_acceptance_fixture preferred_cuisine: noodles`.
The source binding remained
`8dbd48c85725bf97c29be220182aa1ae8ff52a2f32165bd745b1dfcd691de827`.
Current owner/device/task authorization, source/privacy binding and conflict checks
passed. The application read reported EXACT_SUPPORTED_QUOTES, LOCAL_REAL,
simulation=false, approval_required=true and execution_enabled=false.

Read-only terminal SQL independently confirmed **one DONE job, one proposal,
PENDING_APPROVAL, zero ApprovalDecision rows and zero ActionExecution rows** for
this request. REQUESTED, QUEUED, RUNNING, EVIDENCE_VERIFIED and PENDING_APPROVAL
milestones were present, with evidence verification committed atomically with the
proposal/job. No external message was sent. These are acceptance-time snapshots:
cleanup subsequently revoked the temporary identity grant, so its saved permission
binding is deliberately stale. This does not authorize later approval or execution,
or assert that a future read should expose content under revoked credentials.

### Measurements and cleanup

| Measurement | Actual scope/result |
| --- | --- |
| Provider-reported tokens | 162 input / 19 output / 181 total |
| Authenticated POST wall time | 890.138 ms; enqueue response, not generation |
| Application provider/model-call latency | 8712.863 ms, includes acquisition/release |
| Controller inference transport | 4874.143 ms, within unchanged eight-second deadline |
| Recorded controller server-readiness interval | 0.777 s; not a separate weight-load measurement |
| Enqueue-through-acceptance pipeline | 44718.687 ms, includes staged service transitions/polling |
| Peak sampled Qwen process-tree RSS | 1,334,591,488 bytes / 1272.77 MiB, below 2048 MiB |
| Verified model shutdown | 0.044 s |

Ollama loads weights lazily; server readiness is not model-only load latency.
The wider model-call scope exceeding eight seconds does not increase the inference
transport deadline. No TTFT, streaming speed, sustained throughput or instantaneous
hard RAM quota is inferred. Process-tree RSS may include shared-page accounting.

The one-second host watcher recorded **100 snapshots**, swap **0–900.06 MiB**,
minimum free disk **18,387,902,464 bytes**. Three-sample initial/before-POST/before-worker
headroom checks each showed 0 MiB swap. At controller acquisition swap was
**99.62 MiB**, disk **19,463,651,328 bytes**; after verified Qwen termination swap
was **900.06 MiB**, disk **18,388,213,760 bytes**. Final stopped reading: swap
**900.06 MiB**, disk **18,388,029,440 bytes**. The controller's existing resource/RSS
watchdog also remained active. No resource stop occurred. These snapshots are
not future activation authority or guaranteed allocatable model RAM.

The model lease/runtime/descendants were released and stopped. Independent checks
found no running Docker containers, model/controller processes or task listeners
on 3000/8000/8080/8180/5432/6379/11434/11435/11436. Scoped resource approval is false,
launch settings reset to FIXTURE/empty real configuration, and the attestation is
closed with both resource/load approvals false. Fresh temporary credentials were
revoked and rejected with 401. The original enabled device registration was
preserved. Application data, previous failures, source memories, vectors, model
artifacts/aliases and dedicated volumes were preserved; no volume/cache deletion,
host restart, model substitution or resource-limit increase occurred.

Safe evidence remains ignored under `.local/phase10/r2-acceptance-20261020-resumed`;
first-preflight evidence is separately preserved under
`.local/phase10/r2-acceptance-20261020`. Scoped credentials/configurations and closed
attestations remain private under their matching `.secrets` directories. No raw
private prompt or credential was added to the source candidate.

### Completion gates and retained limits

All mandatory gates now pass for the defined scope: final-source **750 backend
passes/one explicit real-model opt-in skip**, **17 controller passes**, lint/format/
pip/migration checks, Go race/vet, frontend lint/typecheck/build, **58 browser cases
across four passing invocations**, fixture Kafka/duplicate/HITL/recovery and golden
baseline FULL 104/104, SMOKE 10/10, REGRESSION 25/25, plus this single real draft
acceptance. The cautious 23/25 negative control remains an expected gate failure.
The preceding detailed qualification section retains exact commands, IDs, timing
and intermediate failures. Source hashes still match that qualification; those
suites were not unnecessarily rerun or relabeled as learned quality measurements.

Completion covers explicit owned named-preference drafting through pending
approval, not general autonomous reasoning, semantic entailment, external action,
production readiness, vision, real judging, sustained load or deployment. Existing
Phase 8 Kubernetes/NetworkPolicy caveats remain unchanged. Permission/privacy
checks are acceptance/read snapshots; historical records remain retained. A
single positive real case is not general reliability or model security evidence.

Only existing status/outcome documentation changed during acceptance. Candidate
remains **24 text files, 12 modified/12 added**, main/HEAD
`7765b33736c28ccc560fc8269bb5fc4b9b050518`, index empty, no remote. No staging,
commit, push, download, installation, deployment, paid/cloud inference, external
action or Phase 11. External spend $0; local compute/electricity unpriced.
**PHASE 10 COMPLETE WITHIN ITS DEFINED BOUNDED LOCAL SCOPE. STOPPED AFTER CLEANUP.**
