# Phase 9 implementation reference

Start: clean main at f4c430cbf42a1168c3e167780dc8ade8844d450f.
Extend Phase 4 ModelRoutingService/ProviderRegistry, Phase 6 EmbeddingProvider and
MemoryService, Phase 2 Kernel agents and Phase 5 owned perception evidence. Do not
create a parallel task system. Default FIXTURE, explicit LOCAL_REAL or DISABLED;
never silently fall back from LOCAL_REAL to fixtures or cloud.

Operator configuration is a private local JSON file, never API-selected paths or
URLs. Model metadata includes artifact digest, version, license, estimates,
capabilities and an explicit resource approval. Local execution additionally
requires a satisfied live resource gate. No downloader, runtime installation or
resource allocation changes. Existing artifact use must be read-only.

Reuse durable model calls for generation and add bounded run metadata for
mode/evidence/error/latency without prompts/completions. Version embeddings by
artifact-derived namespaces. Reindex in explicit owned checkpointed batches;
retain original vectors and revalidate memory eligibility. Grounded generation
uses owned eligible memory and owned visual observations as untrusted evidence;
reject foreign citations, conflicting facts and invalid schemas. Citation validity
is not factual entailment. Model output never chooses tools or grants approval.

Local transport inherits loopback allowlisting, timeouts, byte bounds, no proxies
or redirects; add async cancellation-safe concurrency (one active inference),
short queue timeout and no retries. Preserve deterministic policy checks on agents
and action hashes. Real adapters return typed unavailable/resource-blocked errors.

Acceptance: deterministic fixtures and existing 495 backend/53 cross-profile
browser/104 golden cases retained; new contracts, version isolation, reindex,
citations, injection, ownership and mode tests. Real test/benchmark opt-in stays
separate; skip or block honestly when resources/models are unavailable. Separate
versioned evaluation expectations with safety violations failing independent of
averages. Report Recall/MRR/nDCG only for executed labeled retrieval cases and
never call hash embeddings semantic quality. Human/model judgments not fabricated.

Licensing: cached Qwen2.5-1.5B-Instruct metadata/license says Apache-2.0. Candidate
BAAI/bge-small-en-v1.5 is MIT, 384 dimensions; no embedding download is approved.
Implementation/configuration/execution/measurement/evaluation are separate states.
Phase 8 Kubernetes and NetworkPolicy remain unverified. No commit/push/Phase 10.
