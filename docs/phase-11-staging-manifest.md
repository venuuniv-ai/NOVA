# Phase 11 staging manifest — nothing staged

Baseline main/HEAD: `80dc41af8d3742fdb700b02e342f579e06389fcf` (Phase 10).
Scope approved: local reliability, security and operational qualification.
Final acceptance is recorded in the Phase 11 audit/evidence; no checkpoint is
implied. Keep Phase 11 changes uncommitted. No staging, commit, push or remote
change is authorized by the implementation instruction.

## Exact candidate inventory

```text
M README.md
M backend/app/events/api.py
A backend/tests/test_operations.py
M backend/tests/test_owned_drafts.py
M docs/architecture.md
A docs/local-release-checklist.md
A docs/local-release-guide.md
A docs/local-release-test-evidence.md
A docs/phase-11-architecture.md
A docs/phase-11-implementation-audit.md
A docs/phase-11-proposed-specification.md
A docs/phase-11-staging-manifest.md
A docs/phase-11-test-evidence.md
M frontend/app/operations/page.tsx
M frontend/tests/continuity.spec.ts
A frontend/tests/operations.spec.ts
A release/local-v1.0.json
M scripts/acceptance_phase10.py
A scripts/nova_local.py
A scripts/package_local_release.py
A scripts/phase11_integration.py
A scripts/qualify_phase11.py
A scripts/smoke_local_release.py
A scripts/start-local.sh
A scripts/stop-local.sh
A scripts/test_local_release.py
A scripts/test_phase11_qualification.py
```

Only source/tests/documentation belong here. No credential, private real registry,
model artifact, activation attestation, runtime evidence/log/database, generated
build/dependency/browser output, qualification overlay or installed image is
included. Evidence stays ignored under `.local/phase11`, private qualification
grants under `.secrets/nova-phase11-q-*`. The initial isolated-image installation
deviation is disclosed in the audit; its image/artifacts are outside Git.

Production changes are confined to bounded operational metadata and its UI.
Existing draft/model/grounding/approval contracts remain unchanged. The Phase 10
fixture acceptance harness now recognizes the exact validated Phase 11 project
format for qualification; arbitrary project names still refuse. No migration or
new dependency is proposed. Preserve Phase 1–10 history and measured audits.

Before a separately authorized checkpoint: compare all candidate paths with this
inventory, verify regular UTF-8 text, inspect the complete diff, scan for private
material, run whitespace checks, then compare the exact staged inventory. Do not
silently stage unrelated files or stage ignored evidence. Review current audit
results and limitations before any completion claim or checkpoint.


## Final combined Phase 11 / local MVP review

The final inventory above combines 17 Phase 11 paths with ten explicitly authorized
local release paths: **27 text files, seven modified / twenty added**. Shared README
and architecture changes describe both scopes. Phase 11 complete offline entrypoint
PASS and all MVP P0 lifecycle gates are recorded in their audits/evidence. Model
activation/external action stayed disabled; current services/grants are closed.
The source-only candidate excludes private/runtime/dependency/build artifacts and
verifies runtime fingerprints/archive hashes. Earlier partial/failure statements
remain history; no failed command was relabeled as passing.

Nothing staged or committed. The Phase 10 checkpoint and its ancestry remain HEAD;
no remote operation. A future checkpoint requires separate explicit authorization
and an exact fresh inventory review, not an implicit commit from release readiness.
