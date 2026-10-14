# ADR 0002: application-owned approval and exact payload binding

Status: accepted for the local Phase 3 simulation.

Communication agents and kernel plugins can draft but have no approval or
execution capability. The server constructs proposals and deterministic policy;
communication always requires an explicit human decision. A separate immutable
ApprovalDecision binds proposal ID, server-owned user, canonical SHA-256 payload,
and validity. Execution rechecks all bindings and policy under a proposal row
lock immediately before pure simulation.

Editing creates a new proposal and supersedes the old one, preserving the old
approval as unusable history. Unique execution constraints prevent duplicate
simulation even with competing keys. PostgreSQL commits receipt, state, and audit
together. This is appropriate for a pure simulator, not a general guarantee of
exactly-once external communication. A future transport would require an outbox,
provider idempotency, authenticated identity, and a separate reviewed design.

Rejected alternative: provider-generated approval flags or mutable approved
payloads. They allow agent self-authorization or approval of a different action.
See [Phase 3 architecture](../phase-3-architecture.md).
