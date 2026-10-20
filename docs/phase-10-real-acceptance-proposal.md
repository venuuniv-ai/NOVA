# Phase 10 bounded real draft acceptance — NOT APPROVED / NOT EXECUTED

Prepared October 19, 2026. Current authorization is implementation and offline/local
fixture qualification only. Earlier Phase 9 model approvals are closed.

## Requested future scope

Authorize **one authenticated owner application draft request and at most one
Qwen generation**, zero BGE requests, zero retries and zero external actions.
Use the existing isolated Phase 10 application data and a single controlled owned
ACTIVE memory, not the protected Phase 9 database or its vectors.

Reuse the controlled memory prepared without generation on October 19: subject
`phase10_acceptance_fixture`, predicate `preferred_cuisine`, value `noodles`.
These dedicated fixture records are not protected Phase 9 user data. Query exactly:
`Which cuisine does phase10_acceptance_fixture prefer?`

POST the existing `/api/v1/proactive/drafts` exactly once with this frozen body:

```json
{
  "task_id": "9b363f16-1c38-46ff-a190-b674b7b28ed8",
  "query": "Which cuisine does phase10_acceptance_fixture prefer?",
  "memory_ids": ["7d1049cb-06b9-49c4-ad06-a8db5036480a"],
  "idempotency_key": "15d88b00-b223-429e-88cd-c1a6b160daf2",
  "expires_in_seconds": 600
}
```

Owner: `00000000-0000-4000-8000-000000000001`, through the existing dedicated local
identity and enabled device grant. Source binding SHA-256:
`8dbd48c85725bf97c29be220182aa1ae8ff52a2f32165bd745b1dfcd691de827`.
Exact original quote: `phase10_acceptance_fixture preferred_cuisine: noodles`.
No draft request was submitted during preparation; no real job is queued.

Enable only private scoped
`OWNED_DRAFT_MODE=LOCAL_REAL` in the API and draft worker, using existing
`nova-qwen-phase9-rag96`, managed residency, SELECTION_V1 and
`grounded_budget_profile=QWEN2_CHATML_0351`. BGE remains disabled/stopped. No alias,
model or dependency installation; no broader planner/critic inference.

Current selection prompt-at-96 SHA-256:
`7529089aa6ff8c7700b7c497ac04021c5af7d5b02849efd2d467b6f2922127b2`.
GroundedSelection schema SHA-256 (sorted compact JSON):
`abe361e90105db233c7727baf491643f167b626942be49232da2a6eb84b4da92`.
Conservative offline bound including the full output allowance: **469/512**,
not a measured runtime count or timing promise. Production source fingerprints
are retained in ignored `.local/phase10/source-review.json`; freeze the exact
private scoped overlay before startup. Refuse drift rather than alter the proposal
during execution. Verify no other real job is pending/running before enabling the
single request. Do not regenerate controlled records or silently change IDs.

## Preconditions and limits

Fresh disk >=5 GiB, swap <2048 MiB; no resident/unowned models/listeners; fresh
private scoped attestation; approved Qwen tensor SHA-256
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4` and existing
alias/template/blob integrity. Verify local JWT owner/device and controller bearer
authentication, read-only artifact mounts, loopback-only model sandbox and worker
reachability before activation. Preserve context 512, output <=96, threads 2,
GPU layers 0, temperature 0, concurrency 1, Qwen sampled RSS <=2048 MiB,
startup 30s/inference 8s and existing leases/watchdog/zero-queue controls.

Do not issue a warmup or diagnostic generation. The sole worker request must use
the reviewed current selection prompt/schema and budget. An ambiguous interrupted
real RUNNING job fails without re-generation. Metadata/status polling is permitted;
additional application/model requests are not. No automatic inference retry.

## Predeclared results and stop

PASS requires a model-generated supported value/index, independently verified
original UUID/full quote, successful current identity/device/source/conflict checks,
one proposal and completed job committed atomically, PENDING_APPROVAL, approval
required and execution disabled. No ApprovalDecision approving it or ActionExecution
may exist. A valid abstention is a failed positive case; invalid output, timeout,
resource/auth/citation/privacy failure is a failed case, not a repaired result.

Stop after that single case on every outcome. Record actual request/event/job/
proposal IDs, model identity, reported usage or UNKNOWN, latency scopes, sampled
RSS, resources and source verification. Unload Qwen and verify process/descendant/
listener disappearance; stop task-owned services, clear real mode/config approval,
close attestation and preserve data/artifacts/aliases/volumes. No external message,
cloud/API spend, download, limit increase, Git checkpoint or Phase 11.

This case would qualify only the bounded Phase 10 recommendation contract, not
general planning, semantic entailment, autonomous action or production readiness.
**Fresh explicit approval is required; this document activates nothing.**
