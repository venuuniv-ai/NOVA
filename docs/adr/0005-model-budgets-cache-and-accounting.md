# ADR 0005: durable budget exposure and scoped transient model cache

Status: accepted for Phase 4; priced behavior is tested with deterministic providers.

Use typed manual prices and Decimal USD arithmetic. Reserve declared input-context
and capped output exposure in PostgreSQL before a priced call. Lock daily rows
in UTC, enforce the aggregate request cap across fallback attempts, and settle
reported usage to a configured estimate. Unknown outcomes retain conservative
exposure because timeout does not prove zero billing. Startup recovery preserves
that exposure. Redis never owns financial accounting.

ModelCall is one authoritative logical-request ledger, including decisions,
attempts, normalized errors, token provenance and accounting. Do not retain raw
prompts or generated output there. Original UUID retries read metadata without
another invocation. Advisory locks suppress duplicate requests/cache stampedes.

Use bounded user/task/model/policy/settings-scoped exact-result caching in local
Redis. Sensitive-local-only bypasses it. HMAC authenticates cache content and
key scope; per-process key rotation forces recomputation after restart. Cache
loss/error cannot lose application state. Signing does not encrypt personal
output; the trusted local Redis boundary and TTL are explicit limitations.

Token absence stays UNKNOWN. Fixture has $0 API spend; local has $0 external API
spend with compute/electricity unpriced. Cache hits incur no fresh API call.
Synthetic priced/failure probes are POLICY_REPLAY and never benchmarks. No real
commercial rate or optional cloud client is assumed by default.

Rejected alternatives: provider-reported prices, per-attempt-only request caps,
Redis financial ledgers, unauthenticated cross-user cache keys, and prompt logs.
See [Phase 4 architecture](../phase-4-architecture.md).
