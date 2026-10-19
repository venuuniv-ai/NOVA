# Phase 9 final acceptance proposal — NOT APPROVED / NOT EXECUTED

October 16, 2026. This proposal follows the operator's final Phase 9 mission,
sections 1, 4 and 13. That mission explicitly requires fresh authorization before
any further real-model execution or runtime budget change. No approval is inferred
from the historical standalone or Phase 9B runs.

The old RAG completion was not retained. Its 276 input / 32 output tokens and
INVALID_RESPONSE establish failure, not a specific syntax, citation or truncation
cause. The new diagnostic classifier records bounded categories, parser class,
whitelisted validation paths/types, finish reason and reported counts without
persisting model text. EOF plus finish_reason=length is an indicator, not a proof
of the historical cause. Local grounded requests now supply a JSON schema;
compatibility with installed Ollama 0.35.1 remains unverified until execution.
Unsupported structured output must fail closed; do not fall back to free text.

## Proposed independent approvals

1. **Profile implementation and metadata:** add a distinct task-owned alias
   `nova-qwen-phase9-rag96`, referencing only the existing verified Qwen tensor.
   Set context=512, num_predict=96, num_thread=2, num_gpu=0, temperature=0,
   concurrency=1. Extend private configuration/controller validation only for
   this alias's 96-token ceiling, retaining the original alias's 32-token ceiling.
   No weights, packages, conversion or replacement runtime. Alias metadata is
   estimated below 20 KiB; verify actual bytes. This profile is not implemented
   or enabled by this document.
2. **One positive acceptance cycle:** authenticated BGE embedding and owned
   retrieval of the existing controlled memory namespace, verified BGE release,
   fresh resource check, then one authenticated Qwen GROUNDED request with at
   most one evidence item. Require valid JSON/schema, an existing owned evidence
   UUID, the exact supported quote and post-generation eligibility checks.
3. **One insufficiency acceptance cycle:** one authenticated BGE retrieval for
   an unrelated controlled question, verified release and fresh resource check,
   then one Qwen GROUNDED request expected to abstain on irrelevant evidence.
   A failed abstention is a failed acceptance result. Do not filter by a new
   uncalibrated similarity threshold to force a pass.

Maximum scope: two BGE requests and two Qwen generations, sequential residency,
no inference retries. Any additional generation, reindexing, benchmark or change
of bounds requires a new scope decision. Existing real vectors and fixture vectors
remain untouched. Positive cycle query: “Which cuisine do I prefer?”; insufficiency
query: “What is my spacecraft launch authorization code?” Only controlled owned
memory may be included; inspect its eligibility before invoking models. An existing
cache hit is not new model execution: use fresh run keys and verify attempt/usage
provenance. Stop if the expected evidence is absent or the profile cannot be enforced.

## Exact application requests proposed

Use the existing controlled owner/task
`70b45f12-b509-4443-a66f-81b86caf872c` and namespace
`bge-small-en-v1.5@bd60ce951a6ec4edab8518c1b3301686`.
The approved pinned BGE configuration and new alias must be private operator
settings, never client-supplied model paths or runtime URLs. Verify the existing
three eligible 384-dimensional vectors before execution; do not reindex or overwrite
them. Stop if owner, evidence, model identity or namespace differs from this scope.

Make exactly two authenticated POSTs to `/api/v1/inference/generate`, each with
a fresh UUID request_id. Both use this body; change only the query for cycle two:

```json
{
  "task_id": "70b45f12-b509-4443-a66f-81b86caf872c",
  "request_id": "<fresh UUID for this cycle>",
  "mode": "LOCAL_REAL",
  "operation": "RAG",
  "query": "Which cuisine do I prefer?",
  "retrieval": "HYBRID",
  "max_output_tokens": 96
}
```

Second query: `What is my spacecraft launch authorization code?`.
Each RAG request performs one BGE query embedding/retrieval followed by one Qwen
generation. No additional standalone EMBED request or acquisition is included.
Read-only status, ownership and cleanup checks are allowed; any third generation
is outside this proposal. Use the existing eight-second inference deadline and
an outer 15-second generation hard-stop; acquisition remains separately bounded.
After implementing the separately approved alias allowance, rerun its offline
limits/refusal tests and applicable regression before requesting either cycle.

## Budget rationale and stop rules

A successful claim must encode `claims`, `evidence_id`, a UUID, `quote`, the exact
quote and `abstain`. The compact JSON alone is substantially longer than the short
SUMMARY response. Rough planning allowance: 60–90 output tokens for one short
quote and UUID; tokenizer behavior is not measured here. Proposed 96 is bounded
headroom, not evidence that generation will finish. An explicit abstention is
shorter: `{"claims":[],"abstain":true}`. No automatic budget increase is allowed.

Context remains 512; bound selected evidence and prompt using the existing exposure
checks. More allowed output can increase compute time and resident activations;
fixed context does not prove identical actual memory. Keep the measured 2048 MiB
Qwen ceiling, CPU-only two threads, eight-second inference deadline, 30-second
startup bound and current lease/watchdog protections. Keep BGE float32 CPU,
1024 MiB, batch one, at most 128 input tokens and two threads. No timeout extension
is included. If schema generation or a 96-token response exceeds bounds, record
failure and stop rather than repeating or weakening validation.

Before each acquisition: free disk >=5 GiB, swap <2048 MiB, fresh private host
attestation, verified model hashes, no resident model/listener and explicit scoped
operator resource approval. Monitor sampled runtime-tree RSS and global resources.
A sample is not a hard RAM quota. Deny external model-network access using the
existing loopback sandbox and offline flags. Stop on unexpected network activity,
artifact mismatch, shutdown failure, a resource breach or unowned listener.
Release in finally; verify process/descendant termination and listener disappearance
before acquiring the next model. Keep private registries disabled after closure.

BGE tensor SHA-256:
`3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.
Qwen tensor SHA-256:
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.
No download, paid transport, external action, volume/cache deletion, commit or
Phase 10 is part of these approvals.

## Evidence and remaining quality work

Record authenticated run IDs and artifact fingerprints; acquire, inference,
validation, release and HTTP durations at their actual scopes; reported usage or
UNKNOWN; safe failure category; sampled RSS; before/after swap/disk; unload evidence.
Persist no raw private prompts/completions or memory text in diagnostic records.
Success of these two finite cases cannot establish general model quality.

The unchanged retrieval-v1 set is five positives and one no-answer query. Historical
real BGE Recall@5=1, MRR=.9, nDCG@5=.9101 and five irrelevant no-answer results remain
historical. Exact top-k ranking always fills available candidates without a relevance
cutoff; RRF fuses ranks rather than estimating answerability. Future explicit real
evaluation can report content-free per-rank similarities/fusion scores, but was not
rerun here. Before any threshold proposal, obtain independently reviewed calibration
labels and an untouched holdout; report precision/recall and abstention trade-offs.
No human review or suitable new labels are assumed.

The pinned BGE model card permits no-instruction v1.5 embeddings, recommends a
query prefix for some retrieval tasks, and specifies CLS pooling plus normalization.
The current bridge consistently uses no prefix, CLS and L2 normalization. Changing
query preprocessing would require explicit version/provenance and separate evaluation;
do not silently change the existing namespace.

Protocol references: [Ollama structured outputs](https://github.com/ollama/ollama/blob/main/docs/capabilities/structured-outputs.mdx),
[OpenAI-compatible protocol](https://github.com/ollama/ollama/blob/main/docs/api/openai-compatibility.mdx).
These describe protocol intent; they do not validate the installed runtime or certify
semantic correctness. Approval is the next boundary, after offline review and audit.
