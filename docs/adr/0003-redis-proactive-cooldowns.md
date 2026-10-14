# ADR 0003: Redis gates suggestions; PostgreSQL owns consequential state

Status: accepted for Phase 3.

Use local Redis atomic SET NX EX with a 300-second TTL for trigger cooldowns.
Keys contain user UUID and a hash of stable trigger/meeting/window inputs, with
no personal message text. Redis failure suppresses new suggestions and records
REDIS_UNAVAILABLE in PostgreSQL; existing approval and simulation operations
remain available. A durable PostgreSQL fingerprint check under a user row lock
prevents repeated surfaced suggestions after TTL expiry or Redis loss.

No distributed transaction is introduced. A claimed key followed by failed SQL
commit may suppress a valid suggestion for up to the TTL. This conservative
failure is preferred to spam. Retries of one evaluation key reproduce its
original outcome; a new event/key is needed to reevaluate suppressed context.
Redis never stores authoritative proposals, approvals, receipts, or audit.

Rejected alternatives: Redis as the approval store, unbounded cooldown keys,
and fail-open suggestion creation. All weaken durability or outage behavior.
See [Phase 3 architecture](../phase-3-architecture.md).
