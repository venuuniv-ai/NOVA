# NOVA Phase 3 final audit

Date: October 14, 2026 (America/New_York).

**Disposition: PASS within the documented local deterministic simulation scope.
Remaining Phase 3 blockers: none identified.** Phase 4 was not begun.
No real message was sent. Phase 3 changes remain unstaged and uncommitted.

## Preserved checkpoints

- Phase 1: `d1d80d687171e992c963e92c797ec924ba815cb5`.
- Phase 2 / current HEAD: `1cecd1b276887241d5e46c77159f76f85cc14bd7`.
- Branch: main. Two existing commits; neither was amended. No remote or push.

## Implemented architecture

Next.js same-origin gateway → FastAPI application event service → deterministic
ProactiveTriggerEngine → Redis cooldown gate / durable PostgreSQL deduplication
→ CommunicationAgent → registered Semantic Kernel CommunicationPlugin and
FixtureModelProvider → server-owned ActionProposal → deterministic policy →
human ApprovalDecision → independent authorization service → pure simulated
adapter → PostgreSQL receipt and audit.

The original shared Task and handoff path remain authoritative. Phase 2's
five-agent workflow, contracts, kernel plugin invocation, and intelligence
persistence remain functional. The new draft-only CommunicationAgent is recorded
with its tools/output/provider/trace in the proactive trigger's bounded JSONB
agent_record. It does not fabricate a completed Phase 2 execution or attach
execution capability to a kernel plugin.

The public scenario explicitly uses a frozen FixtureClock at 13:31. Clock has
separate injectable SystemClock and FixtureClock implementations; no global
datetime patch is used. The engine computes 14:00 − 13:31 = 29 minutes,
35 − 29 = six minutes of risk, and 14:06 arrival. Arithmetic is application
code, never provider reasoning. Deterministic relevance rules cover preference,
confidence, urgency/window, threshold, duplicate status, and cooldown.

Each task owns a separate synthetic meeting instance; repeated events and
handoffs of that task preserve its meeting identity. No actual calendar,
travel estimate, attendee account, or personal location was read.

## Approval and execution invariants

ActionIntent rejects approval/status injection, malformed/extra fields,
unsupported action/channel, oversized content/recipient, and mismatched
context/task/trace. The provider proposes only; server code assigns ownership,
status, policy version, expiry, and canonical hash.

Policy always requires human approval for communication, including simulation.
SHA-256 binds sorted compact canonical UTF-8 JSON over action_type, recipient,
channel, content, and task_id. ApprovalDecision separately binds proposal ID,
server-owned user, hash, and bounded expiration. The UI cannot supply approval
objects, policy outcomes, user identity, status, clocks, or executor configuration.

Edit creates a new proposal, supersedes the old one, and requires fresh approval.
Old approval remains historical evidence and authorizes neither version after
supersession. Server clock checks reject expired proposals and approvals, including
at the exact boundary. Proposals last ten scenario minutes; approvals at most five
and never beyond the proposal.

Proposal row locks serialize approve/reject, edit/approve, and duplicate execution.
Immediately before simulation, the application independently checks approval
identity/ownership/decision, status, both expirations, canonical hash, current
policy/version, supersession, and prior execution. Unique proposal/approval
execution constraints enforce one logical receipt even with different keys.
Mutation keys bind operation and request payload; edits replay their original new
proposal. Historical execution retries return a receipt without simulating again.

SimulatedCommunicationAdapter computes a deterministic receipt; it has no
communication transport or network client. The receipt is labeled
DELIVERED_SIMULATION, SIMULATED / NOT SENT, external_message_sent=false.
Failures record a safe error and cannot produce repeat adapter calls.
Explicit tests block socket connections, synchronous/asynchronous HTTP,
requests, and urllib during the communication-agent/adapter path.
PostgreSQL and Redis network connections are local infrastructure outside that
pure communication path; the test does not claim the entire application is network-free.

## Redis behavior and persistence

Local Redis atomic SET NX EX, TTL 300 seconds, provides the first justified
Redis use. Keys contain user UUID plus a hash of stable meeting/window/trigger
inputs, not personal text. Redis unavailable means SUPPRESSED/REDIS_UNAVAILABLE,
with persisted context and audit and no proposal. Existing approvals/receipts
remain usable. A new event/key can reevaluate after recovery; original-key
retries reproduce their original suppression. The empty Approval Center offers
Evaluate new fixture event; unacknowledged event keys are preserved for retry.

A PostgreSQL user-row lock and durable surfaced-fingerprint check prevent
repeated proposals after Redis expiry or loss. Redis is not authoritative for
proposals, approvals, execution, or audit. A Redis claim followed by SQL failure
may conservatively suppress for one TTL; no distributed transaction is claimed.

## Database, API, and UI

Migration `0003_proactive_actions` adds seven UUID-linked tables:
context_events, proactive_triggers, action_proposals, approval_decisions,
action_executions, audit_events, and action_mutations. They have foreign keys,
status checks, bounded text, timestamptz, JSONB, indexes, and uniqueness for
context keys/traces, trigger events/traces, supersession, approval, execution,
and mutation keys. Upgrade/downgrade only ran against isolated test data;
application migrations were forward-only and application state was preserved.

| Method | API |
| --- | --- |
| POST | `/api/v1/proactive/evaluate` |
| GET | `/api/v1/tasks/{id}/proactive` |
| GET | `/api/v1/tasks/{id}/proposals` |
| GET | `/api/v1/proposals/{id}` |
| POST | `/api/v1/proposals/{id}/edit` |
| POST | `/api/v1/proposals/{id}/approve` |
| POST | `/api/v1/proposals/{id}/reject` |
| POST | `/api/v1/proposals/{id}/execute` |
| GET | `/api/v1/tasks/{id}/audit-events` |

Mutation requests require idempotency keys. Trace headers are returned for
successful evaluation and proposal mutations; audit links and existing JSON
logging carry trace/correlation IDs. Audit covers created/suppressed triggers,
proposal/edit, approval/rejection, expiry, execution/failure and refusal. Safe
metadata does not duplicate draft text or raw provider errors. Refusals preserve
their audit transaction even when the API responds 409.

Command Center receives a synthetic TIME_TICK and shows persisted proactive
risk without the user asking to diagnose lateness. `/approvals` shows the
situation, draft, recipient, policy, hash, trace, expiry, and lifecycle history.
Edit/Approve/Reject precede a separate Execute simulation control. Task Detail
embeds the same panel. No button claims real message sending. The UI displays
SIMULATED DELIVERY COMPLETE / NO EXTERNAL MESSAGE WAS SENT.

Task-keyed components cancel obsolete reads and ignore stale acknowledgments;
parent ownership gates mutations before task navigation completes. A synchronous
posting guard prevents duplicate clicks. Local storage contains request intent
only, including synthetic edit parameters, not authoritative approval state.
Held browser responses contain real API results, not invented task data.
Mobile 390px screenshot was generated and visually inspected; no overflow.

## Tests actually executed

43 additional backend cases (including parametrized variants) and seven new
browser tests were added. Earlier 55 backend and 12 browser cases were retained.
The final rebuilt production/test images passed these checks:

| Executed check | Final result |
| --- | --- |
| Full PostgreSQL-backed backend `pytest -q` | **98 passed**: 55 previous + 43 Phase 3 |
| Separate adversarial selection, after full validation | **26 passed**, 17 deselected |
| Backend `ruff check .` | Passed |
| Backend `ruff format --check .` | Passed; 37 Python files formatted |
| Backend `pip check` | No broken requirements |
| Frontend `npm run lint` | Passed |
| Frontend `npm run typecheck` | Passed |
| `NEXT_TELEMETRY_DISABLED=1 npm run build` | Passed |
| `npm audit --audit-level=high` | Zero reported vulnerabilities |
| Backend, backend-tests, frontend Docker image builds | Passed |
| Entire Chromium `npm run test:e2e` | **19 passed**: 12 previous + 7 Phase 3 |
| `docker compose config --quiet` | Passed |
| Isolated `alembic downgrade 0002_intelligence`, `upgrade head`, `check` | Passed; no schema drift |
| Application `alembic current` | `0003_proactive_actions (head)` |
| Application `alembic check` | No new upgrade operations |
| Phase 3 script `py_compile` | Passed |
| Phase 3 REST acceptance script | Passed |
| Phase 3 acceptance verification after backend/frontend restart | Passed |
| Original Phase 2 acceptance after restart | Passed |
| Original Phase 1 acceptance after restart | Passed |
| `git diff --check` | Passed |

Full backend validation used the rebuilt test image with the isolated ephemeral
PostgreSQL and test-redis services:

```sh
docker compose --profile test run --rm backend-tests sh -c \
  'alembic downgrade 0002_intelligence && alembic upgrade head && alembic check && pytest -q && ruff check . && ruff format --check . && pip check'
```

The separate adversarial rerun selected tampering, wrong approval binding,
provider self-approval, malformed intents, concurrency/races, expiry, replay-key
binding, no-network simulation, duplicate events, and Redis outage cases.
Playwright retries remain zero; final results did not depend on hidden retries.

## Acceptance evidence

Final REST task: `2efed4f2-1ecf-4e4f-8b56-eca91c910ec0`.
Proposal: `58f5b132-3d5b-4983-8fb9-ffeb01344da3`.
Trace: `d0f42e59-f979-4384-a0ec-19115831789a`.
Execution: `d6e1aa38-9499-4753-949a-d108627e48e9`.

Fixture arithmetic is 29 / 35 / +6. Draft arrival is 2:06 PM. The server created
PENDING_APPROVAL, recorded exact payload-bound approval, and created one
simulated execution. Duplicate evaluation, approval, different-key execution,
and historical handoff retries produced no duplicate actions/events.
Desktop → Wearable → Mobile preserved task/proposal/trace identity. Audit has
exactly four trace-correlated acceptance events.

After `docker compose restart backend frontend` and health verification,
`acceptance_phase3.py --verify-task` retained the same proposal, approval,
execution, receipt, trace, Mobile state, and four audits. Independent browser
acceptance refreshed at both device contexts, approved on Mobile, executed,
and refreshed the persisted NOT SENT result.

The original Phase 2 task `495411fd-b1ad-4890-90e3-0c679b7078e8` retained its
six runs, five tools, Critic PASS, plan, original trace, and Mobile state.
The original Phase 1 task `0251cb6e-c92c-4aee-acfa-9ecf7fd4a80e` retained Mobile
and TASK_CREATED / HANDOFF_DESKTOP_TO_WEARABLE / HANDOFF_WEARABLE_TO_MOBILE.

## Adversarial findings and resolutions

**P3-A01 — mutation key binding, CLOSED.** Review found successful new-key
replays of an already-recorded approval/execution returned before adding that
new key to ActionMutation. No duplicate execution or authorization bypass was
observed, but the new key could be reused for a different operation without
the expected key-conflict classification. Added ledger persistence to both
replay branches; the regression proves approval replay keys reject a subsequent
edit and execution replay keys reject a subsequent rejection. Full suites pass.

**P3-V01 — browser test synchronization, CLOSED.** The first suite passed 18/19;
the stale-acknowledgment test inspected B's API proposals immediately after its
component mounted, before its fixture evaluation completed. Added an explicit
wait for the loaded actionable state. The final 19-test suite passed. No fake
response or retry configuration was added.

Initial Python import/format checks and React ref-render lint were corrected
before final validation. A manual original-Phase-1 probe initially used an
incorrect assumed Mobile UUID; it was corrected to resolve device identity
from the API and passed. These were validation/implementation corrections,
not concealed remaining failures.

| Adversarial scenario | Verified result |
| --- | --- |
| Forged APPROVED/status/approval fields | Strict API/intent validation rejects extras |
| Execute without approval | 409, refusal audit, no execution |
| Changed message/recipient/channel after approval | Independent hash/policy checks refuse |
| Wrong approval user/hash/proposal | Refused; no adapter execution |
| Expired proposal/approval, exact boundary, concurrent execute | Refused and expiry audited |
| Old approval after edit | Old proposal superseded; new proposal remains unapproved |
| Duplicate execution, different keys, eight racing callers | One execution/receipt |
| Concurrent approve/reject | One decision wins; competing decision returns 409 |
| Concurrent edit/approve | New version pending; old approval cannot execute it |
| Provider returns approval=true | Invalid intent; failed trigger, no proposal/execution |
| Communication agent invokes execute/another plugin | Kernel capability rejection; no executor supplied |
| Duplicate context events and Redis races/expiry | One surfaced proposal; cooldown/durable suppression |
| Redis unavailable | Persisted suppression, no proposal |
| Stale task reads/approval acknowledgment and handoff | Current selection retained; original intent retries safely |
| Malformed/oversized/unexpected action/channel | Typed rejection |
| External HTTP/socket attempt during simulated communication | Explicit no-network tests pass |
| Simulator failure | Safe persisted failure; no repeat adapter call |

The separate review inspected authorization checks, immutable approval binding,
transaction/lock boundaries, replay handling, Redis/SQL consistency, capability
allowlists, simulation implementation, and task-selection guards. No remaining
blocking finding was identified within this scope.

## Cost and security limits

Required paid API/infrastructure spend: **$0**. No paid inference, cloud resource,
managed Redis/database, model download, real communication API, or personal
account connection was used. New redis-py is a free local Redis client.
Existing mandatory Semantic Kernel commercial/telemetry SDK dependencies remain
unconfigured. No real message is sent even after approval.

This is an unauthenticated single-user, loopback-bound local demo. Approval means
an explicit local UI/API decision, not an authenticated human identity. Agents
have application capability boundaries, not an OS sandbox. The fixture clock
is frozen and expiration is lazy; demo validity does not age in wall time.
Tests explicitly advance the injected clock. No autonomous background calendar
monitor, real travel context, live LLM, durable distributed worker, push updates,
external outbox, or production exactly-once delivery is implemented.

The simulator's atomic SQL/receipt guarantee depends on pure computation;
future external actions require a separately reviewed architecture. Audit is
persistent but not tamper-proof. Optional localStorage request intent can contain
synthetic draft text. Python advisory/container vulnerability scans and a
penetration test were not performed. npm audit/pip checks are not security
certification. The non-failing Playwright environment-color warning remains.

## Files and Git

34 Phase 3 files: 13 tracked modifications and 21 additions. The manifest follows.
Dependencies, bytecode, builds, screenshots, traces, caches, and database data
remain excluded. Candidate files were inspected for secret patterns, generated
artifacts, and unexpected size; none was detected. `.env.example` only adds the
local Redis URL; no actual environment file or credential was added.

```text
.env.example
README.md
backend/app/config.py
backend/app/intelligence/provider.py
backend/app/main.py
backend/app/proactive/__init__.py
backend/app/proactive/api.py
backend/app/proactive/clock.py
backend/app/proactive/communication.py
backend/app/proactive/contracts.py
backend/app/proactive/models.py
backend/app/proactive/policy.py
backend/app/proactive/service.py
backend/app/proactive/trigger.py
backend/migrations/env.py
backend/migrations/versions/0003_proactive_actions_proactive_actions.py
backend/requirements.lock.txt
backend/requirements.txt
backend/tests/conftest.py
backend/tests/test_proactive.py
compose.yaml
docs/adr/0002-human-approval-boundary.md
docs/adr/0003-redis-proactive-cooldowns.md
docs/architecture.md
docs/phase-3-architecture.md
docs/phase-3-final-audit.md
frontend/app/approvals/page.tsx
frontend/app/globals.css
frontend/components/approval-workspace.tsx
frontend/components/nova-workspace.tsx
frontend/lib/proactive.ts
frontend/styles/approvals.css
frontend/tests/proactive.spec.ts
scripts/acceptance_phase3.py
```

Git HEAD remains `1cecd1b276887241d5e46c77159f76f85cc14bd7`, branch main.
The index is empty. Changes are unstaged/untracked for review; no Phase 3
commit, checkpoint amendment, push, or remote configuration occurred.

## Local operation and final disposition

```sh
docker compose up --build -d --wait
python3 scripts/acceptance_phase3.py
# After a backend/frontend restart, verify the printed task:
python3 scripts/acceptance_phase3.py --verify-task TASK_ID
```

Open `http://localhost:3000`; select a task in Command Center, then Review
proposal or Approval Center. API docs: `http://localhost:8000/docs`.
Local validation containers were stopped after checks; persistent application
volumes and acceptance/regression tasks were preserved. No database volume
was deleted. Test databases were isolated from application data.

**Final result: Phase 3 accepted for the documented deterministic local
simulation. Remaining Phase 3 blockers: none identified. Phase 4 not started.**
