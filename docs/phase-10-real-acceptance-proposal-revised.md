# Phase 10 real draft acceptance — revised source freeze R1

Prepared October 20, 2026 (America/New_York).
**READY FOR EXPLICIT OPERATOR APPROVAL — NOT APPROVED / NOT EXECUTED.**
Phase 10 remains NOT COMPLETE. This document proposes reconciliation of the audit-only
source change; it is not permission to enable a model, submit a draft or retry inference.

## Original evidence and exact reconciliation

Preserve [the original proposal](phase-10-real-acceptance-proposal.md) unchanged.
Its file SHA-256 is
`19319380e993f7e4d9aeb4333e8117457642d917bea55139575a5dfd096d02a7`.
The original ignored `.local/phase10/source-review.json` also remains unchanged.
Only explicit approval of this R1 revision would replace its `drafts.py` freeze for
the same single case. No earlier approval is reused for changed source.

File: `backend/app/proactive/drafts.py`.

- Original frozen SHA-256:
  `8ce187f969f521981b10ea977f264bdad226fd1ad713e0907d5564a3ed67407e`.
- Qualified R1 SHA-256:
  `b9c239154da11ed8acbbf90816e939c35c96a919184e9f97bb53a6fa0af92881`.

The exact difference contains four hunks:

1. Import the existing `SystemClock` from `app.proactive.clock`.
2. Change only the owned-draft audit helper from `ProactiveService().audit(...)`
   to `ProactiveService(clock=SystemClock()).audit(...)`.
3. Add `audit(session, row, "REQUESTED")` immediately before the existing QUEUED
   audit in the existing context/outbox creation transaction. QUEUED already
   existed; both milestones commit or roll back with request creation.
4. After final `validate(session, row)`, add the EVIDENCE_VERIFIED audit and its
   two-line explanatory comment. It shares the existing final proposal/job/
   PENDING_APPROVAL transaction, so rollback cannot retain a verified milestone.

No durable state or trigger was added. Audit event timing/observability changes;
model and acceptance semantics do not. Reversing precisely these four hunks
reconstructs text whose SHA-256 exactly equals the original frozen fingerprint.
The exact unified diff and reconstruction are retained as ignored review evidence
under `.local/phase10/reconciliation-20261020`. This is hash-verified reconstruction,
not an assertion that the original source was committed.

No change affects the model prompt, GroundedSelection schema, selected evidence,
owner/task/device/privacy authorization, conflicts, routing, inference budget,
request payload, model artifact identity or approval/execution authority. The legacy
demo clock is unchanged. Extra audit writes remain in the existing transactions;
no raw evidence, prompt or model output is added to audit metadata.

## Qualified regression evidence

The October 20 source freeze passed:

| Check | Existing actual result |
| --- | --- |
| Focused owned drafts | 47 passed, 3.31 s |
| Full PostgreSQL backend | 747 passed, one explicit real-model skip, 68.65 s |
| Ruff / format / pip check | PASS, 112 app/test files, no broken requirements |
| Controller/process tests | 13 passed, 0.057 s, no models |
| Go race / vet | two tests passed; vet passed |
| Frontend lint / typecheck / build | PASS |
| Browsers, retries=0/trace=off | 38 + 15 replay, 3 local-auth, 2 actual OIDC passes |
| Fixture Kafka/draft/duplicate/restart/outage | PASS; broker recovery 21.756 s |
| Golden baselines | FULL 104/104, SMOKE 10/10, REGRESSION 25/25, critical=0 |

The focused/full database checks cover current UTC timestamps, atomic request and
verified milestones, rollback, duplicate/idempotent processing, terminal non-revival,
source/privacy revocation, conflict rejection and no approval/execution bypass.
The live fixture check found unique REQUESTED/QUEUED/RUNNING/EVIDENCE_VERIFIED/
PENDING_APPROVAL/REJECTED milestones, one durable proposal/job and zero execution
rows. Legacy fixture-clock tests passed unchanged. Browser lifecycle assertions
passed for all seven durable states. These are deterministic/local-service
regressions, not model-quality measurements or real Phase 10 acceptance.

See [audit](phase-10-implementation-audit.md) and [test evidence](phase-10-test-evidence.md)
for exact IDs, commands, timing scopes, negative control and retained limitations.
The reconciliation reran no full suite: production/test files match that qualified
snapshot. New checks only verify source/artifact integrity and read-only fixture/wire
construction, without model activation or application mutation.

## Unchanged single-case request

Request exactly one authenticated owner POST to `/api/v1/proactive/drafts` with:

```json
{
  "task_id": "9b363f16-1c38-46ff-a190-b674b7b28ed8",
  "query": "Which cuisine does phase10_acceptance_fixture prefer?",
  "memory_ids": ["7d1049cb-06b9-49c4-ad06-a8db5036480a"],
  "idempotency_key": "15d88b00-b223-429e-88cd-c1a6b160daf2",
  "expires_in_seconds": 600
}
```

Owner remains `00000000-0000-4000-8000-000000000001`. Task/source/subject/predicate/
value/full quote are unchanged. Exact original quote:
`phase10_acceptance_fixture preferred_cuisine: noodles`.
Source binding SHA-256:
`8dbd48c85725bf97c29be220182aa1ae8ff52a2f32165bd745b1dfcd691de827`.
Canonical body SHA-256 (sorted compact JSON):
`e289fa1dbc21b59b9b623bf2434db26e5f21e222288edd95d494b0ca8c4906de`.

Fresh reconciliation checks used a transaction with `transaction_read_only=on`
against only the existing isolated qualification database. They confirmed the owned
ACTIVE source, exact fixture fields/quote/binding, zero rows for the frozen request
and zero LOCAL_REAL owned-draft rows. Nothing was recreated, corrected or submitted.
The temporary database/metadata-check processes were stopped afterward. The protected
Phase 9 database/vectors were not connected to or changed.

Temporary qualification identity grants were revoked at the preceding cleanup.
Fixture ownership verification is not proof of current authenticated execution
readiness. Future approved preflight must establish a valid short-lived owner/device
identity and controller authentication, without expanding roles or bypassing policy.

## Verified production freeze

All other original frozen production fingerprints match; only `drafts.py` adopts
its qualified audit correction. The proposed R1 production hashes are:

| File | R1 SHA-256 |
| --- | --- |
| `backend/app/inference/grounding.py` | `3bd4db09caef3be880d280d4ddae359a49772baa2e6441a096fc15a42bd9eab7` |
| `backend/app/inference/contracts.py` | `2c225f7da6d9fc34e4fa6db2eef77211d4c9b9735853b6b85042ddd18a9a19ca` |
| `backend/app/inference/providers.py` | `a1d6196afc16dfec6ec62cb14897b59bf8d9129ded992f1cccb0431ecb25a03d` |
| `backend/app/inference/registry.py` | `8c69001929097ddfc70b7862e56f17308ace7817ba85c757e1e699157773a403` |
| `backend/app/inference/service.py` | `1a7d2cda04d4039f812422d6297126dea44b9f000dad5b03a7744f8f4ba3df14` |
| `backend/app/events/outbox.py` | `26d375619e54c8214f91731a8439bb8a4a51af8575873b3eb8c126bb6439896a` |
| `backend/app/events/pipeline.py` | `f2e76fcbfbde8621aa1fdcd08af5738c95c8cadabbc3137f8c03283bab2c6a66` |
| `backend/app/proactive/api.py` | `4315737e2e80738aef5f15765cdfef6cbfc71228031957de1b878baec51d0ea2` |
| `backend/app/proactive/contracts.py` | `7421921664c697b2113f1f615cca36556121099e95a7482acbb29484f649a9c3` |
| `backend/app/proactive/drafts.py` | `b9c239154da11ed8acbbf90816e939c35c96a919184e9f97bb53a6fa0af92881` |
| `backend/app/proactive/service.py` | `713883ffe2150ba782b33f75cf5f026259c7f5f91127980bb90f8ba285e84edd` |
| `backend/app/security/auth.py` | `ace1a60727e05b00a45c8f6eb948c0a908e72198873d53c5e9a7b5382bb15fa6` |
| `backend/app/security/identity.py` | `98159a0c2909006fa3a17a41f99bb079e41942626b981021a736700728560809` |

Additional unchanged committed dependencies checked against HEAD:

- `backend/app/proactive/clock.py`: `13f920256b27a55b2dbaa3b483b3eda43c55831c614d1ca3cd2bd5907e597783`.
- `scripts/phase9_residency.py`: `1fb19f0a02a7db8320f58ededbed0c9641d9c0befc8fb38e723962345d65946f`.
- Model-routing source has no working-tree difference from the Phase 9 checkpoint.

The original 20 candidate hashes also match the October 20 qualified snapshot before
this reconciliation's documentation edits. Earlier test/documentation differences
from the October 19 inventory are already qualified audit/lifecycle assertions and
historical reports; they are not unexplained production or inference changes.
R1 adds only this proposal plus audit/manifest reconciliation notes. No production,
test, fixture or model configuration was edited. Refuse any later unexplained drift.

## Prompt, schema, budget and artifacts

Fresh offline construction verified:

- Selection prompt at 96 SHA-256:
  `7529089aa6ff8c7700b7c497ac04021c5af7d5b02849efd2d467b6f2922127b2`.
- Unchanged GroundedSelection schema SHA-256, sorted compact JSON:
  `abe361e90105db233c7727baf491643f167b626942be49232da2a6eb84b4da92`.
- Same selected fixture and conservative bound **469/512**, including output 96.
  This is not runtime token accounting or a latency/fit guarantee.
- Existing pinned `QWEN2_CHATML_0351` and SELECTION_V1 paths; no output repair,
  forced claim, weakened citation/privacy validation or cloud fallback.

Fresh read-only artifact hashing verified both existing alias manifests and every
referenced blob's size/digest, including model, config, system, ChatML template,
license and parameters. Key immutable identities:

| Artifact | Bytes where applicable | SHA-256 |
| --- | --- | --- |
| Qwen tensor | 986048512 | `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4` |
| `nova-qwen-phase9-rag96` manifest | 1091 | `af492c94e96e620796e53faeccc48230c42eb81afec1141cfeb7b32af352fa64` |
| Preserved original `nova-qwen-phase9` manifest | unchanged | `dafd3dc8e500e0774baaf6dc50d5792374815c013e8de4a3a98ac026b1473271` |
| Existing ChatML template blob | 1482 | `eb4402837c7829a690fa845de4d7f3fd842c2adee476d5341da8a46ea9255175` |
| Existing 96-token parameter blob | 76 | `4b28aeeab8b41deeb7a8b6f050b586e4cd9785675fc7fd726d73a358ffcae568` |
| BGE tensor, unused by this case | 133466304 | `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad` |

All seven installed pinned BGE files also match their approved hashes; BGE still
must remain stopped/disabled and receives zero requests. Artifact verification
loaded no model and proves no runtime behavior. RAG96 metadata retains context 512,
output 96, threads 2, GPU layers 0 and temperature 0. Concurrency/residency/deadline
safeguards remain enforced by the unchanged reviewed controller/provider.

## Unchanged limits, gates, outcome and cleanup

Maximum **one authenticated draft POST and at most one Qwen generation**; zero
BGE requests, retries, warmups, additional probes, broader planner/critic inference
or external actions. Use only existing `nova-qwen-phase9-rag96`, CPU threads 2,
GPU layers 0, context 512, output <=96, temperature 0, concurrency 1, Qwen sampled
RSS <=2048 MiB, startup 30 seconds/inference eight seconds. Retain leases/watchdog,
zero queue, verified unload, offline/local-files-only and loopback-only model sandbox.
FIXTURE stays the default; only the future explicitly scoped API/worker configuration
may select LOCAL_REAL after approval. No configuration is enabled by this document.

Before any approved execution, repeat fresh disk >=5 GiB/swap <2048 MiB, source/
proposal/prompt/schema/fixture/artifact checks, no prior frozen request execution,
no other real jobs or resident/unowned model listeners/processes, private controller
bearer authentication, valid owner/task/device authorization and read-only mounts.
Create a fresh scoped private attestation and freeze/review the private overlay.
The original proposal had not frozen that future overlay; no claimed overlay hash
is invented here. Preparation checks never waive runtime gates or provide future
activation authority. Refuse drift/failure rather than update inputs during execution.

PASS still requires model-generated `noodles` at the correct evidence index,
independent original UUID/full quote and current binding/privacy/conflict verification,
one atomic durable proposal/completed job, PENDING_APPROVAL, approval required and
execution disabled. No approving ApprovalDecision, ActionExecution or external
message may exist. A valid abstention fails the positive case. Invalid response,
timeout, auth/resource/citation/privacy failure or unload failure is recorded as
failure/refusal, never repaired or regenerated. Stop after the single case on every
outcome; an ambiguous interrupted real job must not generate again.

Record actual request/event/job/proposal IDs, identities, usage or UNKNOWN, separate
model/HTTP timing scopes, sampled RSS, resources, verification and unload. Release
leases, verify process/descendant/listener termination, stop task-owned services,
disable scoped real configuration and close attestation in finally. Preserve all
existing aliases/artifacts/data/vectors/volumes and historical results. No download,
dependency install, resource increase, cloud/paid API, external action/message,
Git staging/commit/push/remote, deployment or Phase 11.

**Reconciliation result: no unexplained drift; R1 is ready for explicit operator
approval only. Zero model generations/draft submissions occurred. Phase 10 remains
NOT COMPLETE until the separately authorized real case passes. STOPPED.**

## Authorized R1 preflight outcome — October 20, 2026

The operator explicitly approved the R1 pre-execution document with SHA-256
`8af356e0b97bb325b896af5b3023ebb1dbfd799159f4097c73efa1ec503e2d95` and qualified
`drafts.py` fingerprint above. That exact approved text is retained in ignored
`.local/phase10/r1-acceptance-20261020/approved-proposal.md`. This outcome appendix
does not alter the frozen request, source, model, limits or acceptance criteria.

**BLOCKED / NOT EXECUTED.** Source, prompt/schema, artifact, fixture binding,
context budget and resource checks passed. The task's existing owned origin
Desktop device `00000000-0000-4000-8000-000000000010` has **no DeviceRegistration
row**. R1 requires an enabled, owner-matching registration. The strict preflight
refused before token renewal, controller startup, worker activation or submission.
The earlier phrase describing an enabled device grant was a proposed prerequisite,
not independently established readiness; this check demonstrates it is currently
unsatisfied. No registration was created, ownership changed or requirement waived.

The existing scoped owner identity is present with unchanged roles/owner but
remains disabled from the prior qualification cleanup. No replacement token/grant
was issued. Device and fixture inspection used read-only SQL; source binding and
original fixture fields still match and the frozen request count is zero.

Actual scope: **0 authenticated draft POSTs, 0 Qwen generations, 0 BGE calls,
0 inference retries, 0 external actions**. No draft/job/proposal IDs, model answer,
evidence index, token usage, generation latency or model RSS exist for this case.
Positive post-generation citation/privacy acceptance was not exercised. This is
not a failed model output and must not be counted as a positive acceptance.

Scoped private model approval was reset false, its API/worker overlay returned to
FIXTURE/empty real settings, the fresh scoped attestation closed and all started
services stopped. The original private configurations remain unchanged. No model
or controller started, so no lease/unload was needed. Data, all eleven inventoried
qualification volumes, vectors and artifacts were preserved. Final independent
cleanup at 02:02:39 America/New_York found no running containers/model processes/
relevant listeners, swap 1663.06 MiB and 13,744,967,680 bytes free disk.

Latest 747 backend/47 focused/13 controller and complete local cross-stack
qualification still cover the unchanged production/test source. No heavy suite
was rerun. **PHASE 10 NOT COMPLETE.** This scoped execution authorization is closed;
there is no implied retry allowance. Operator resolution of the missing device
registration and valid scoped owner/device credentials is required before any
future separately authorized attempt. **STOPPED AFTER PREFLIGHT AND CLEANUP.**

## Device recovery completed — awaiting fresh real authorization

October 20, 2026, approximately 02:19–02:21 America/New_York. The operator separately
authorized recovery of the existing device registration, explicitly excluding
inference and requiring fresh approval afterward. **RECOVERY PASS.**

The authenticated supported `POST /api/v1/auth/devices/register` enrolled only
`00000000-0000-4000-8000-000000000010`, owned by
`00000000-0000-4000-8000-000000000001`, as one enabled registration, **version 1**.
A legitimate bootstrap token was issued by the existing operator CLI. It was
correctly refused with 401 after enrollment; a freshly CLI-issued token authenticated
successfully with matching current identity/device versions. No direct database
insert, invented credential, alternate device, role expansion or challenge bypass
was used. These remain simulated local device identities, not hardware attestation.

The missing row arose because identity/device provisioning does not itself enroll
DeviceRegistration; explicit enrollment had been omitted. The compatibility view's
enabled/version-0 fallback was not mistaken for R1 readiness. All owner/task/device
binding checks passed after recovery. A read-only count found exactly one enabled
registration, zero frozen request rows, zero real draft rows and no pending owned
jobs. Original fixture/binding, prompt/schema, 469/512 bound, qualified source and
all existing model artifact/alias/blob fingerprints remain unchanged.

Controller authentication/host reachability passed via static inventory only;
**zero acquisitions/model loads**. A readiness snapshot had model_load_approved=false
and inference_authorized=false. FIXTURE and empty real provider settings stayed
active throughout. No Qwen, BGE, draft submission or inference retry occurred.

Cleanup preserved the enabled version-1 registration and revoked the temporary
identity/token. The final token correctly returned 401. Thus credentials were
validated while active, then deliberately retired; a future authorized run must
issue/verify fresh scoped credentials against that preserved registration.
All task-owned services/controller stopped; the readiness snapshot is closed.
Final independent checks: no containers/models/listeners, swap **1655.06 MiB**,
free disk **13,713,174,528 bytes**, unchanged 8 GiB RAM/Docker allocation and twelve
private real flags disabled. All data/vectors/artifacts/volumes were preserved.

**R1 is ready for fresh explicit operator approval, not execution under this
recovery grant.** The 747 backend/47 focused/13 controller and existing final
cross-stack qualification remain applicable to unchanged source. Phase 10 remains
NOT COMPLETE until the mandatory positive real case and cleanup pass.

The exact next approval requested is:

> Authorize exactly one authenticated R1 draft POST for task
> `9b363f16-1c38-46ff-a190-b674b7b28ed8`, source
> `7d1049cb-06b9-49c4-ad06-a8db5036480a`, query
> `Which cuisine does phase10_acceptance_fixture prefer?`, and frozen idempotency
> key `15d88b00-b223-429e-88cd-c1a6b160daf2`. Use the unchanged request body above,
> qualified `drafts.py` SHA-256
> `b9c239154da11ed8acbbf90816e939c35c96a919184e9f97bb53a6fa0af92881`, and existing
> `nova-qwen-phase9-rag96`/SELECTION_V1. Permit at most one Qwen generation, zero
> BGE calls, zero retries/warmups/additional inference and zero external actions.
> Preserve every R1 CPU/context/output/memory/concurrency/deadline, authorization,
> citation/privacy/conflict, proposal-only and cleanup requirement. Reissue scoped
> owner/device credentials, repeat fresh resource/artifact/source/controller gates
> and close the scope afterward. Stop on any failed prerequisite or after the case.

This request is a review artifact, not approval. Evidence remains ignored under
`.local/phase10/device-recovery-20261020`. **STOPPED BEFORE REAL INFERENCE.**

## October 20 — fresh authorization consumed: FAIL

The operator freshly authorized the current R1 document SHA-256
`0ee038ebbd97ec4cd01c3d8172a2ff3582131120d281caf351dedff1ca900d67` after recovery.
Its exact pre-execution bytes are preserved in ignored
`.local/phase10/r1-final-acceptance-20261020/approved-proposal.md`. This appendix
changes no frozen source, request, fixture, prompt, schema, model or criteria.

**FAIL / EXECUTED. PHASE 10 NOT COMPLETE.** One frozen authenticated draft POST
returned 202, draft `2ac3dd25-5854-443a-8bd7-67f8dc37fa76`, worker trace
`57b6aea1-c387-4ac5-b510-8910e1869851`. One Qwen inference request was attempted;
host swap crossed 2048 MiB during CPU loading and the controller returned 409.
The worker logged OWNED_DRAFT_FAILED. No completed model response/answer/index,
positive citation/privacy acceptance or pending proposal was observed. No retry,
second POST, diagnostic generation or BGE call occurred.

Fresh source/artifact/fixture/budget/authentication/device/controller/sandbox checks
passed before submission. Swap was 1647.06 MiB before the POST, 2072.62 MiB at
stopped cleanup. Tokens/model latency/peak RSS are UNKNOWN: no normal response
arrived, and the final controller resource check interrupted residency-record
persistence after runtime termination. Do not invent missing measurements or a
DONE job/PENDING_APPROVAL proposal. Post-shutdown SQL was not restarted under
failed resources, so the job UUID/final database counts were not independently read.

All services/model processes/listeners are stopped, fresh temporary credentials
revoked (401 verified), private resource approval false, scoped attestation closed
and launch overlay reset to FIXTURE/empty real settings. All data/eleven volumes/
vectors/artifacts and the version-1 registration are preserved. Full measurements,
recording limitation and independent cleanup are in the final [audit section](phase-10-implementation-audit.md).
The preceding final-source qualification remains applicable to unchanged code.
This attempt's approval is closed; another request/generation is not authorized.
**STOPPED. PHASE 10 NOT COMPLETE.**
