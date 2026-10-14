# ADR 0009: exact pgvector search and independent rank fusion

Accepted for Phase 6 small local datasets.

Extend the existing PostgreSQL 17 Alpine image with verified-source pgvector,
preserving its volume. Store embeddings in VECTOR, not JSONB, with explicit
provider/model/dimension namespaces. Use exact search; dataset size does not
justify ANN indexes. Filter ownership/scope/state/time/privacy before ranking.

Keep structured, PostgreSQL lexical and vector rankings independent; fuse via
RRF k=60. Expose source ranks and provenance. Similarity is relevance, never truth
or inference confidence. Fixture hash vectors exercise infrastructure only.
Optional embeddings use an existing local endpoint, no cloud/download fallback.

Reject model/shape/NaN/Inf namespace manipulation. Persist bounded retrieval
snapshots for planner explanation. No managed vector database or ML installation.
See [architecture](../phase-6-architecture.md).
