# Phase 3: proactive intelligence and human action control

Phase 3 extends the verified Phase 1 and Phase 2 checkpoints. It runs locally
with PostgreSQL, Redis, FastAPI, Next.js, and the existing Semantic Kernel
fixture runtime. No model inference, cloud infrastructure, account connection,
or communication service is configured.

## Event and temporal boundary

`ProactiveService` is the application event/orchestration service; API routes
validate requests and delegate. Typed TIME_TICK, CALENDAR_CHANGED,
DEVICE_CHANGED, and TASK_UPDATED inputs produce persistent ContextEvent rows.
The public evaluator accepts only the MEETING_TRAVEL_RISK fixture scenario;
it does not accept client-generated meeting evidence, user identity, time,
policy decisions, status, approval, or execution configuration.

`Clock` has SystemClock and explicitly injectable FixtureClock implementations.
The public demonstration deliberately uses FixtureClock at
2026-10-14 13:31 UTC as a **synthetic scenario time**, not a claim about the
user's local time. Architecture Review starts at 14:00, at Client Office;
synthetic travel from Demo home requires 35 minutes. Application arithmetic
computes 29 minutes available, six minutes of risk, and arrival at 14:06.
The provider never performs temporal arithmetic.

Each task gets its own synthetic meeting instance (`demo-architecture-review`
plus task UUID). This makes separate local demonstrations reproducible without
resetting Redis or deleting previously audited proposals. Events for the same
task retain that meeting identity across all device handoffs. No real travel,
traffic, calendar, location, or attendee data is used.

`ProactiveTriggerEngine` applies deterministic rules: proactive preference must
be enabled, confidence at least 0.8, meeting ahead within 60 minutes, and
lateness strictly above two minutes. Suppression has an explicit reason.
There is no learned utility score. Fingerprints hash user identity, stable
meeting identity, meeting start/window, and trigger type; no personal text is
placed in Redis keys.

## Redis and PostgreSQL consistency

Redis uses atomic `SET key 1 NX EX 300` for deduplication and a bounded cooldown.
See the [Redis SET contract](https://redis.io/docs/latest/commands/set/).
Redis failure suppresses new suggestions as REDIS_UNAVAILABLE and persists the
context, trigger, and suppression audit in PostgreSQL. Existing proposals,
approvals, receipts, handoffs, and their APIs remain usable without Redis.
No fallback loop surfaces messages during an outage.

The application serializes evaluations with the demo user's PostgreSQL row
lock. An already SURFACED fingerprint in PostgreSQL is never surfaced again,
even after Redis expiration or data loss. Redis is a short-lived gate, not an
authoritative action store. Evaluation keys are unique per task and bind the
event input; historical retries return the original trigger. A replay of a
suppressed event remains suppressed. A new event/key is necessary after an
outage or cooldown; refresh alone does not turn a previous denial into success. The empty Approval
Center exposes Evaluate new fixture event for explicit recovery; it preserves
an unacknowledged event key for retry.

There is no distributed transaction with Redis. If Redis claims a key and the
PostgreSQL transaction then fails, that key can suppress subsequent evaluations
for at most its TTL. This favors missed suggestions over duplicate spam. A
crash cannot leave an approved or executed action without a database commit.

## Communication capability boundary

CommunicationAgent receives only a typed situation and a bounded KernelRuntime.
It invokes the registered native CommunicationPlugin.resolve_demo_attendee via
real Kernel.invoke, KernelArguments, and trace metadata. Its allowlist contains
only that synthetic attendee capability. The plugin cannot send, access accounts,
invoke the action executor, or expand its own allowlist. Other agents cannot
use this plugin. The deterministic FixtureModelProvider implements a separate
communication capability on the existing provider abstraction.

The untrusted provider envelope must validate as CommunicationOutput/ActionIntent.
Extra approval/status fields, unsupported channels/actions, oversized text,
wrong task/trace/evidence, and mismatched synthetic recipient fail validation.
The server creates the proposal, assigns ownership and status, computes policy
and hash, and controls expiration. Communication execution records and kernel
tool evidence are persisted under `ProactiveTrigger.agent_record` as bounded
JSONB, correlated by trace. Phase 2 agent execution tables and their five-agent
workflow remain unchanged; the new draft-only stage belongs to the proactive
trigger pipeline, not a fabricated Phase 2 intelligence execution.

Semantic Kernel registers, discovers, and invokes capabilities; it does not
own approval, authorize actions, or execute external communication.

## Canonical payload and policy

The security-relevant canonical object consists of action_type, recipient,
channel, content, and task_id. UTF-8 JSON uses sorted keys, compact separators,
and explicit Unicode handling. SHA-256 binds the exact server-owned payload.
A proposal ID and server-owned user identity are bound separately by its
ApprovalDecision. No normalized or edited message is substituted after approval.

Policy version `communication-v1` validates the typed canonical action and
always returns REQUIRE_APPROVAL for communication, including simulation.
Unsupported payloads return DENY. ALLOW_WITHOUT_APPROVAL is a conceptual policy
outcome with no Phase 3 communication path. No provider field influences it.

## Proposal and approval lifecycle

The server creates PROPOSED, evaluates policy, and persists PENDING_APPROVAL
(or REJECTED for denial) in the same transaction. Approve and reject are
explicit user mutations. ApprovalDecision is separate, unique per proposal,
and binds proposal, user, exact payload hash, and expiration. Approval is never
inferred from clicking another button, fixture content, model output, or UI state.

Editing a pending or approved proposal creates a new UUID/hash, links
supersedes_id, marks the old proposal SUPERSEDED, and requires a new approval.
The old decision remains as immutable audit evidence but cannot execute either
the old superseded proposal or the new one. Executed, failed, rejected, and
expired proposals cannot be edited. No real message is sent in any lifecycle state.

Proposals live for ten scenario minutes; approvals live at most five scenario
minutes and never beyond proposal expiration. Reads and mutations lazily persist
EXPIRED and ACTION_EXPIRED using the injected clock. There is no wall-clock
expiry sweeper. The public fixture clock is frozen, so demo records do not age
with real elapsed time. Tests advance the injected clock and prove server
rejection at the exact expiration boundary. A future real context mode must
explicitly select SystemClock; it is not presented as implemented integration.

## Execution and concurrency

The application locks the proposal row before all lifecycle mutations. Immediately
before invoking the adapter it independently checks APPROVED status, proposal
and approval ownership/identity, approval decision, both expirations, recomputed
hash equality, current policy version and decision, and absence of supersession
or a prior execution. It never trusts an approval object supplied by the client.

ActionExecutor receives only the authorized canonical payload. Its sole adapter
is SimulatedCommunicationAdapter: pure deterministic receipt computation, with
no HTTP client, account, network transport, or real send. The receipt identifies
DELIVERED_SIMULATION and SIMULATED / NOT SENT with external_message_sent=false.
Approval and simulation are separate explicit user steps.

One unique execution per proposal and one per approval provide database-level
idempotency. Different request keys replay the existing execution rather than
call the adapter twice. Original-key replay after expiry is a historical receipt
read, not renewed permission. Simulator failure records FAILED, a safe error,
and an audit, and never invokes the adapter again for that proposal.

Mutations bind keys to operation and request hashes in ActionMutation; edits
also record their resulting new proposal UUID. Conflicting key reuse returns
409. Proposal locks serialize approve/reject, edit/approve, and duplicate execute
races. Approval rows are server-owned and immutable through the API. Handoffs
change only the shared task's device; proposal identity, trace, and approval
remain intact. Simulation is pure, synchronous computation inside the database
transaction; these guarantees do not extend to future external side effects.

## Persistent audit and schema

Migration `0003_proactive_actions` adds ContextEvent, ProactiveTrigger,
ActionProposal, ApprovalDecision, ActionExecution, AuditEvent, and ActionMutation.
They use UUIDs, foreign keys, bounded strings, timestamptz, JSONB, indexes,
status checks, and unique event/decision/execution/key/supersession constraints.

Audit events include trigger creation/suppression, proposals/edits, granted or
rejected approval, execution success/failure, and expiry. Audit contains trace,
task/user/proposal links, timestamps, correlation IDs, reason codes and hashes;
no draft text or secret is duplicated into audit metadata. Refused mutations
preserve their refusal audit even though the API returns 409. Readiness requires
the new schema; Redis is not required for reading or authorizing persisted actions.

## API and UI

| Method | Route | Result |
| --- | --- | --- |
| POST | /api/v1/proactive/evaluate | Typed fixture event and persisted evaluation; key required |
| GET | /api/v1/tasks/{id}/proactive | Persisted triggers, situation and communication record |
| GET | /api/v1/tasks/{id}/proposals | Proposals, including lifecycle history |
| GET | /api/v1/proposals/{id} | Proposal, approval and execution receipt |
| POST | /api/v1/proposals/{id}/edit | New pending proposal; content/recipient/key required |
| POST | /api/v1/proposals/{id}/approve | Exact approval; key required |
| POST | /api/v1/proposals/{id}/reject | Rejection; key required |
| POST | /api/v1/proposals/{id}/execute | Independently authorized simulation; key required |
| GET | /api/v1/tasks/{id}/audit-events | Persistent trace-correlated audit |

Command Center receives a synthetic TIME_TICK on loading a task and surfaces
backend risk/proposal state without asking the user to diagnose lateness.
Approval Center at `/approvals?task=UUID` shows the situation, recipient, draft,
policy, hash, trace, lifecycle, edit/approve/reject, and Execute simulation only
after approval. Task Detail embeds the same panel. Superseded cards remain
visible for review. No control is labeled Send message.

Keyed task components abort obsolete reads and ignore unmounted responses.
Parent selection ownership gates mutations before navigation finishes. A
synchronous posting guard prevents duplicate clicks. Request intent (key and
edit parameters) may survive in localStorage for original-key retry; authoritative
approval/proposal/receipt state always comes from the API. This optional browser
storage contains synthetic draft text and should be cleared before any future
real personal-data deployment. Pending HTTP acknowledgment does not imply
approval or delivery. Errors and unacknowledged requests remain explicit.

## Limitations

Single unauthenticated demo user; local loopback ports; no OS agent sandbox,
real personal context, autonomous scheduler, travel API, push events, or message
transport. Event delivery is application-level/visible-page fixture loading;
it does not monitor a calendar in the background. Proactive state polls every
five seconds, and task/event/proposal reads are separate read snapshots.
Historical audit is durable but not a cryptographically tamper-proof ledger.
Lists have no UI pagination. No hosted CI, deployment, telemetry stack, or real
LLM is added. Local dependencies and container pulls require internet; operation
requires no paid API or service. Phase 4 is outside this change.
