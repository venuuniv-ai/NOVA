# ADR 0008: controlled memory lifecycle and immutable provenance

Accepted for Phase 6 local demonstration.

Memory is a policy-managed record, not raw history. Explicit safe user statements
may store; inferred/visual/task-outcome candidates require human confirmation.
Origin survives confirmation. Rejected unsafe content is tombstoned, not embedded.
No hidden visual profiling or automatic permanent memory.

Use USER/TASK scope, temporal bounds, active-only reads, canonical deduplication,
new records for corrections and predecessor links. Preserve supersession/deletion/
expiration audit. Owned mutation keys and user/record locks serialize conflicts
and lifecycle races. Soft deletion preserves historical audit; it is not erasure.
Seed old preferences as FIXTURE, never USER_EXPLICIT, and never resurrect them.

Read-only kernel tools retrieve bounded MemoryHit data. Memory cannot authorize
an action or change Phase 3 policy. Reject arbitrary client-owned authority fields.
See [architecture](../phase-6-architecture.md).
