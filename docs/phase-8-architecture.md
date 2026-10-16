# Phase 8: local security, event delivery and operations

Implementation reference: [approved scope](phase-8-implementation-spec.md).
Operational commands: [runbook](phase-8-runbook.md). Actual executed evidence and
limits: [final audit](phase-8-final-audit.md).

## Identity and ownership

The base Compose stack remains an explicitly unauthenticated local replay profile
for existing fixture checks. compose.phase8.yaml defaults to authenticated local
JWTs with a generated private signing key in a named volume. compose.oidc.yaml
adds a real local Keycloak authorization-code/S256 PKCE path; it is an optional
local infrastructure profile, not a commercial identity dependency. No paid
service or model is required.

FastAPI verifies signatures, fixed algorithms, issuer/audience, time bounds,
server-managed subject grants, roles and signed device ownership. OIDC uses a
bounded local JWKS fetch/cache or an operator-supplied public snapshot. Token
headers cannot select a URL/key/file/algorithm. Roles asserted in a JWT/header do
not replace local grants. Device registration/revocation preserves the existing
simulated Desktop/Wearable/Mobile UUIDs and task history. It does not attest real
hardware. Local credential epochs and disabled registrations are checked on every
request. OIDC device attributes are admin-managed; disabled devices are refused.

A request Principal ContextVar supplies owner queries across tasks, memory,
intelligence, routing, perception, proposals and evaluations. Internal fixture
seeds retain their explicit demo owner. Evaluation contexts deliberately reset
identity inside disposable schemas while public run records retain the requesting
owner. Owned background execution captures the same server identity. No client
user_id/header can choose the task owner. A viewer cannot mutate; evaluation and
operations require operator; approval/execution additionally require approver.
The draft worker has owner-only capabilities and cannot approve/execute even
through a direct service call.

Browser token sessions use an HttpOnly SameSite cookie, short lifetime and Origin
checks. PKCE uses a separate five-minute state/verifier cookie, a fixed callback,
server exchange and independent FastAPI access-token verification. Tokens are not
stored in localStorage, logs, metrics, reports or source. This is a localhost HTTP
lab; production TLS, full identity lifecycle and hardware attestation are outside
its verified boundary.

## Gateway and network boundaries

Next.js forwards the original bearer (or its HttpOnly session) through the Go
reverse proxy. The Go gateway delegates identity verification to FastAPI's /auth/me,
strips asserted user/role/device headers, then forwards the original signed bearer.
FastAPI independently verifies it again and applies ownership/policy. The gateway
is not an alternative authorization authority or an arbitrary-host proxy.

Go enforces allowed paths/methods, bounded headers/body, correlation ID format,
identity/IP rate buckets, upstream/read/write/request timeouts and no redirects
for identity checks. Rate buckets are bounded and process-local, not distributed
Redis quotas. Client cancellation does not guarantee a domain transaction did not
commit; handoff/action keys retain their existing replay semantics.

The full overlay separates edge, application, state, telemetry and identity
networks. Internal bridges keep clients off storage/event networks. Dedicated
host-facing diagnostic bridges permit intended loopback-published ports, without
claiming a universal outbound firewall. Base replay topology is unchanged.
Kubernetes declares default-deny plus explicit edges, restricted/non-root pods
and disabled service-account token mounts. Actual policy enforcement requires a
suitable CNI and is not implied by a rendered manifest.

## Atomic outbox and at-least-once delivery

SQLAlchemy mapper hooks write supported lifecycle records on the same DB
connection and transaction as the business row, after its FK exists. Supported
entities are Task, TaskEvent, AgentExecution, ActionProposal, ApprovalDecision,
ActionExecution, MemoryRecord and PerceptionRun. Outbox snapshots contain bounded
resource/task/user UUIDs, type/status, transition and W3C trace metadata, not memory
content, prompts, media or approval authority. Bulk/uninstrumented SQL is not a
general change-data-capture guarantee. Temporary golden-evaluation writes do not
emit public integration traffic.

A publisher locks pending rows with SKIP LOCKED, respects unpublished/dead
predecessors per task, publishes using the task UUID as partition key, awaits
Kafka acknowledgment, then marks PUBLISHED. Failures use bounded exponential
backoff and DEAD state after eight attempts. Crash-after-ack can publish the same
event again. No exactly-once broker delivery is claimed.

Projection, proactive and audit groups disable automatic offset commit. They
validate the bounded envelope against the committed authoritative outbox row.
An inbox unique on consumer/event and projection/job effects commit together.
Only then does the consumer commit its Kafka offset. Redelivery becomes DUPLICATE.
Projection sequence guards prevent an older event overwriting a newer view.
Poison/untrusted messages become durable fingerprint/reason dead letters without
retaining raw content. Unexpected database failure leaves the offset uncommitted.

Proactive delivery creates a single job only for an owned, explicitly subscribed
Desktop→Wearable event. The job calls the existing fixture draft service with the
original event-derived key. Advisory locking plus domain idempotency protects
crash-after-domain-commit replay. Job failures back off and become DEAD after five
attempts. A retry changes delivery state only, never payload, owner, task UUID,
approval hash or authority. Normal proposal approval/simulation remains solely
inside FastAPI's existing canonical payload policy. Execution is SIMULATED / NOT
SENT. Kafka/model outputs cannot authorize an action.

## Observability, deployment and evaluation

Actual HTTP spans/metrics include authentication outcomes, safe route templates,
status and measured elapsed time. Trace context propagates through outbox events
to consumer spans. Structured logs expose correlation/business trace/OTel trace
metadata without bodies/credentials. Backend and workers export OTLP to the local
Collector, traces to Tempo and metrics to Prometheus; Grafana provisions local
datasources and measured HTTP panels. There are no invented throughput or model
quality panels. Local diagnostics are not a retention/security certification.

Migration 0008 adds grants/outbox/inbox/projections/subscriptions/jobs/dead letters;
0009 adds revocable device registrations; 0010 adds durable job retry time and
state/attempt checks. Existing business UUIDs/hashes are preserved. The isolated
migration round trip starts at 0007; application DB upgrades only forward.

Docker Compose runs the complete local stack. Kubernetes manifests declare the
same application/event/observability components for a local cluster. Terraform
has only a kind-context Kubernetes provider and defaults to namespace-only;
deploy_local_stack is explicit. No cloud provider or hosted resource is present.
The deterministic CI workflow runs Go/backend/frontend/browser/evaluation gates
without model calls; writing it does not mean hosted CI ran. The audit records
which deployment checks actually executed and which failed.

The unchanged 104-scenario golden dataset remains a fixture-system release gate.
It does not establish production reliability, real-user utility, real CV accuracy
or semantic model quality. REAL EMBEDDING MODEL NOT CONFIGURED. Fixture embeddings
are not a real semantic model. Real CLIP/DINOv2/SAM/VLM remain unconfigured and
unexercised. REAL LLM JUDGE NOT CONFIGURED. Phase 9 is not part of this work.
