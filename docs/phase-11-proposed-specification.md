# Phase 11 proposed specification — scope review required

Prepared October 20, 2026 (America/New_York).

**Phase 10 COMPLETE and locally checkpointed. Phase 11 NOT COMPLETE: proposed
scope only; no Phase 11 application implementation or qualification has run.**

The operator instructed scope discovery and implementation only where Phase 11
is already defined. If it is undefined, the instruction explicitly requires a
proposed specification and a stop before arbitrary implementation. This document
fulfills that preparation boundary; it does not establish an official phase title,
approve its proposed features or authorize real inference.

## Discovery and existing requirements

Reviewed README's Costs and roadmap, architecture documents, phase specifications,
Phase 9/10 handoff and acceptance/audit/evidence records, engineering constraints,
existing security/event/controller interfaces and relevant TODO/phase references.
No Phase 11 specification, mandatory feature list or acceptance matrix exists.
The repository's `NovaAI` file is empty. No Phase 11-named file existed before this
proposal. Historical prohibitions on Phase 11 are authorization records, not a
definition of its implementation scope.

The only phase-specific direction is the historical Phase 9 final audit's statement
to “close measured reliability/security/performance gaps for Phase 11.” It also
explicitly says the roadmap is not an implementation-ready Phase 10–12 specification.
See [that handoff](phase-9-final-audit.md) near its SELECTION_V1 offline section and
the [README roadmap](../README.md#costs-and-roadmap). Phase 10 remains the bounded
named-preference draft workflow, not a complete general-purpose agent platform.

**Official Phase 11 title: not defined.** Proposed title for review:
**Local reliability, security and operational qualification**.

The following work packages and acceptance criteria are proposals, not discovered
requirements or claims of implementation. Scope approval is the next step.

## Phase 10 checkpoint and preserved baseline

- Commit: `80dc41af8d3742fdb700b02e342f579e06389fcf`.
- Message: `feat(phase10): complete proactive drafts and approval workflow`.
- Parent: `7765b33736c28ccc560fc8269bb5fc4b9b050518`.
- Exactly the 24 reviewed manifest paths committed: 12 modified / 12 added.
- All nine Phase 1–9 ancestors preserved; index and working tree clean immediately
  after the checkpoint; no configured remote and no remote operation.
- All 17 R2 frozen source hashes and qualified application/test hashes still match.
  Original/R1 proposals, historical audits and golden baselines are preserved.
- Bounded candidate review: UTF-8 regular files, Python syntax, staged inventory
  equality, staged whitespace and credential-shape checks passed. Machine-specific
  paths are historical local reproducibility references; private configs, tokens,
  weights, runtime logs/databases, caches and generated build output are excluded.
  This review is not a comprehensive secret-detection/security certification.

The existing R2 evidence was read, not rerun: draft
`a0571679-0f5c-4b40-8d9a-775f5170c8d8`, proposal
`af08ea0d-56ab-4db9-aa73-9c90c8c88646`, generated `noodles` at index 0,
162 input/19 output tokens, one generation, zero retries/BGE calls, one DONE job,
one pending proposal, zero approvals/executions/messages. Citation/source/current
permission/privacy/conflict verification passed at acceptance. Cleanup subsequently
revoked the temporary grant; the acceptance snapshot does not authorize continued
use under revoked credentials. No draft was submitted during checkpoint review.

Qualified baseline retained: 750 backend passes/one explicit model-opt-in skip,
17 controller passes, Go race/vet, frontend lint/typecheck/build, 58 browser cases
across four passing invocations, actual Kafka recovery and baseline golden
104/104, 10/10, 25/25. The cautious 23/25 negative control remains an expected failure.
These historical checks are not new Phase 11 passes.

## Proposed objective and work packages

Make the existing local system's failure handling and qualification reproducible
under its resource limits, with bounded operational metadata and explicit security
tests. Preserve Phase 10's draft-only authority and Phase 9's narrow support contract.

| Order | Proposed work | Concrete reviewable result |
| --- | --- | --- |
| 1 | Qualification orchestration | One operator-run, local-only entrypoint for staged offline checks, explicit existing images, readiness checks, bounded resource monitoring and cleanup. Separate test/project data from protected application data. Produce an ignored machine-readable report with actual command exit status and failure scope. |
| 2 | Resource-refusal and recovery evidence | Deterministic load/refusal, process cleanup, persistence-failure and interrupted-real-job tests; assert that event/job redelivery or manual retry cannot cause a second ambiguous real generation or duplicate proposal. Use non-model subprocesses and scripted providers. |
| 3 | Bounded operational visibility | Review existing `/api/v1/operations` queries and UI. If approved, add bounded pagination for task event/job history and safe request/job failure metadata using existing records. Keep raw provider bodies, prompts, source content, secrets and local paths out of operational responses. |
| 4 | Security qualification | Verify owner/task/device isolation, grant revocation, stale source/conflict checks, mutation authorization, idempotency and terminal-state behavior across proposed operational changes. Preserve owner checks and existing operation-specific RBAC. |
| 5 | Reproducible performance baseline | Measure fixture HTTP and event recovery under a predeclared sequential local workload, reporting hardware, concurrency, quotas, timing scope, sample count and failures. Keep browser pacing explicit. No model-speed, capacity, percentile or improvement claim without corresponding measurements. |

This proposal deliberately prioritizes measured R1 resource/refusal telemetry gaps,
R2's service-staging mitigation, historical harness/readiness/project-selection
errors, and replay traffic reaching the unchanged gateway quota. These observations
motivate investigation; they do not establish an unresolved production defect in
the checkpointed Phase 10 implementation.

## Proposed component requirements

**Backend:** reuse event/job/outbox/inbox and safe diagnostic contracts. Any
operational query extension must enforce task ownership before returning metadata,
bound page size and use stable ordering/cursors without exposing another owner's
records. No new execution, approval or model-activation endpoint. Mutation routes
retain validation, audit, transactional consistency and changed-intent refusal.
Do not rewrite completed Phase 10 behavior absent a demonstrated correctness or
security defect. Freeze existing behavior with focused regressions before changes.

**Frontend:** extend the existing operations surface only if its proposed metadata
work is approved. Provide accessible loading, empty, error and pagination states;
cancel/ignore stale task responses. Display measured metadata or UNKNOWN and safe
failure classifications. Do not show protected evidence in diagnostic panels or
add approval/execution controls for Phase 10 drafts.

**Database:** no new table or migration is presumed necessary. Start from existing
event/job/audit records and migration head `0011_inference_registry`. Justify any
index/schema change with query evidence, provide an Alembic migration, and test
upgrade/drift and isolated round-trip behavior. Never downgrade protected data.

**Events/workers:** preserve durable outbox/inbox deduplication, advisory worker
serialization, terminal-state guards, cancellation and at-most-one proposal per
draft. Recovery testing uses deterministic providers; an ambiguous real generation
must not automatically retry. Do not claim exactly-once external side effects.

**Authentication/privacy:** use existing local/OIDC identity/device bindings, RBAC,
task ownership and current-source checks. Operational metadata must remain scoped;
safe errors must not expose credentials/provider payloads. Keep privacy checks and
final acceptance transactional. No new principal, role expansion or identity
assumption is proposed.

**AI/ML:** retain existing abstractions, fixtures by default, pinned artifacts and
schemas. No prompt/schema change, new model or real generation is proposed. Synthetic
responses establish contract/policy behavior, not learned quality or injection
resistance. A later real-model experiment would require a separate exact proposal
and explicit approval; it is outside this proposed offline scope.

## Proposed acceptance matrix

Approve or revise these criteria before implementation; none is silently treated
as an existing mandatory Phase 11 requirement.

| Gate | Required evidence if this scope is approved |
| --- | --- |
| Scope freeze | Agreed feature list/exclusions, acceptance matrix and baseline source/fixture fingerprints recorded before work. |
| Qualification runner | Refuses unsafe project/data targeting and missing prerequisites; captures truthful stage results; stops task-owned services on interruption/resource refusal without deleting volumes or unrelated processes. Failure of a required stage cannot produce overall PASS. |
| Resource/recovery | Deterministic tests cover exact swap ceiling, resource changes during load, telemetry-write failure, cleanup failure, no second ambiguous generation, duplicate delivery and unique proposal persistence. |
| Operational API/UI, if approved | Bounded stable pagination; owner/foreign-owner/no-bearer cases; safe metadata-only errors; accessible loading/empty/error/stale-task handling; no new execution authority. |
| Backend/controller | Focused and full pytest, Ruff lint/format, installed-environment dependency checks, migration checks and host controller tests pass against isolated data with real/external model tests disabled. Record skips by purpose. |
| Frontend/Go | Configured lint/typecheck/production build, relevant browser journeys and existing Go race/vet pass using installed dependencies/toolchain only. State component coverage precisely. |
| Events/golden | Dedicated local Kafka duplicate/forgery/worker/broker-recovery tests and baseline FULL/SMOKE/REGRESSION pass with no unauthorized effects. Preserve expected negative-control failure and historical datasets. |
| Measurements | Predeclare fixture workload/concurrency and timing scopes; retain raw ignored samples and accurate failures. Establish a baseline first. No new numerical speed/quality target is assumed from the roadmap. |
| Cleanup/review | No model calls or external actions; credentials revoked, real config disabled, services/listeners stopped, protected data preserved; source/secret/artifact inventory reviewed. Keep all Phase 11 changes uncommitted. |

Any unavailable dependency, resource refusal or missing required evidence remains
an explicit incomplete gate. Do not lower criteria after observing a failure.

## Resource contract, exclusions and execution sequence

Use existing local images/packages/browsers/compiler only, with pull/download and
external model tests disabled. Development/external spend target $0. Keep existing
Docker allocation, per-service caps and sequential heavy suites. Real inference
remains prohibited under the current instruction; if separately authorized later,
retain swap <2048 MiB, disk >=5 GiB, existing model RSS/context/output/CPU/concurrency
and 30-second startup/eight-second inference limits, sandbox and scoped attestation.

Exclude cloud/paid APIs, downloads/installation, real-model quality or load tests,
external integrations/messages/actions, general-purpose semantic reasoning, vision,
LLM judging, Kubernetes/Terraform deployment, HA/security certification, host/swap
configuration changes and automatic host restart. Existing Phase 8 deployment
qualifications remain unchanged. No cache/volume deletion or unrelated process kill.

After scope approval: (1) freeze the agreed baseline and acceptance workload;
(2) implement the runner and focused failure tests; (3) implement only agreed
operational API/UI changes; (4) run focused then full sequential qualification;
(5) record actual implementation/test evidence, limitations, source manifest and
cleanup. Create Phase 11 implementation audit/test evidence/architecture decisions
from actual work, not prefilled PASS claims. No Phase 11 commit without separate
authorization.

## Work performed and stop state

Only this proposed specification was added after the Phase 10 checkpoint.
No Phase 11 application code, migration, endpoint or UI was implemented; no model,
draft, new fixture job, service or paid/external call was run. No Phase 11 functional
test result is claimed. Checkpoint verification and document review were read-only
apart from the authorized local commit and this document.

Fresh discovery snapshot: swap **684.06 MiB**, free disk **17,748,996 KiB**;
Docker reported zero running containers. This is a point-in-time observation, not
model activation approval or guaranteed allocatable RAM. Previous R2 cleanup and
closed attestations remain historical evidence; no private model configuration
was enabled or modified here.

**Next action: operator review/approval of an explicit Phase 11 scope**, either
this proposal or an authoritative specification supplied by the operator. Phase 10
checkpoint is complete. Phase 11 remains **NOT COMPLETE / SCOPE UNDEFINED**.
Stopped at the boundary expressly required by the current instruction.


## October 20 scope authorization

The operator subsequently instructed “complete phase 11,” approving this proposed
scope after its presentation. Title adopted: **Local reliability, security and
operational qualification**. Work packages and acceptance gates above are the
implementation baseline, including the operational API/UI extension. Earlier
undefined-scope/stop statements remain preparation history. Real inference remains
unapproved. Exact pre-implementation proposal and predeclared workload (ten
sequential fixture HTTP reads, one broker recovery task, zero browser retries)
were frozen under ignored `.local/phase11` evidence before implementation.
Current results and completion disposition belong in the Phase 11 audit/evidence.


## Final disposition

The approved scope completed offline qualification on October 20. See the final
Phase 11 audit/evidence for the complete entrypoint PASS, actual measurements,
retained failures and limitations. No additional real inference or Phase 11 commit
was authorized or performed. The separate local MVP release is fixture-default.
