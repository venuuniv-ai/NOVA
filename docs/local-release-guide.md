# NOVA v1.0 local MVP — installation, usage and recovery

Candidate: **1.0.0-local-rc1**, prepared for the existing Apple M2/8 GiB local host.
Release readiness is determined by the checklist/test evidence, not by this guide's
existence. This is an authenticated local workflow MVP with **deterministic FIXTURE
AI by default**. It is not a live learned-model assistant or production deployment.
Existing real BGE/Qwen integrations and historical Phase 9/10 acceptance remain
available in source; fresh bounded operator approval is required before enabling
or testing real inference. No model is loaded by these commands.

## Prerequisites and installation

Use the reviewed source candidate on the prepared host, or unpack its source-only
archive to a local directory. Required existing tools: macOS Python 3, Docker
Desktop/Compose with the unchanged 4,106,604,544-byte allocation, installed Node/npm
and `frontend/node_modules`. Required existing images: `nova-backend:latest`,
`nova-gateway:local`, `nova-postgres-vector:local`, `redis:7-alpine`,
`apache/kafka:4.0.1`. Qualification additionally uses `nova-backend-tests:latest`,
`nova-gateway-compiler:local`, existing Chromium and optional local Keycloak image.
The verified frontend environment is Node 26.10.0/npm 11.19.1/Next 16.4.0.

There is **no automatic package installation, image pull/build or model download**.
Missing prerequisites cause a refusal: supply them through a separately approved
operator setup, rather than expecting this source archive to contain dependencies.
Fresh-machine provisioning is not qualified by this release. Start Docker Desktop
normally, save other work and close competing local stacks yourself. Do not change
Docker allocation or delete caches/volumes to make a check pass.

From the repository root:

```sh
./scripts/start-local.sh
python3 scripts/nova_local.py status
```

Start checks the reviewed source fingerprints, existing images/dependencies,
private data targeting, fixed Docker allocation, free ports, swap strictly below
2048 MiB and disk >=5 GiB. It uses the dedicated persistent `nova-v1-local` project,
not the protected Phase 9/10 qualification databases. Explicit private subnets avoid
Docker's exhausted default address pools without pruning existing networks or
changing internal network flags. The native standalone frontend is built from
installed packages only when its source changes; required static/public assets
are copied into the generated standalone directory. Nothing is installed.

PostgreSQL/Redis/API/gateway start first, then the broker and bounded workers, then
the frontend. Resource checks continue during startup and a task-owned watcher
checks disk/swap every two seconds while running. A violation stops only the
release's own processes/services and preserves volumes. This watcher and Node heap
limits are not hard host RAM quotas or a production supervisor.

## Sign in and use

Open `http://localhost:3000/auth`. Copy the short-lived local token from the private
file, without printing it into shared logs:

```sh
pbcopy < .secrets/release-v1/operator.token
```

Paste it into **Access token**, then Sign in. Credentials are generated through the
existing operator CLI; the original owned simulated Desktop is registered through
the authenticated device API if unenrolled, then a fresh device-version-bound token
is issued. Revoked devices are not silently re-enabled. The authenticated server,
not the UI or model, enforces roles and ownership. Token login uses the existing
HttpOnly/Strict cookie. The optional OIDC button is outside this default release
stack; do not use it unless separately configured local OIDC is running.

1. Create a task on Desktop. Open Device Continuity and wait for that page to load;
   continue to Wearable/Mobile. Task UUID and event history persist.
2. In Memory Center, create an explicit fact using a named subject and supported
   predicate such as `preferred_cuisine` or `preferred_beverage`. Review privacy,
   scope and lifecycle. Unconfirmed visual suggestions remain unconfirmed.
3. In `/inference`, select FIXTURE and the owned task. For a reproducible lexical
   grounding example, search the fact's full normalized text. Inspect original
   evidence UUID/quote and simulation labels. Fixture hash vectors are not learned
   semantic embeddings; fixture output is not a model quality measurement.
4. In Approval Center's Owned evidence drafts, ask a named preference question,
   e.g. “Which cuisine does named_subject prefer?” Optionally pin its memory UUID.
   Wait for QUEUED/RUNNING to become PENDING_APPROVAL. Inspect source/provenance,
   cancel or reject. **Phase 10 drafts cannot approve, edit or execute actions.**
   Legacy explicitly labeled communication simulations remain NOT SENT.
5. Local Operations is operator-only. Inspect bounded event/job history, page
   continuations and fixed safe diagnostics. Refresh for a new append boundary.
   Do not interpret DEAD as a measured model failure explanation.

Tokens last one hour. To issue a fresh one on a running stack:

```sh
python3 scripts/nova_local.py token
```

Then copy/paste the new private token and sign in again. Rotation/revocation makes
previous identity-bound draft grants stale: queued/pending drafts may expire rather
than revive under a new grant. Retained tasks and eligible memories are preserved.
Create a new explicit draft after re-authentication when needed. No automatic
external action is enabled.

## Health, smoke, shutdown and recovery

```sh
python3 scripts/nova_local.py status
python3 scripts/nova_local.py smoke
./scripts/stop-local.sh
python3 scripts/nova_local.py recover
```

After an intentional stop, health status reports BLOCKED because the services are
off; the stop command itself reports STOPPED. This does not invalidate the qualified
source candidate. Start the stack before expecting health status READY.

Status checks the authenticated identity, API/database readiness, frontend, required
running services and Docker health checks, plus tracked frontend/watcher processes.
Smoke creates clearly named fixture task/memory/draft records, checks original
citations, waits for one proposal, verifies approval/execution refusal, explicitly
rejects the draft, performs device handoffs, and runs three existing authenticated
browser journeys. It is not read-only and requires the installed browser/test tools;
run it only when you want these controlled local test records. It makes zero real
model calls and sends no external messages. Its records remain for audit.

Stop terminates only tracked task process groups and this Compose project, revokes
the temporary identity and preserves data/volumes/models. It does not stop Docker
Desktop or other user processes. Recovery performs that stop followed by the same
preflight/start sequence with fresh credentials and persistent volumes. Re-login
after recovery. It does not promise to preserve the visibility of stale draft
content after permission revocation. A partial/failed startup reports the ignored
log name; use status/recover after fixing the actual blocker. Do not repeat real
model requests or weaken safety checks to troubleshoot.

If Docker itself is stopped, start it normally before using recovery. If token
revocation cannot be verified, keep the release stopped and treat cleanup as
BLOCKED until the existing identity can be revoked or safely rotated through the
supported workflow. Resource-stop evidence is `.local/release-v1/resource-stop.json`;
command logs, smoke reports and measurements are in the same ignored directory.
Private credentials/database password are in `.secrets/release-v1`, mode 0600.
Back up these privately with the dedicated data volumes; losing the password file
must not be “fixed” by resetting a protected database.

## Rollback and source recovery

No new database migration is introduced: application head remains
`0011_inference_registry`. Do not downgrade the database or delete a volume.

1. Stop the release and confirm no release service/frontend process remains.
2. Preserve data volumes, private database credentials and any uncommitted work.
3. Retain the reviewed `nova-v1.0-local-rc1.tar.gz` plus its SHA-256 from
   `.local/release-v1/package.json`. The archive contains source/documentation only,
   not credentials, models, installed dependencies or user data.
4. Verify its checksum, unpack into a separate review directory, and compare its
   source manifest before restoring only the intended source files. Do not use a
   blanket Git reset/clean against user work. The packaging check reads back every
   archived member and verifies its hash; this is source recovery evidence, not
   a tested rollback of arbitrary future database migrations.
5. Run the same start/status/smoke procedure with the preserved private credentials
   and volumes. The launcher refuses source drift until a reviewed candidate is
   regenerated and qualified. If validation fails, leave it stopped; never fall
   back silently to different models, data or insecure configuration.

The Phase 10 checkpoint `80dc41af8d3742fdb700b02e342f579e06389fcf` remains intact as
history. Cross-version database rollback, public deployment, general AI quality,
vision and model judging are not claimed. The release checklist classifies those
separately from essential local workflow gates.
