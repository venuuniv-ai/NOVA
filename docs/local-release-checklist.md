# NOVA v1.0 local release checklist and feature freeze

Deadline: October 21, 2026, America/New_York. Scope frozen October 20.
**READY: every P0 gate passed on October 20.** Actual results and limitations are
in local-release-test-evidence.md; the decision applies only to its defined scope. New feature development is frozen except
for demonstrated P0 release blockers. Phase 10 is already checkpointed; do not
create a duplicate checkpoint. Phase 11/release changes remain uncommitted.

## P0 — required for the defined local MVP

- Verify Phase 10 commit `80dc41af8d3742fdb700b02e342f579e06389fcf`, exact 24-file
  inventory and preserved Phase 1–9 ancestry; no secrets or remote operation.
- Review Phase 11 operational API/UI changes and preserve all existing model,
  ownership, privacy, conflict, idempotency and draft-only authority boundaries.
- Deterministic backend/controller/security regression and current frontend
  lint/typecheck/build pass; preserve exact earlier qualification scope/skips.
- Existing real BGE/Qwen/RAG/draft evidence retained without further generations.
  Default release AI remains explicitly FIXTURE; no learned-model quality claim.
- One documented command starts the dedicated persistent local stack using existing
  images/dependencies, local authentication, owner/device authorization, native
  frontend and durable queue. Missing/competing prerequisites fail closed.
- Correct private token issuance, authenticated device enrollment, credential
  rotation/revocation, no secrets in logs/source/candidate archive.
- Health checks and resource monitoring preserve strict swap <2048 MiB, disk >=5 GiB,
  Docker 4,106,604,544 bytes and existing service/model limits. No models loaded.
- Fresh authenticated end-to-end smoke: task/memory, exact UUID/quote fixture RAG,
  one durable draft/proposal, HITL pending/rejection/refusal, device continuity and
  real-service browser auth/operations journeys. No unauthorized execution/message.
- Stop/recover preserves task/memory identities and private data, revokes credentials,
  restores healthy services with fresh credentials, and terminates owned processes.
- Installation/usage/health/shutdown/recovery guide, known limits, source archive/
  fingerprints, rollback procedure, actual test evidence and final cleanup review.

## P1 — useful, explicitly deferred

- Default live learned-model activation: requires fresh bounded approval, artifact/
  runtime/resource preflight and separate acceptance. Historical real acceptance
  does not grant future loading authority. Existing implementations remain intact.
- Fresh semantic relevance/quality matrices, no-answer calibration, real-vector crash
  experiments, streaming, sustained load and general proactive agent reasoning.
- Optional local OIDC in the user release stack (already separately qualified);
  default release uses local JWT login to reduce continuously resident services.
- Additional qualification/capacity work beyond the measured Phase 11 scope. The
  complete current entrypoint passed; intermediate failures remain disclosed.
- An installer for a clean machine, new image builds, dependency/advisory upgrades,
  comprehensive secret/security scanning and unattended OS-level supervision.

## P2 — future work

Real vision/LLM judges, hardware integrations, external messaging/actions, cloud or
paid providers, production/HA capacity, Kubernetes/NetworkPolicy rollout, Terraform
apply/public hosting and new roadmap features. Each requires its own scope and
appropriate approvals. Existing Phase 8 deployment caveats remain unchanged.

## Release decision

READY requires every P0 gate above, within the explicitly fixture-default local
scope. Any unresolved P0 defect is BLOCKED with its exact next action. Do not call
this a production deployment or a currently running learned AI assistant. Do not
silently promote a P1/P2 item to PASS, claim unrun tests, or drop a failed gate.


## Completed decision

All P0 rows above are satisfied by actual lifecycle, regression, archive and
cleanup evidence. Current services are intentionally stopped after validation.
READY describes the prepared-host source candidate, not a running learned-model
service. P1/P2 remain deferred and do not authorize model loading or public deployment.
