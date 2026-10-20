# Phase 11 test evidence

October 20, 2026 (America/New_York). Local deterministic qualification only.
Baseline Phase 10 checkpoint: `80dc41af8d3742fdb700b02e342f579e06389fcf`.

**Final complete qualification PASS; PHASE 11 COMPLETE in its bounded offline
scope.** No model execution or deployment. The final section supersedes earlier
pending dispositions only; historical failures/counts remain intact.

## Reproduction and isolation

The source entrypoint is `python3 scripts/qualify_phase11.py`. It uses installed
tools and explicit existing images, no paid/model transport, fresh isolated Compose
projects, read-only source and dedicated test/application data. Generated overlays,
logs, numerical resource samples and reports remain ignored under `.local/phase11`;
credentials remain mode-0600 under `.secrets/nova-phase11-q-*`. No protected Phase
9/10 application volume or real registry is mounted. `--stages` gives PARTIAL_PASS
when successful, never full qualification. Failed attempts are retained separately.

Initial focused PostgreSQL command passed 59 cases in 4.35 s. The initial full
application suite passed 759/one skip in 71.33 s but the combined command failed
import-order lint. Corrected-root qualification passed 759/one skip in 70.99 s with
all lint/format/pip checks. Adding signed-bigint cursor bounds required new tests
and another complete backend run, not relabeling those earlier counts.

Final backend snapshot: **762 passed, one explicit real-model opt-in skip,
73.65 s**. Ruff lint/format PASS, 113 app/test files; pip check PASS. Mandatory
autouse setup requires a `_test` database, upgrades Alembic head and checks drift.
Current host pass: **17 controller tests and 10 runner tests** in separate commands.
The controller uses fake callbacks and tiny non-model subprocesses. The runner
tests use controlled command failures/process groups/mocked orchestration; their
deliberate FAIL/PARTIAL_PASS report output is assertion evidence, not live failure.

Existing compiler-image Go race/vet and installed-dependency frontend checks passed
on the prior identical application/UI snapshot. Current complete entrypoint will
run them again before integration; exact final results belong below. There is no
configured backend static type checker or separate frontend unit/component runner.
None was installed or represented as executed.

## Security and correctness coverage

Pagination tests exercise independent event/job cursors, duplicate-free immutable
sequence ordering, append high-water exclusion, bounds including signed-bigint
overflow, empty histories, page size 100, bounded query count and no source/provider
body exposure. Real local JWT tests assert owner success, no-bearer 401, operator
role requirements, foreign operator 404 and revoked identity 401. Existing device,
source/privacy/conflict, idempotency, cancellation, atomic acceptance and owner
regressions remain in the full suite.

The new interrupted-real-work regression is scripted: after a stored RUNNING
LOCAL_REAL context, manual retry/redelivery must never call the provider or create
a proposal/ApprovalDecision/ActionExecution. Existing resource/controller tests
cover swap refusal during loading, exact ceiling, record persistence failure,
termination and poisoned subsequent acquisition. No real process/model crash is
claimed. Runner tests verify admission failure before child creation, protected
project/mount/volume refusal, one failed command with no retry, partial-stage
classification, cleanup failure, actual tiny child-group termination and subnet
collision/exhaustion. New browser operations journeys explicitly script transport;
they do not measure real delivery or model behavior.

## Intermediate environment failures

See the implementation audit for full details. Retained attempts include unsupported
Compose-run `--no-build`; an accidental isolated test-image build/install caused by
an unspecified test-image name; wrong-root import ordering; read-only Ruff-cache
refusal corrected with `--no-cache`; preflight refusal of legitimate read-only
observability binds; exhausted default Docker address pools; null IPAM metadata;
and the legacy fixture harness refusing the new Phase 11 project prefix. No failed
required command was counted as passing, no assertion/quota/resource bound changed,
and no automatic test retry was enabled. Only reviewed explicit image/subnet/project
handling was corrected. The install deviation prevents a blanket claim that the
entire investigation performed zero dependency installation: host dependencies
and source dependency versions stayed unchanged; final qualification uses the
preexisting explicitly named image. No model/runtime download or installation.

## Final integration evidence

Pending completion of the full current-source runner invocation
`.local/phase11/nova-phase11-q-4bd0beceeb2b`. Predeclared workload: ten sequential
authenticated fixture task reads, concurrency one, no warmup; one broker-outage
task; baseline golden suites and unchanged cautious negative control. Browser
replay is paced across two quota windows; local and OIDC authentication run in
separate profiles. Retry count is zero, tracing disabled. Exact run IDs, timings,
sample scopes, resource range, terminal database invariants and independent cleanup
must be recorded before completion. No speed, quality, penetration/security,
production capacity or deployment certification is implied.


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
