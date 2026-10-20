# Phase 11 implementation audit

October 20, 2026 (America/New_York). Baseline main/HEAD:
`80dc41af8d3742fdb700b02e342f579e06389fcf`, the verified Phase 10 checkpoint.

**PHASE 11 COMPLETE for the approved bounded offline scope.** The final complete
qualification entrypoint passed, including current backend/frontend/browser/auth/
Kafka/golden checks, corrected terminal invariants and cleanup. See the final
section for exact results, failures retained and scope limits.
No real inference, model activation, external action or deployment is authorized
or performed by this scope. No Phase 11 file is staged or committed.

## Approved scope and implementation

The operator approved the previously presented Phase 11 proposal with “complete
phase 11.” The adopted scope/title is Local reliability, security and operational
qualification. Its exact preparation document and predeclared workload were copied
to ignored evidence before implementation. Existing Phase 9/10 audits, model
contracts, fixtures, source support/privacy rules and real acceptance results are
preserved. Scope and exclusions are in the proposal and architecture document.

The operations endpoint now returns bounded independent event/job pages, immutable
sequence cursors and an append high-water boundary. Ownership is checked first;
event/job queries also filter owner/task, and projection owner is checked. Receipts
use one batch query instead of an event-count-dependent query loop. Responses
contain metadata, known consumer names and a fixed DEAD-job label, without source
content, prompts, raw provider responses or private configurations. No migration
or persistent schema change is necessary; existing event/task and job/event indexes
and unique sequence order are reused. A 100-row-page test bounds query count.

The operations UI provides separate event/job continuations, refresh, loading,
empty/error feedback and UNKNOWN metadata. Task-keyed components, request aborts
and mounted-state checks suppress stale-task results. No draft approval/execution
capability is added. Existing subscription controls retain their original policy.

The new operator-only qualification runner stages host/backend/Go/frontend/browser/
Kafka/auth/golden checks, captures per-command outcomes and preserves partial/failure
status. It rejects unsafe project/mount/volume/real-provider settings, competing
listeners/containers and changed Docker allocation. Its resource watchdog preserves
the disk/swap thresholds and terminates only owned process groups; finally stops
only the generated project, including detached one-off test runners. Scoped grants
are tracked before potentially ambiguous provisioning and revoked in finally.
Missing measurements, failed commands and failed cleanup cannot create overall PASS.

New deterministic tests cover bounded independent pagination, high-water behavior,
batched query count, metadata exclusion, authenticated ownership/RBAC/revocation,
manual retry after an ambiguous real RUNNING record, and runner admission/failure/
cleanup/process termination/subnet allocation. Existing 17 controller tests retain
resource-change-during-load, persistence failure, poisoned cleanup and exact-ceiling
coverage. All provider responses in these tests are scripted; no model runs.

## Evidence recorded before final integration

- Focused PostgreSQL operations/owned-draft tests: **59 passed, 4.35 s**.
- Final application snapshot full backend: **759 passed, one explicit real-model
  opt-in skip, 70.99 s**. Ruff lint/format and installed-environment pip check PASS;
  113 Python app/test files formatted. Mandatory test setup upgrades/checks the
  dedicated `_test` database. No protected application database is tested/cleaned.
- Existing Go compiler image, network disabled, GOPROXY=off/GOTOOLCHAIN=local:
  race package passed in **1.025 s**, vet exit 0.
- Frontend installed dependencies: lint/typecheck/build PASS. No separate configured
  component runner; Playwright provides browser coverage.
- Host/controller and qualification-runner results and final integration outcomes
  will be recorded in the final evidence section, with individual invocation scope.

## Intermediate failures and deviations retained

The first focused command used unsupported Compose-run `--no-build` and refused
before tests. Removing that flag in the ad-hoc command exposed another mistake:
the new focused project lacked an explicit backend-test image name, so Compose
created `nova-phase11-focus-backend-tests` and installed pinned development
dependencies in that isolated image. This violated the existing-dependencies-only
preparation plan. It was reported immediately; no host package, model/runtime,
protected data or source dependency file was changed. The subsequent qualification
runner explicitly names and inspects existing images, uses pull=never and does
not invoke a build. The accidental image is retained; no cache/data was deleted.
This deviation must not be represented as zero installation across the whole task.

Initial script formatting/import findings were corrected. The first full suite
passed 759 tests/one skip in 71.33 s, then lint found four import-order differences
caused by formatting from the wrong project root. Imports were corrected from
the backend root, assertions unchanged; the complete current-source command then
passed as above. A read-only script lint invocation could not create its cache;
the corrected `--no-cache` check passed. None of these failures is counted as PASS.

Initial runner preflight refused legitimate existing read-only observability bind
mounts in unused Compose services. The explicit reviewed allowlist was completed;
tests still reject unreviewed/protected mounts. Integration startup then refused
because Docker default address pools were fully subnetted. No global network
prune, deletion or daemon configuration change was used. The runner now inspects
Docker subnets and non-default host routes and selects disjoint private /24
subnets for this isolated project's networks, preserving existing internal flags.
An initial allocator probe encountered null IPAM Config on host/none networks;
it now treats that as no subnet. Allocation collision/exhaustion is unit tested.
All prior project networks/containers/volumes were preserved.

## Remaining acceptance gates at this snapshot

Actual browser journeys including new operations behavior, strict local/OIDC auth,
Kafka duplicate/forgery/recovery, golden suites, measured fixture baseline, final
source/inventory/security review and independent cleanup verification remain
required. No numeric performance or model-quality target is invented. The fixed
workload is ten sequential fixture HTTP reads, no warmup/concurrency one, and one
broker-outage task. Browser retries remain zero and quota pacing remains explicit.

Retained limits: finite tests, metadata pagination rather than MVCC export, trusted
operator/database and dedicated local services; no learned quality, production
capacity, external side effects, real-model crash recovery, advisory/penetration
certification or deployment claim. Existing Phase 8 deployment caveats are unchanged.


## Further integration corrections before final qualification

The isolated project with explicit subnets passed replay 38 + 17 cases and all
three strict-auth cases. The existing Phase 10 fixture harness then refused its
Phase 11 project prefix before submitting its fixture request. The harness now
also accepts exactly `nova-phase11-q-[a-f0-9]{12}`, validated by a new host test;
its existing loopback/explicit Compose-file guards and Phase 10 project support
remain intact. This is test orchestration, not changed draft/approval behavior.

A subsequent complete attempt passed backend 762/one skip, Go/frontend and migration
checks, but replay A had 37 passes/one continuity failure. Read-only access-log
review recorded the actual handoff POST returning 200; the UI still displayed
Desktop. The test clicked a handoff immediately after a client navigation, while
the source view can still be mounted. It now explicitly asserts the Device
Continuity destination heading before its first handoff. No original assertion,
timeout, expected state or retry policy was weakened. This is navigation
synchronization evidence, not a demonstrated backend handoff failure. The failed
invocation, backend metadata logs and browser error context remain ignored evidence.

Final input validation also bounds all sequence cursors to PostgreSQL signed-bigint
range, with three added overflow cases (762 total backend passes on that snapshot).
Script lint/format and the current ten host runner safety tests pass. Keycloak
metadata readiness is explicitly awaited before provisioning. All these corrections
precede the final full entrypoint invocation and remain subject to its results.


## October 20 — final complete offline qualification PASS

**PHASE 11 COMPLETE for the approved bounded offline scope.** The complete source
entrypoint `python3 scripts/qualify_phase11.py` returned **PASS** for all four
stages in `nova-phase11-q-615ad1daf73c`, with services stopped and all temporary
local/OIDC grants revoked. No model activation, real inference or external message
occurred. Prior failed/partial reports remain unchanged, not relabeled as passes.
The release mission froze new features and prioritized existing verified workflows;
its separate lifecycle tools and evidence are documented in the local release guide.

| Gate | Final actual result |
| --- | --- |
| Full PostgreSQL backend | 762 passed / one explicitly marked real-model opt-in skip, 73.65 s |
| Backend lint / format / pip compatibility | PASS; 113 app/test files formatted; no broken requirements |
| Existing controller/process tests | 17 passed, 0.140 s; fake callbacks/non-model subprocesses |
| Qualification runner safety/policy tests | 11 passed, 0.044 s |
| Go race / vet, existing offline compiler image | PASS; race package 1.022 s |
| Frontend installed-dependency lint/typecheck/build | PASS |
| Browser replay A / B, retries=0, trace=off | 38 passed, 45.9 s / 17 passed, 11.2 s; five explicit profile skips |
| Separate strict local-auth / actual local OIDC | 3 passed, 2.4 s / 2 passed, 2.4 s |
| Alembic current / drift | 0011_inference_registry head; no new operations |
| Kafka duplicate/forgery, queued worker recovery | PASS using actual dedicated local broker/workers |
| Broker outage recovery | PASS; two events drained in 32.012 s from restart command |
| Golden baseline FULL / SMOKE / REGRESSION | 104/104 / 10/10 / 25/25, zero critical violations |
| Cautious negative control | 23/25, gate FAIL and expected exit 1; not promoted |
| Final database invariants / cleanup | PASS |

Browser coverage is **60 unique cases across four passing invocations**, not one
60-pass command. Additional MVP smoke repeats three existing strict-auth cases;
those repetitions are not new unique regression cases. Controller/runner doubles
and fixture golden results do not establish learned model quality or model attack
resistance. Mandatory migration checks use only the guarded `_test` database.
No protected application downgrade or new migration occurred.

Actual owned fixture acceptance task `41521f30-a91d-4fb6-bac3-632189952598`, draft
`4ef883e9-1ed3-4e16-bdb4-1317d2e4ba47`, proposal
`92be3243-4737-4846-be36-8625f6f499a3`: original UUID/quote verified, pending before
explicit rejection, owner isolation, no approving/execution authority, three duplicate
messages without extra effect and three forged-envelope dead letters. Queued work
survived a worker stop/restart; this is not a real mid-generation crash experiment.
Legacy fixture task `dccf9fca-2351-49d9-82f3-2d97aafba5d4` retained its UUID through
Mobile, nine outbox events, three groups, one job and payload-bound approval with
SIMULATED / NOT SENT execution. Recovery task
`c0f5d559-d5bd-4023-8024-e01e73f0f219` persisted during the actual broker outage.

Golden run IDs: FULL `1955d66e-5eab-4402-b9a6-065b50e15689`, SMOKE
`1779ebe5-4f83-40c9-a90a-943be35baf14`, REGRESSION
`800158a3-74e8-453f-a210-908c4aa15fc0`, cautious
`ebc8226c-438d-414e-8162-c49009b01f00`. Datasets, expected labels and historical
baselines were not changed. Expected failure-path log messages in golden scenarios
are not ignored suite failures; their actual gate/counts above determine disposition.

### Final terminal-check correction

The preceding full run `nova-phase11-q-8c51e273f151` passed every functional stage
but its final helper incorrectly required zero LOCAL_REAL **records**, rejecting
one expected FAILED/MODEL_NOT_CONFIGURED browser refusal. Independent read-only
inspection also showed why provider-name inequality is insufficient: fixture-vlm
is a fixture, and `test-failing-local` / `FAILURE_POLICY_FIXTURE` raises before any
transport in `app/model_routing/replay.py`. An invoked callback is not proof of a
real model call. No record or failure was erased to obtain a pass.

The corrected terminal query/policy explicitly requires zero RUNNING/DONE real
results, zero unexpected real failures, zero invocations outside the exact reviewed
fixture/failure-probe identities, zero owned-draft executions and zero leftover
evaluation schemas. Missing measurements refuse. A host regression tests expected
refusal, forbidden counts and missing fields. Read-only reconciliation passed,
then the complete current-source entrypoint passed with the same required values:
configuration refusals=1; all forbidden counts=0. This changes verification
accuracy, not inference, schema/citation/privacy or acceptance authority.

### Measured baseline, resources and limits

Predeclared workload: ten sequential authenticated fixture task reads through the
local gateway, concurrency one, no warmup. Samples in milliseconds:
6.789, 8.607, 7.227, 7.762, 7.151, 6.544, 6.514, 6.252, 7.005, 7.627;
mean **7.1478 ms**. These are fixture metadata HTTP wall times, not LLM latency,
TTFT, semantic quality or capacity. No performance improvement threshold was
invented. Recovery measurement has its separate restart-command timing scope.

The final qualification watcher recorded **404 samples**, swap **543.50–747.94 MiB**,
minimum free disk **16,861,659,136 bytes**. Docker remained 4,106,604,544 bytes/eight
CPUs, host RAM 8 GiB; service caps were unchanged. All recorded gates passed.
No hard instantaneous host/model RAM quota or future activation authority follows.
No models ran, so no new model RSS/token/speed measurement exists.

All qualification services/native frontend were stopped and grants revoked;
independent final release cleanup verifies listeners/processes/containers and
preserved volumes across both scopes. Exact safe reports remain ignored under
`.local/phase11/nova-phase11-q-615ad1daf73c`; credentials stay private. No secret,
model weight, runtime database/log, generated build/browser output or dependency
artifact enters the reviewed source candidate. The earlier accidental isolated-image
install remains a disclosed historical deviation; final runs used preexisting images.

Retained limits: bounded append pagination, single-host/process assumptions, trusted
operator/database, finite fixture/security/load samples, narrow existing support
subset, no learned quality or real-vector interruption acceptance, no production,
advisory/penetration or Kubernetes/Terraform qualification. Phase 8 deployment
caveats remain unchanged. Phase 9/10 real evidence remains historical and intact.
Phase 10 checkpoint remains HEAD; Phase 11 and local release changes remain
uncommitted, index empty, no remote/push/deployment. **STOPPED AFTER QUALIFICATION.**
