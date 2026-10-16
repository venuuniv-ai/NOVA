# NOVA Phase 8 implementation reference

Approved scope supplied in conversation on October 15, 2026. Baseline is clean
main at 6fb2e803c9c2a1422bfdc45d2352efdbd2b84872. This file records the supplied
requirements; implementation and executed evidence belong in the final audit.

Implement sequentially:

1. Security: OIDC authentication, server-owned authorization and resource ownership,
   device registration/revocation. FastAPI independently verifies identity and policy.
2. Go gateway: bounded routing, validated identity, trusted propagation, rate limits,
   request sizes and timeouts. Gateway identity is never sufficient by itself.
3. PostgreSQL transactional outbox, Kafka publisher and idempotent consumers with
   retries, dead-letter handling and operator recovery. Kafka is at least once.
4. OpenTelemetry distributed traces, Prometheus metrics, Grafana and structured logs.
5. Hardened Docker, local Kubernetes, Terraform and deterministic CI/CD gates.
6. Actual load/outage/recovery/security checks and operational runbooks.
7. Retain/rerun 470 prior backend tests, 48 prior browser tests, and the unchanged
   104-case golden dataset. Report measurements, failures and limitations honestly.

Invariants:

- Business changes and outbox events commit in the same PostgreSQL transaction.
  Broker publication happens afterward, with no exactly-once delivery claim.
- Inbox claims and consumer effects commit together. Retries preserve task UUIDs
  and prevent duplicate business effects.
- FastAPI owns payload-bound human approval. Events, workers and model outputs
  cannot confer execution rights. All execution remains SIMULATED / NOT SENT.
- Preserve existing task/memory records, approval hashes and fixture behavior.
- Required external infrastructure/API spend is $0. No paid service, cloud resource
  or automatic model download is authorized.
- REAL EMBEDDING MODEL NOT CONFIGURED; fixture embeddings are not a real semantic
  model. Real CLIP/DINOv2/SAM/VLM inference remains unconfigured/unexercised.
  REAL LLM JUDGE NOT CONFIGURED. Existing fixture metrics retain their scope.
- Preserve every Phase 1–7 checkpoint. No commit, amendment, push, remote setup or
  Phase 9 work. Leave changes unstaged/untracked for review.

If a dependency cannot run, record the specific blocker and continue independently
verifiable work. Never label unexecuted checks PASS. Finish with
`docs/phase-8-final-audit.md`, implementation evidence, actual validation and
reliability measurements, unresolved limitations/blockers and Git status.
