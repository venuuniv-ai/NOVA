# NOVA v1.0 local release evidence

October 20, 2026, America/New_York. **READY for the defined prepared-host local MVP, completed before the October 21
deadline.** Defined scope: authenticated local MVP with
explicit deterministic FIXTURE AI default, real inference disabled, no external
execution. No new real-model generation is authorized by this release mission.

Phase 10 checkpoint verified at `80dc41af8d3742fdb700b02e342f579e06389fcf`; no new
checkpoint is necessary or authorized for release changes. Phase 11/current app
qualification already passed 762 backend cases/one opt-in real skip, 17 controller,
10 runner safety cases, Go race/vet, frontend lint/typecheck/build, 60 browser
cases across four separate profiles, actual Kafka duplicate/forgery/recovery and
golden baseline suites. Exact retained results and final reconciliation appear in
the Phase 11 evidence, preserving all intermediate failures.

The last Phase 11 overall runner status was FAIL at its terminal SQL assertion,
after every functional stage passed. Read-only inspection found one FAILED /
MODEL_NOT_CONFIGURED LOCAL_REAL run, zero owned-draft executions and zero evaluation
schemas. This is the expected refusal browser case, not inference. Attempt metadata
contained fixture/fixture-vlm and the explicit FAILURE_POLICY_FIXTURE test double;
provider names must not be guessed to be real from string inequality. Correction
checks for forbidden RUNNING/DONE real results rather than suppressing expected
failure records. The original failed report remains unchanged.

Fresh MVP validation and final artifact/cleanup status will be appended after
startup, smoke, recovery and shutdown complete. No historical model metric is
relabeled as a new release measurement; missing usage stays UNKNOWN.


## Final P0 release decision — READY

Completed October 20, 2026, America/New_York. Every P0 gate in the release checklist
passed. Scope is authenticated persistent local workflows with explicitly labeled
FIXTURE AI. Existing learned BGE/Qwen/RAG/draft integration and accepted real results
remain in source/history; this release does not activate them or claim a new learned
answer. No P0 blocker remains. P1/P2 items are deferred as listed, not relabeled PASS.

### Fresh release lifecycle

`./scripts/start-local.sh` started the dedicated `nova-v1-local` project using only
existing images, installed Node dependencies and a generated standalone frontend.
Resource checks ran during startup commands, then a persistent two-second watcher
continued sampling. Fresh operator credentials were issued through the existing CLI;
Desktop was enrolled using the authenticated device API, then a new version-bound
token was issued. No revoked enrollment credential was reused. No private model
registry, artifact, alias, resource approval or model activation attestation changed.

First authenticated smoke: task `7ec2c18b-c9cd-451c-b163-b466728899ab`, memory
`f96cf194-fde5-416c-bab4-a97e950f18a0`, draft
`b1875cb3-5926-4de1-8a10-d4532513d6cc`, proposal
`d69a3760-34a7-434f-b92d-9f6c862d9919`, fixture RAG run
`96263988-4daa-4584-9280-05c2b7c813b9`. Task/memory, original UUID/full quote,
one durable draft/proposal, explicit rejection after pending, approve/execute
refusal, Mobile handoff persistence and three existing strict-auth browser cases
passed. No real-model generation or external message.

Documented shutdown and `python3 scripts/nova_local.py recover` passed. The original
task and memory UUIDs persisted; the task remained on the authoritative Mobile
device, Desktop registration remained enabled/version 1, old credentials returned
401 and fresh credentials worked. The first recovery inspection wrongly guessed a
device UUID suffix; replacing that guess with the server's actual device list
passed without changing any data or expected Mobile assertion. Permissions on old
drafts can become stale after revocation by design; no persistence claim overrides
privacy/version revalidation.

Second fresh smoke after recovery: task `d0bb502c-7f45-4316-a1ef-f6839aa8a71c`,
memory `a42476e0-9b67-4994-98e1-581882cebe84`, draft
`4ad8e935-d77e-436b-8ec8-275bd1337d83`, proposal
`6bff686e-7a9f-4815-938c-bd702462c0a6`, fixture RAG run
`d367c93f-f174-40c1-a808-91bff60de3ca`: PASS, including the same three browser cases.
Those are repeated journeys, not six new unique cases. Fixture tokens/cost/speed
are not invented or represented as learned inference measurements.

Independent READ ONLY SQL verified this final draft's FIXTURE mode, REJECTED state,
exactly one DONE durable job, one proposal, zero approving decisions, zero executions
and zero LOCAL_REAL inference rows in the release database. The first inspection
used the same SQL bind for UUID and JSON text and was refused by PostgreSQL; explicit
casts fixed only the read-only helper. No job/request/data was retried or mutated
by that inspection. The two smoke cycles are separate deliberate fixture tests.

### Regression and safety

The complete current application qualification then passed in
`nova-phase11-q-615ad1daf73c`: 762 backend/one explicit real opt-in skip, 17 controller,
11 qualification-runner cases, Go race/vet, frontend lint/typecheck/build, migration
checks, 60 browser cases over four separate profiles, Kafka duplicate/forgery/
queued-worker/broker recovery and golden FULL 104/104, SMOKE 10/10, REGRESSION 25/25.
Cautious remains 23/25 with expected FAIL/exit 1. The corrected terminal policy
also passed. The full command returned overall PASS; no failed report was overwritten.
Exact IDs, timings and intermediate failures are in Phase 11 audit/evidence.

Release lifecycle guards: **six deterministic tests passed**, including private
0600 files, PID-reuse refusal, source-drift refusal, resource refusal before work
continues, child termination and cleanup bypass of the work gate. Script Ruff
lint/format, Python syntax and shell syntax passed. No production behavior beyond
already qualified operational metadata/UI was changed for release. There was no
new package/image/model installation or download in this release execution; the
older Phase 11 isolated-image installation deviation remains disclosed separately.

### Resource and cleanup evidence

During MVP lifecycle validation, **407 recorded samples** had maximum swap
**5.25 MiB**, minimum free disk **17,243,467,776 bytes**. Independent stopped-host
reading later measured **575.50 MiB swap** and **17,248,403,456 bytes free disk**
at 14:53:12. The host-wide increase after the watcher stopped was not causally
attributed; no model ran. All recorded readings passed unchanged thresholds.
The separate final qualification recorded 404 samples, swap 543.50–747.94 MiB,
minimum disk 16,861,659,136 bytes. Keep these scopes separate. Docker remains
4,106,604,544 bytes/eight CPUs, host 8 GiB; caps and timeouts unchanged. No new model
RSS/latency/token or instantaneous quota claim.

Before shutdown, revocation through the existing CLI was independently checked
with HTTP 401 while the API was still listening. Final `stop-local.sh` returned
STOPPED/credential_revoked=true. No running containers, known model/frontend/
watcher processes or task listeners remained on 3000/5432/6379/8000/8080/8180/
11434/11435/11436 at the independent check. Ten release data volumes were inspected
as exclusively mounted by stopped release containers and preserved; original
application/qualification volumes and vectors remain untouched. Fifteen inspected
private real-registry flags were false. Database/token files are mode 0600.
All final-qualification services and grants were subsequently stopped/revoked too.

### Candidate, recovery and retained limitations

The source-only archive `.local/release-v1/nova-v1.0-local-rc1.tar.gz` is generated
from tracked source plus the exact reviewed Phase 11/release inventory. The packager
refuses unrelated candidates, private/generated paths, model/database/key artifacts
and credential-shaped content; every archived member is read back and hash-checked.
The shipped `release/local-v1.0.json` pins runtime source hashes; startup refuses
drift. Archive SHA-256/file count are recorded in ignored `package.json` to avoid a
self-referential checksum in the archive. The first packaging scan matched its own
PEM-marker source literal; anchoring the actual PEM-header pattern corrected that
false positive. Git's collapsed `release/` status then required explicit untracked
file expansion. Both were packaging-helper refusals, not accepted secrets or
application failures. No unsafe file was silently excluded to force a PASS.

The guide documents prerequisites, login, use, health, smoke, token rotation,
shutdown, recovery, privately preserving data/credentials, checksum/source recovery
and rollback without volume deletion or database downgrade. Archive round-trip
integrity and current stop/start data recovery were tested; arbitrary future
cross-version database rollback is not claimed. This prepared-host candidate does
not include installed dependencies, Docker images, credentials, weights or user data.

Limits: FIXTURE AI default; real-model activation needs separate scoped approval;
narrow named-preference support, exact-value/quote verification rather than general
semantic entailment, single trusted local host/operator, sampled resources, one-hour
credentials and stale-draft invalidation after revocation. No production capacity,
public deployment, real vision/judge, sustained/streaming model benchmark, advisory/
penetration certification or Phase 8 Kubernetes/NetworkPolicy qualification.

Phase 10 checkpoint remains `80dc41af8d3742fdb700b02e342f579e06389fcf`; Phase 1–10
history is preserved. Phase 11/release source changes remain uncommitted, index
empty, no remote/push. External API/infrastructure spend $0; host energy unpriced.
**READY TO LAUNCH LOCALLY WITH THE DOCUMENTED COMMANDS; STOPPED AFTER VALIDATION.**
