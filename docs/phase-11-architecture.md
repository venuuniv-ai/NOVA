# Phase 11 — local reliability, security and operational qualification

Scope approved by the October 20 operator instruction to complete Phase 11 after
review of the proposed specification. The original proposal is preserved as
preparation history; its exact pre-implementation bytes and workload freeze are
ignored evidence under `.local/phase11`.

## Operational metadata

The existing operator-only `GET /api/v1/operations/tasks/{task_id}` now accepts
`limit` (default 50, 1–100), `after`, `jobs_after` and optional `through`
(nonnegative outbox sequences). Existing response fields remain; `page` adds the
captured high-water mark and independent nullable event/job continuation cursors.
Task ownership is checked before any metadata query. Every event/job query also
scopes owner/task, and the projection owner is checked before exposing its cursor.

Events order by immutable outbox sequence. Jobs join their original outbox event
and use that same unique sequence, avoiding a mutable update-time cursor. First
capture the largest visible task sequence; subsequent pages carry `through` to
exclude newly appended events. Fetch at most `limit+1` rows per collection; batch
the bounded inbox receipts rather than querying once per event. Only the existing
three known consumer names are exposed. There is no count query or source/prompt/
provider-body inclusion. DEAD jobs have the fixed diagnostic
`TERMINAL_JOB_FAILURE`, not an inferred resource/model failure reason.

This is an append high-water boundary, not an MVCC snapshot or a complete export.
Delivery status can change between reads and a newly materialized job for an old
event may appear on refresh. Refresh starts a new view. Existing small-task
acceptance scripts continue to work; large histories must follow page cursors.
No table, migration, retention policy or new action authority is introduced.

## Operations UI

The existing task inspector renders typed metadata, with independent event/job
continuations, explicit refresh, empty lists, loading feedback, retry after errors
and UNKNOWN for unavailable diagnostic/projection values. Component identity is
bound to the selected task; abort and mounted-state checks suppress stale responses.
Pagination preserves the captured high-water mark. No automatic polling replaces
the current page. The existing opt-in fixture subscription remains the only
mutation on this screen; Phase 10 drafts gain no approval/execution controls.

## Qualification entrypoint

`python3 scripts/qualify_phase11.py` runs host/controller, PostgreSQL backend,
Go/frontend and local integration stages sequentially. `--stages` permits focused
investigation; passing a subset is labeled PARTIAL_PASS, never complete qualification.
No result from an omitted stage is invented. The runner refuses competing containers/
listeners, changed Docker allocation, unsafe disk/swap and unreviewed Compose mounts,
external/shared volumes or real provider configuration. It uses a fresh isolated
project and existing explicitly named images with pull disabled. Read-only source
mounts keep current code separate from runtime/test data.

The generated overlay retains Phase 10 caps: backend/worker 384 MiB, PostgreSQL
192 MiB for application integration, Redis 64 MiB, Kafka/Keycloak 768 MiB each;
backend-test runner/test DB 512 MiB each and test Redis 48 MiB. Kafka workers stop
before Keycloak starts. Docker remains 4,106,604,544 bytes. Node heap limits are
512 MiB for serving and 768 MiB for building, not hardware-enforced RSS quotas.
Disk >=5 GiB and swap strictly <2048 MiB are sampled throughout heavy work; no
model is activated. Browser traffic is paced across quota windows without changing
the gateway limit, retry count or assertions.

The runner captures per-command exit code, expected exit and timing to ignored
JSON/log files. The deliberately cautious golden candidate requires exit 1. Any
required-stage failure, unsafe measurement or failed cleanup makes overall FAIL.
Only task-owned process groups and project services are stopped; volumes remain.
Private local/OIDC grants are scoped to dedicated data and revoked in finally.

## Security and recovery

Existing local/OIDC authentication, operator RBAC, task ownership, device/version
bindings, source/conflict revalidation and atomic Phase 10 acceptance remain
unchanged. A new deterministic regression drives the existing manual job retry
route after an ambiguous LOCAL_REAL RUNNING record; the existing terminal guard
must refuse provider acquisition and leave no proposal/approval/execution. This
does not kill a real model or measure learned quality.

All current real provider settings remain disabled. No generation, external
message, paid service, new model or deployment is part of Phase 11. Historical
Phase 9/10 real results and failures remain unchanged. Existing Kubernetes and
NetworkPolicy qualifications remain limited as audited in Phase 8.
