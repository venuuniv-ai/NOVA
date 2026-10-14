# ADR 0007: normalize media and discard original metadata

Accepted for Phase 5 local demonstration.

Use maintained Pillow with server byte/dimension/pixel limits, decoded MIME
validation, container checks, orientation normalization and clean RGB PNG
re-encoding. Discard original bytes, filenames, EXIF/GPS/XMP/ICC/text metadata.
Persist only bounded metadata and opaque UUID/hash references. Signing/hashing
is not encryption. No SVG, animation, URL fetch or arbitrary client path.

A private local Docker volume retains sanitized PNGs across service restart;
PostgreSQL owns task/owner/device links and idempotency. Verify content hashes
on access. Task/user ownership gates both media and mask artifact endpoints.
Store real SAM masks as bounded PNG artifacts, never huge arrays in JSONB.

This local filesystem is not a transactional or encrypted object store; an
interrupted write can leave an orphan file and retention is operator-managed.
No cloud storage, private image logging or automatic model downloads.
See [architecture](../phase-5-architecture.md).
