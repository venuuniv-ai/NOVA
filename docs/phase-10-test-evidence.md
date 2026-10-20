# Phase 10 qualification and acceptance evidence

Historical fixture sections began October 19, 2026 without real inference. The
separately authorized real R1 attempt appears at the end. No download, installation
or external action occurred. Evidence/logs/overlays are ignored under `.local/phase10`; private runtime
credentials are under `.secrets/phase10-qualification`. These are local finite
checks, not real-model quality, throughput or production/security certification.

**Latest, October 20: authorized R2 PASS. PHASE 10 COMPLETE in its bounded local
scope.** One Qwen generation selected `noodles` at index 0; application citation,
source/privacy/conflict/permission checks passed. One DONE job/one pending proposal,
zero approval/execution; cleanup verified. Current-source qualification: 750 backend
passes/one opt-in skip, 17 controller, Go race/vet, frontend checks, 58 browser cases
across four passing invocations, Kafka/recovery and golden baselines. Historical
results and failures below remain unchanged; see the appended R2 evidence.

## Results

| Check | Qualified result |
| --- | --- |
| PostgreSQL backend, final source | 747 passed / one separately marked real-model skip, 68.38 s |
| Backend lint / format / compatibility | PASS, 112 app/test Python files, pip check clean |
| Existing controller/process tests | 13 passed, final 0.047 s; zero model loads |
| Go gateway | two race tests, package 1.024 s; vet PASS |
| Frontend | installed-dependency lint, typecheck and production build PASS |
| Replay browser batch A | 38 passed, 41.3 s |
| Replay browser batch B | 15 passed / five explicit auth/OIDC skips, 10.8 s |
| Strict local-auth browser | three passed, 2.8 s |
| Actual local Keycloak OIDC browser | two passed, 2.4 s |
| Phase 10 authenticated fixture Kafka/draft/recovery | PASS, exact quote/UUID, pending approval, reject/cancel, execution denied |
| Legacy Kafka/HITL/duplicate/forgery | PASS, simulated NOT SENT only |
| Broker outage recovery | PASS, two events / same task, 28.591 s from restart command |
| Alembic | 0011_inference_registry head, no drift; no new migration |
| Source isolation / model-disable / cleanup | PASS, no real execution, dedicated volumes preserved |

Browser evidence covers **58 cases across four invocations**: 38 + 15 replay,
three local-auth and two OIDC. It is not a single passing full-profile invocation.
The unchanged 1200/min gateway quota was exceeded by fast full runs; batches were
paced beyond the existing minute window. No quota, assertion, deadline, retry
configuration or source policy was weakened. See the audit for all earlier failures.

The browser/broker runs precede a final one-line defensive job refresh after the
owner lock. A new direct internal concurrency regression exercises a stale caller;
the complete final backend suite was rerun and passed 747/one skip. Frontend and
wire contracts were unchanged; browser/Kafka checks were not relabeled as rerun
after that final service hardening. Earlier 746/one skip, 71.69 s remains history.

## Reproduction commands and environment

Backend command is recorded in the implementation audit. It uses the existing
Phase 9 test overlay, `_test` PostgreSQL, test Redis, empty real registries,
offline flags, 512 MiB DB/runner and 48 MiB Redis, with current source read-only.

```sh
python3 scripts/test_phase9_residency.py
docker run --rm --pull never --network none --memory 384m --cpus 2 \
  -v /Users/pragnyathreddie/NOVA/gateway:/src:ro -w /src \
  -e GOPROXY=off -e GOTOOLCHAIN=local nova-gateway-compiler:local \
  sh -c 'go version && go test -race -count=1 -json ./... && go vet ./...'
```

Frontend uses existing dependencies and browser binaries, telemetry disabled,
Node build heap 768 MiB and server heap 512 MiB. No advisory/toolchain/package
download was performed. In frontend:

```sh
npm run lint
npm run typecheck
npm run build
npm run test:e2e -- tests/continuity.spec.ts tests/evaluation.spec.ts tests/inference.spec.ts tests/intelligence.spec.ts tests/memory.spec.ts tests/models.spec.ts --trace off
# Pace the next batch beyond the existing gateway minute window.
npm run test:e2e -- tests/owned-drafts.spec.ts tests/perception.spec.ts tests/proactive.spec.ts tests/security.spec.ts --trace off
npm run test:e2e -- tests/security.spec.ts --grep 'authenticated local stack' --trace off
npm run test:e2e -- tests/security.spec.ts --grep 'local OIDC provider' --trace off
```

All browser runs have retries=0 and trace=off. Separate authenticated profiles
require dedicated private tokens or local IdP credentials; do not substitute public
fixtures for authentication. OIDC uses only the new local Keycloak service.

Integration project `nova-phase10-qualification` uses compose.yaml, compose.phase8.yaml,
compose.oidc.yaml and ignored `.local/phase10/qualification-overlay.yaml`. Its
real configs are empty, OWNED_DRAFT_MODE=FIXTURE, source read-only and pull=never.
Caps reuse the Phase 9 isolated qualification values: PostgreSQL 192 MiB,
backend/workers 384 MiB each, Redis/gateway 64 MiB each, Kafka/Keycloak 768 MiB
each. Kafka stages stop before OIDC. All eleven named/anonymous volumes are
exclusively qualification-owned and preserved. No protected application volume,
real vectors or model artifact was mounted into this application.

```sh
# Explicit isolated COMPOSE_PROJECT_NAME and complete COMPOSE_FILE required.
python3 scripts/acceptance_phase10.py --inject-duplicates --recovery
python3 scripts/acceptance_phase8.py --inject-duplicates
python3 scripts/reliability_phase8.py --tasks 1 --outage
```

Private NOVA_TOKEN_A/B are environment inputs, never command arguments or logs.
The outage command was run through an ignored wrapper that preserves every
qualification overlay for its explicit Compose stop/up calls, adds no-build and
pull=never, and never raises Kafka limits. The initial Phase 10 harness expected
JSON in a correctly empty 401 response; handling empty expected responses fixed
that harness error without changing authorization.

## Actual application records

Phase 10 task: `b920261a-8d82-4ead-87db-d86ffd15279b`.
Draft request: `aca5f9e7-1bc2-4a7d-a70f-5aa8ecfc6dba`.
Proposal: `3fe3d499-92d5-491b-a237-50503b0ac14c`.
Owner-authenticated fixture generation reached PENDING_APPROVAL; original evidence
was independently verified. No bearer returned 401; other owner returned 404;
approve/execute returned 409 DRAFT_ONLY. Three actual Kafka duplicates caused no
additional proposal, and a forged approval-like envelope produced three dead
letters. Rejection persisted using the existing approval record. A second explicit
fixture draft remained queued while its worker was stopped, then reached pending
after restart and was cancelled. This is queued durability, not an actual
mid-generation process kill; RUNNING recovery and rollback are PostgreSQL tests.

Legacy acceptance task: `c7af81a9-3da9-4751-b2ad-2a7035a641c6`, nine outbox events,
three groups, one job, payload-bound approval and simulated NOT SENT execution.
Broker-outage task: `69b5ae27-0775-4a27-a5aa-394740bc33ad`, same task persisted,
two events drained in 28.591 s. Four continuity HTTP samples are not a load test.

| Golden fixture suite | Run UUID | Result |
| --- | --- | --- |
| FULL baseline | 27f9fcec-d7b8-4a8f-8adc-2909dc5c5392 | 104/104, critical=0, PASS |
| SMOKE baseline | d4c58ec9-6ab7-4c9a-82fa-200802cd7bd2 | 10/10, critical=0, PASS |
| REGRESSION baseline | 2434f07b-aa5f-4d6c-8498-b421a6842c44 | 25/25, critical=0, PASS |
| Cautious negative control | 3dfcdb42-3d93-478d-b0aa-4d8da0c841c2 | 23/25, critical=0, expected FAIL |

Mandatory baseline CLIs exited 0; cautious exited its expected 1. Original golden
labels, thresholds, baselines and all Phase 9 results are unchanged.

SQL before/after backend/auth-profile restarts preserved identical Phase 10 IDs,
owners, task bindings, modes and terminal states. It confirmed zero Phase 10
ActionExecution rows, zero DONE LOCAL_REAL inference runs, empty real configs,
FIXTURE draft mode and zero leftover evaluation schemas. Controlled task/memory
records for the future proposal were prepared without submitting a draft.

## Resources and stop state

Initial read-only snapshot: 8 GiB RAM, swap 1304.81 MiB, approximately
16,513,150,976 bytes free disk; Docker 4,106,604,544 bytes/eight CPUs unchanged.
The task-owned watcher recorded 728 snapshots: minimum free disk 15,478,239,232
bytes, swap 1152.81–1388.69 MiB. No disk/swap gate failed or model was activated.

Initial post-integration stopped snapshot at **05:15:32 America/New_York**: free disk
**15,493,492,736 bytes**, swap **1388.69 MiB**, RAM 8,589,934,592 bytes; Docker
allocation unchanged. These readings do not authorize future activation or promise
allocatable model RAM. No model RSS/tokens/latency were measured in this phase.

The final backend hardening run added 45 watched snapshots, swap unchanged at
1388.69 MiB and minimum disk 15,489,908,736 bytes. Its final stopped snapshot at
**05:20:17** recorded disk **15,490,191,360 bytes**, swap **1388.69 MiB**, unchanged
RAM/Docker allocation, no running containers/listeners and zero model activation.

All task-owned containers, native frontend and watcher stopped. No listeners on
3000/8000/8080/8180/5432/6379/11434/11435/11436; no model process remained. All
volumes/artifacts/data preserved, real modes disabled, no model lease or passing
activation attestation issued. No cache prune, host/Docker restart or allocation
increase occurred. External service spend $0; host compute unpriced.

## Latest continuation: checks after the resource refusal

- Real draft requests/Qwen generations/BGE calls: **0 / 0 / 0**. Frozen real case
  **BLOCKED / NOT EXECUTED**. No request ID or inference measurement exists.
- Host controller tests: **13 passed, 0.046 s**, no models.
- Python candidate AST parsing and 20-path UTF-8 regular-file inventory: PASS.
- Edited lifecycle browser test and owned component TypeScript syntax: PASS using
  installed TypeScript with a 96 MiB Node heap; no typecheck/browser/build claim.
- Bounded credential shapes, private real flags (11 disabled), empty Git index,
  unchanged Phase 9 HEAD/history, no remotes and whitespace: PASS. These bounded
  checks do not certify comprehensive security or secrets absence.
- Added backend checks require wall-clock ordered REQUESTED/QUEUED/RUNNING/
  EVIDENCE_VERIFIED/PENDING_APPROVAL audit milestones and verified-audit rollback.
  Expanded scripted browser assertions cover all seven durable states, cancellation
  controls, hidden non-pending citations/content and safe failure messages.
  **Service execution of these changed assertions remains outstanding.**
- Full backend/Ruff/format/pip/migrations, Go, frontend lint/typecheck/build,
  replay/auth/OIDC, Kafka/recovery/outage and golden: NOT RERUN under failed swap.
  Earlier results above are retained without relabeling as final-source passes.

Read at 12:23:23 America/New_York: disk **15,579,082,752 bytes free**, swap
**2102.81 MiB**, RAM **8,589,934,592 bytes**, Docker **4,106,604,544 bytes / eight
CPUs**. The swap gate still fails; the free-memory percentage is not used as an
override. No task services started, real registry enabled or attestation created.
Independent container/process/listener checks were empty; data/volumes/artifacts
are preserved. Evidence is ignored under `.local/phase10/finish-review-20261019`.
See the latest audit section for blockers and exact scope. **PHASE 10 NOT COMPLETE.**

## October 20 final-source qualification

Actual local execution approximately 01:08–01:17 America/New_York. Current
`drafts.py` SHA-256 is
`b9c239154da11ed8acbbf90816e939c35c96a919184e9f97bb53a6fa0af92881`.
No production/test/prompt/schema correction was made during these runs.

| Current-source check | Result |
| --- | --- |
| Focused `tests/test_owned_drafts.py` | 47 passed, 3.31 s |
| Full PostgreSQL backend | 747 passed, one real-model skip, 68.65 s |
| Ruff / format / pip | PASS; 112 app/test files, no broken requirements |
| Controller/process | 13 passed, 0.057 s; no models |
| Go race / vet | two tests passed, package 1.023 s; vet exit 0 |
| Frontend lint / typecheck / production build | PASS |
| Replay batch A | 38 passed, 41.0 s |
| Replay batch B | 15 passed, five profile skips, 10.6 s |
| Strict local authentication | three passed, 5.9 s |
| Actual local OIDC | two passed, 2.4 s |
| Phase 10 fixture Kafka/draft/duplicates/queued-worker restart | PASS |
| Legacy Kafka/HITL/duplicates/forgery | PASS; simulated NOT SENT |
| Broker outage | two pending events drained in 21.756 s; same task retained |
| Alembic | 0011_inference_registry head; no new upgrade operations |
| Golden baseline FULL / SMOKE / REGRESSION | 104/104 / 10/10 / 25/25, critical=0, PASS |
| Cautious negative control | 23/25, critical=0, expected FAIL/exit 1 |
| Frozen real draft | BLOCKED / NOT EXECUTED; source fingerprint drift |

These 58 browser cases ran over four invocations with retries=0 and trace=off.
Every replay file ran in the documented paced batches. No quota/assertion change
or automatic retry was used. The expanded lifecycle case passed for all seven
states and verifies hidden non-pending evidence, cancellation controls and safe
errors. It is explicitly scripted rendering evidence. Actual queue/cancel and
pending/reject/worker-restart flows used the real dedicated application/Kafka.

The latest backend run includes UTC audit timing, REQUESTED/QUEUED atomicity,
EVIDENCE_VERIFIED/final-proposal atomicity and rollback, unique milestones,
identity/device/source revocation, conflicts, malformed generations, unsupported
citations, idempotency, cancellation, terminal non-revival, worker concurrency and
real-interruption no-retry guards. Original fixture-clock tests passed unchanged.
This is deterministic security/application evidence, not real model quality.

### Commands and isolation

Focused and full runs used the existing capped Phase 9 test overlay:

```sh
docker compose -f compose.yaml -f .local/phase9/final-qualification-20261019/backend-test-overlay.yaml --profile test run --rm --pull never backend-tests pytest -q tests/test_owned_drafts.py
docker compose -f compose.yaml -f .local/phase9/final-qualification-20261019/backend-test-overlay.yaml --profile test run --rm --pull never backend-tests sh -c 'pytest -q && ruff check app tests && ruff format --check app tests && pip check'
python3 scripts/test_phase9_residency.py
```

The first focused invocation included unsupported `run --no-build` and exited 1
before tests. Correcting the runner option used the existing image without builds;
no source/assertion/dependency change was required. Subsequent required checks
passed; the cautious CLI retained its expected nonzero exit.

Go, frontend/browser, acceptance and golden commands are the same documented
commands above, now against final source. `COMPOSE_PROJECT_NAME` was explicitly
`nova-phase10-qualification`; `COMPOSE_FILE` included compose.yaml,
compose.phase8.yaml, compose.oidc.yaml and the existing bounded qualification
overlay. Every `up` used `--no-build --pull never`; the broker restart wrapper
preserved all overlays/caps. Kafka stopped before OIDC. Only installed dependencies,
browser binaries and existing images/compiler were used. Test DB/runner retained
512 MiB caps; integration and Node heap limits stayed unchanged. Private tokens
and local OIDC credentials were environment/private-file inputs, never command
arguments or browser traces. The exact command/exit ledger and logs are ignored
under `.local/phase10/qualification-20261020`.

### New actual records

- Phase 10 FIXTURE task `0972c17c-fe0d-41bb-b3c8-18ae6a2ea73e`, draft
  `2b975cda-6641-45eb-ad86-c3db092af85e`, proposal
  `2f9ed721-df50-4826-b4f9-2281ad6ce504`. Original UUID/quote verified, one DONE
  job/proposal, pending before explicit rejection, approve/execute refused, foreign
  owner 404/no bearer 401. Three duplicate envelopes had no extra effect; forged
  authority produced three dead letters. Another queued fixture draft survived
  worker stop/restart and was cancelled. No real generation or external action.
- Live SQL verified unique current-UTC REQUESTED/QUEUED/RUNNING/EVIDENCE_VERIFIED/
  PENDING_APPROVAL/REJECTED audit milestones, a rejecting decision only and zero
  execution rows. This does not claim a real mid-generation process kill.
- Legacy task `ec93c2b1-837b-4f37-8b13-0c548ab5df05`, proposal
  `03eec024-d459-45cf-9c88-9002612fbafa`: nine outbox events/three groups/one job,
  payload-bound approval and SIMULATED / NOT SENT. Outage task
  `cba14508-3288-4146-996e-7575caa509f1` preserved two pending events; recovery
  21.756 s. Four continuity HTTP samples do not qualify sustained load or HA.
- Golden FULL `926541c6-5806-40b2-9e7d-8c29a4fb87df`, SMOKE
  `d65f8e36-e1e9-4533-bba3-0e64f1e9ad47`, REGRESSION
  `4079a448-e1da-4ccf-a0d7-878df4927ae4`, cautious
  `2f28c446-914b-4b25-b89e-7aca45d24bc4`. Expected labels/thresholds unchanged.
- Draft metadata snapshots matched across backend/OIDC restarts. Zero Phase 10
  executions, zero DONE LOCAL_REAL inference rows and zero evaluation schemas.
  Frozen task/source/binding remain intact; frozen request row count is zero.

### Real boundary, resources and cleanup

Exactly one production fingerprint differs from the frozen review:
`backend/app/proactive/drafts.py`, previously
`8ce187f969f521981b10ea977f264bdad226fd1ad713e0907d5564a3ed67407e`, now the qualified
hash above. All other production hashes and frozen proposal bytes match. Per the
operator's explicit drift stop rule, no real request, generation, model acquisition
or passing attestation occurred. No real IDs, tokens, latency or sampled RSS exist.
The original frozen proposal/hash file was preserved; later operator review must
resolve this source change before the single frozen real case can execute.

Read-only initial swap 1935.12 MiB passed; prior swap causation remains unknown.
No task-owned orphan needing termination was identified; unrelated editor/system
processes were left alone. Resource watcher: **243 samples**, swap
**1743.12–1927.12 MiB**, free disk minimum **14,864,408,576 bytes**, no violation.
At **01:17:32** final cleanup: **1743.12 MiB swap**, **14,935,461,888 bytes disk**,
**8,589,934,592 bytes RAM**, Docker **4,106,604,544 bytes/eight CPUs**, unchanged.
These are snapshots, not future activation authority or guaranteed allocatable RAM.

No running container, task frontend/watcher, model/controller process or listener
on the application/database/broker/model ports remained. Eleven inventoried
exclusive volumes and all protected data/artifacts/vectors were preserved. Three
scoped qualification identity grants were revoked; eleven private model registries
remain resource_approved=false. No real configuration or activation attestation was
enabled. No cache/volume deletion, install/download, paid/cloud traffic, external
message, Git write or Phase 11. Offline qualification is complete; **PHASE 10 NOT
COMPLETE** solely pending the mandatory frozen real acceptance/authorization gate.

## Authorized R1 preflight — BLOCKED / NOT EXECUTED

October 20, approximately 02:00–02:02 America/New_York. The operator approved R1's
qualified `drafts.py` hash and the original single request. Production/test source
still matches the 747/47/13 and complete cross-stack qualification above; no heavy
suite was rerun or old result relabeled as a new model measurement.

Passed fresh source/proposal/request/artifact and loopback-sandbox checks. Read-only
fixture/wire checks returned the unchanged prompt/schema fingerprints, source
binding `8dbd48c85725bf97c29be220182aa1ae8ff52a2f32165bd745b1dfcd691de827`, 469/512
bound, owned ACTIVE original source and zero frozen request/real-draft rows.

The strict device prerequisite failed: the task's owned origin DESKTOP device
`00000000-0000-4000-8000-000000000010` has **no DeviceRegistration row**. This is
not a disabled registration or wrong owner. No registration was created or other
device substituted. The existing temporary owner identity remains disabled from
prior cleanup; no new scoped token/grant was issued. The check stopped before
authenticated API reads/submission, worker/controller startup or model acquisition.

| Actual real case observation | Result |
| --- | --- |
| Outcome | BLOCKED / NOT EXECUTED: DEVICE_REGISTRATION_MISSING |
| Authenticated draft POSTs / Qwen generations / BGE calls | 0 / 0 / 0 |
| Inference retries / external actions | 0 / 0 |
| Actual request trace / draft / job / proposal IDs | none |
| Model answer / evidence index | none |
| Model tokens / model-call or request latency / RSS | not measured; no request/model ran |
| Source UUID/quote/binding | verified before generation; original fixture unchanged |
| Positive citation/final post-generation privacy validation | not exercised |
| Approving decisions / execution / external message | none created by this scope |

Initial swap **1679.06 MiB**, free disk **13,748,121,600 bytes**. Twelve watched
samples remained within swap **1663.06–1671.06 MiB**, minimum disk
**13,745,176,576 bytes**. Final cleanup at **02:02:39**: swap **1663.06 MiB**, disk
**13,744,967,680 bytes**, RAM **8,589,934,592 bytes**, Docker **4,106,604,544 bytes /
eight CPUs**, unchanged. No resource violation or limit increase.

All started application/database services stopped; no workers/controller/model
started. Scoped Qwen approval false, operational overlay reset to FIXTURE/empty
real settings and scoped attestation closed. No active lease or new token remained.
Independent checks found no containers, models or relevant listeners; eleven
inventoried volumes and all original data/vectors/artifacts were preserved.

A read-only diagnostic initially shadowed Python's `inspect` module with the
operator filename `/inspect.py`; correcting its container path to `/device_check.py`
returned the exact registration metadata. No acceptance or inference was retried,
no production change or weakened assertion occurred. See the audit for evidence
scope. Logs/snapshots and the approved pre-execution R1/overlay copies remain
ignored under `.local/phase10/r1-acceptance-20261020`; closed secrets stay private.
**R1 scope closed. PHASE 10 NOT COMPLETE — missing registration/valid scoped
owner-device authorization and the mandatory positive real acceptance remain open.**

## Supported device recovery — PASS, real inference explicitly excluded

October 20, approximately 02:19–02:21 America/New_York. No production/test source
changed, so the preceding complete final-source qualification remains applicable;
no heavy suites were rerun. New actual recovery evidence:

| Check | Actual result |
| --- | --- |
| Before enrollment | Correct owned Desktop; no registration row; compatibility view version 0 |
| Supported authenticated registration API | One POST, 200; enabled registration version 1 |
| Bootstrap credential after enrollment | 401, old device epoch correctly refused |
| Fresh operator-CLI credential | Authenticated API reads and application authenticate passed |
| Binding | Same owner/task/identity/device; current signed identity/device versions match |
| Duplicate registration | Exactly one row for the original device primary key |
| Frozen fixture/prompt/schema/budget | Unchanged; original source binding; 469/512 bound |
| Frozen real request / real draft rows | 0 / 0; no competing queued/running owned jobs |
| Controller authentication | Static inventory/host reachability PASS; zero acquisitions |
| Model aliases/tensors/blobs | Fresh read-only integrity PASS |
| Cleanup credential | Identity revoked through supported CLI; fresh token now returns 401 |
| Preserved enrollment | Same owned Desktop, enabled version 1 |
| Real draft/Qwen/BGE/retry/action | 0 / 0 / 0 / 0 / 0 |

Device `00000000-0000-4000-8000-000000000010`, owner
`00000000-0000-4000-8000-000000000001`, existing identity
`c8492b8d-7b54-4bdd-949e-65b75cad91c1`. Identity version was 5 at successful
credential verification and was subsequently invalidated during cleanup. No
identity/device credential was fabricated; existing CLI used the real local signing
key and the normal authenticated registration API committed the enrollment.

Confirmed mechanism: CLI/seed device/identity provisioning does not insert a
DeviceRegistration. The prior preparation omitted the separate enrollment step;
compatibility listing defaults to enabled/version 0 without an actual row. No
migration or security policy change was needed. These are simulated device grants;
no hardware attestation or interactive pairing claim follows.

Five resource boundaries all passed: swap **1655.06 MiB**, disk minimum
**13,708,656,640 bytes**. Final independent cleanup at **02:21:36**: disk
**13,713,174,528 bytes**, swap **1655.06 MiB**, RAM **8,589,934,592 bytes**, Docker
**4,106,604,544 bytes/eight CPUs**, unchanged. No containers, model/controller
processes or relevant listeners remained. FIXTURE/empty real config verified;
twelve private real flags remain false. Readiness snapshot is closed and never
approved model load/inference. All eleven inventoried volumes and all original
fixture/data/vectors/artifacts were preserved.

Recovery evidence is ignored under `.local/phase10/device-recovery-20261020`.
Temporary identity/token revoked; registration preserved. **R1 ready for fresh
explicit approval only.** The recovery authorization expressly excluded the real
case, so Phase 10 remains NOT COMPLETE pending that separately authorized positive
acceptance. Historical blocked scopes and all prior measurements remain unchanged.

## October 20 — authorized real R1 attempt: FAIL

This section is real execution evidence, separate from fixture qualification.
Approved R1 fingerprint `0ee038ebbd97ec4cd01c3d8172a2ff3582131120d281caf351dedff1ca900d67`;
qualified source/prompt/schema/469-token bound/artifacts/fixture binding unchanged.
Fresh legitimate identity version 7 and preserved device registration version 1
passed actual authentication/ownership checks before the exact single POST.

- Request key `15d88b00-b223-429e-88cd-c1a6b160daf2`; HTTP correlation
  `34a7dea9-c2fc-4672-bd28-265da406cff7`.
- Draft `2ac3dd25-5854-443a-8bd7-67f8dc37fa76`; worker trace
  `57b6aea1-c387-4ac5-b510-8910e1869851`.
- One POST, HTTP 202, wall 925.610 ms/server 917.950 ms. One Qwen inference
  attempt, zero completed responses observed, zero BGE calls/retries/extra calls.
- CPU loading was interrupted by swap RESOURCE_GATE; controller HTTP 409 and
  OWNED_DRAFT_FAILED milestone. No model answer/index or final positive citation/
  privacy validation. Job UUID/final database counts were not independently read
  after resource shutdown; no pending proposal was observed or claimed.
- Tokens/finish reason/model-call latency/peak RSS UNKNOWN. The controller's final
  failing resource read prevented residency.json persistence after termination.
- Swap 1647.06 MiB pre-POST, 1948.50 last passing watcher sample, 2072.62 stopped
  driver snapshot. Disk stayed above 5 GiB at sampled boundaries. Final independent
  snapshot 13,723,414,528 bytes free/2064.62 MiB swap; RAM/Docker unchanged.
- Independent no-process/listener/container cleanup, token revoked/401, private real
  flags false, closed attestation, scoped launch FIXTURE, eleven volumes preserved.

Detailed limits/unknowns and remaining gates are in the final audit section. Logs
remain ignored under `.local/phase10/r1-final-acceptance-20261020`. No production or
test change, new qualification pass, model quality sign-off or Phase 10 completion
is inferred. **FAIL; PHASE 10 NOT COMPLETE.** Consumed scope closed, no retry.

## R1 resource diagnosis — verified database outcome and offline corrections

Read-only transaction/ROLLBACK against isolated Phase 10 PostgreSQL confirms draft
`2ac3dd25-5854-443a-8bd7-67f8dc37fa76` FAILED/DRAFT_INVALID; job
`6bfba979-0483-4c6b-86df-3d5a89fa434e` DEAD, attempts=1, result_id=null. Exactly
one frozen request; zero proposals/ApprovalDecisions/ActionExecutions. Outbox
`15e47750-22d7-4a5e-8dd2-340ffda9a6d2` PUBLISHED/attempts=1; three inbox rows
(proactive/projection/audit). Four milestones REQUESTED/QUEUED/RUNNING/FAILED;
no verified/pending milestones. This resolves the earlier uninspected-count limit.
No failed row, fixture, source binding or model artifact changed.

Final focused commands used the existing backend-test overlay/image and guarded
_test database: pytest -q tests/test_owned_drafts.py (**50 passed, 3.52 s**), Ruff
check/format and pip check PASS, 112 app/test files. Host
python3 scripts/test_phase9_residency.py: **17 passed, 0.125 s**. Controller Ruff/
format PASS in existing network-disabled image, 128 MiB/one CPU. Earlier 49 focused
passes preceded the added jobs-mode dependency check; final 50 supersede that
snapshot only. No new full-suite, browser, Go, Kafka, golden or model-quality pass.

New deterministic failure cases exercise strict swap refusal before transport and
during simulated loading, retained unsafe snapshots, non-model child termination,
atomic record replacement failure/controller poisoning, durable failed job/no retry/
no duplicate/no authority and no broker connection from jobs-mode. No real models,
new packages, paid/network model calls, draft POSTs or active attestations.

Current controller persists transitions and unsafe shutdown metadata; original R1
RSS/usage remains unrecoverable. Source hashes and full exact proposed request are
in [R2](phase-10-real-acceptance-proposal-r2.md), which remains unapproved and gated
on <1024 MiB initial swap headroom plus all existing hard limits. Evidence remains
ignored under `.local/phase10/r2-resource-diagnosis-20261020`. Phase 10 NOT COMPLETE.

## Final current-source qualification after R1 controller corrections

Current source, October 20 approximately 03:09–03:24 America/New_York. No production
or test changes during qualification; prior resource-refusal/recording fixes retained.

| Gate | New actual result |
| --- | --- |
| Full guarded _test PostgreSQL pytest | **750 passed, 1 explicit real-model skip, 68.70 s** |
| Ruff lint/format/pip | PASS, 112 app/test files |
| Host controller/process tests | **17 passed, 0.141 s**, no models |
| Go race/vet | 2 passed, package 1.021 s; vet PASS |
| Frontend lint/typecheck/build | PASS, existing dependencies |
| Replay A / B | 38 passed (44.7 s) / 15 passed (10.7 s), 5 profile skips |
| Separate local-auth / corrected local OIDC | 3 passed (6.1 s) / 2 passed (2.5 s) |
| Kafka/fixture draft/duplicates/queued-worker restart | PASS |
| Legacy HITL and actual broker outage | PASS, two recovered events in 31.076 s |
| Golden FULL / SMOKE / REGRESSION | 104/104 / 10/10 / 25/25, zero critical |
| Cautious negative control | 23/25, expected FAIL/exit 1 |
| Staged FIXTURE topology | PASS with only PostgreSQL/jobs worker during generation |
| Alembic current/check | 0011_inference_registry head/no new operations |

Browser coverage is 58 cases across four passing invocations, retries=0/trace=off;
not one passing full-profile invocation. The initial OIDC run had one fail/one pass
because native frontend issuer URLs were missing. Correct documented localhost
URLs fixed the environment; unchanged tests then passed. A subsequent wrapper
parsed None instead of its written snapshot; independent file comparison verified
persistence, and later staged restart confirmed it. A read-only metadata query
initially used wrong auth table names; corrected names passed. These failures are
retained and not counted as passes. No application code/assertion/security/limit
change or automatic test retry was used.

Actual new fixture task 67a26ac6-e4e2-45dc-b992-c7ad80f57024, draft
0ab2bd5f-0907-431c-a70b-768776c5d5c1, proposal 7fb2eda5-349f-478f-96b0-ee994fbb0055:
one DONE job/proposal, exact quote/UUID, ordered unique UTC milestones, explicit
rejection only, zero execution. No bearer 401/foreign owner 404, DRAFT_ONLY approval/
execution denial, duplicates harmless/three forged-event dead letters. Queued
restart/cancel passed; no actual mid-generation kill experiment claimed.

Legacy task 0b2413cf-355c-457d-90f2-8d94bd7eb4c1, proposal
464db2ea-fad0-4586-8dc5-f253cd13e2b2, nine events/three groups/one job, NOT SENT.
Outage task 4b3da2a9-d8cb-42e4-8491-513c3c979e03 recovered two events in 31.076 s.
Golden runs: FULL e9aed1ac-acb4-425c-8441-1f44c1c87b78, SMOKE
10f3941f-26f5-4592-92dd-238df3ad1f9a, REGRESSION
1497956a-293e-4e6f-b493-3fbf703e6d64, cautious
55e4fcf6-12cf-4120-a8a6-66c7695b6a1d. Original labels/baselines unchanged.

Staged fixture draft ea3c25bd-0be7-4772-a7b0-63379e8c1aca, job
16437ceb-1a99-4999-b6f1-7b82149d562d, proposal
07d769f7-2cd1-4883-b65d-067df6cf113b: authoritative Kafka-created PENDING job,
broker/API/Redis stopped, --no-deps worker alongside only PostgreSQL reached DONE/
PENDING_APPROVAL, exact evidence verified after API restart, no approval/execution,
then explicit cancellation. This is operational FIXTURE staging, not a real R2 case.

All qualification used existing capped images/source RO/installed dependencies,
sequential stages, explicit isolated Compose files/project, unchanged gateway quota
and limits. Exact commands/exit logs/resources/SQL are ignored under
.local/phase10/finish-offline-20261020; fresh temporary private credentials under
.secrets/phase10-finish-offline-20261020 were revoked at cleanup. Detailed current
resources, command scopes and remaining blockers are in the final audit section.
R1 remains FAILED/DEAD/attempts=1, R2 rows=0, Phase 10 execution rows=0, no evaluation
schemas. Enabled original Desktop version 1 preserved; all three grants disabled.
No real model ran or activation attestation issued. **PHASE 10 NOT COMPLETE.**


## October 20 — R2 acceptance evidence and completion

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
