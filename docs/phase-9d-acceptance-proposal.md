# Phase 9D bounded acceptance proposal — NOT APPROVED / NOT EXECUTED

Prepared October 17, 2026 (America/New_York). Phase 9D authorizes offline work only.
The earlier October 17 model authorization ended at its first failed positive
cycle. It does not authorize this proposal. No model is loaded by this document.

## Findings and intended test

The old prompt gave an explicit abstention example but no positive claims example
or explicit mapping from evidence `id`/`text` to `evidence_id`/`quote`. The revised
prompt explains both branches, one exact supported claim, the numeric output budget,
and missing/irrelevant/conflicting evidence. It keeps evidence as untrusted data,
forbids tools/actions/approvals and never invents an identity relation or a citation.
The output schema, exact-quote/UUID validation, post-generation privacy checks,
full-set conflict checks, namespace and retrieval thresholds are unchanged.

These are confirmed instruction gaps, not a proven explanation of Qwen's decision.
No new model output exists. Scripted tests establish request construction and
validation only; they cannot establish real-model relevance or instruction following.

A read-only check confirmed that the selected active, owner-authorized record has
the public dataset's subject label `review_fixture` and preferred_cuisine predicate.
Its normalized text matches the public pinned fixture. Ownership grants access;
it does not prove the subject label identifies the requester. The previous question
“Which cuisine do I prefer?” leaves that identity mapping unstated. Why Qwen abstained
remains unresolved; subject-reference ambiguity and the asymmetric old prompt are
hypotheses, not measured causes.

This proposal therefore makes the positive question explicitly about the source
entity. It does not change the fact or hardcode its cuisine value. It is a new
acceptance case, not a retroactive pass for the original first-person question.
If answering the original question is required, first establish a legitimate subject
mapping separately; do not manufacture one from ownership.

## Exact new scope to authorize

Use the existing controlled owner and task:
`70b45f12-b509-4443-a66f-81b86caf872c`.
Preserve namespace:
`bge-small-en-v1.5@bd60ce951a6ec4edab8518c1b3301686`.
Preserve the three historical 384-D real vectors and their fixture vectors.
Use existing alias `nova-qwen-phase9-rag96`; do not create another alias.

Authorize **at most two authenticated LOCAL_REAL RAG requests**, one each:

1. Positive: **Which cuisine does review_fixture prefer?**
2. Only if the positive cycle succeeds: **What is review_fixture's spacecraft launch authorization code?**

POST `/api/v1/inference/generate` with this body, replacing request_id with a fresh
UUID and changing only query for the second cycle:

```json
{
  "task_id": "70b45f12-b509-4443-a66f-81b86caf872c",
  "request_id": "<fresh UUID>",
  "mode": "LOCAL_REAL",
  "operation": "RAG",
  "query": "Which cuisine does review_fixture prefer?",
  "retrieval": "HYBRID",
  "max_output_tokens": 96
}
```

Maximum: two BGE query embeddings, two Qwen generations, zero inference retries.
No separate embedding probe, reindex, relevance benchmark, generation experiment,
additional query, new model or paid traffic. Read-only ownership, integrity,
configuration, ledger and cleanup checks are permitted. Confirm cache MISS and
actual invoked provenance; a cache hit is not real inference evidence.

## Unchanged limits and prerequisites

Qwen: context 512, output <=96, CPU threads 2, GPU layers 0, temperature 0,
concurrency 1, memory ceiling 2048 MiB. BGE: existing pinned CPU float32 bridge,
batch one, <=128 input tokens, two threads, memory ceiling 1024 MiB. Preserve the
existing eight-second inference deadline, 30-second startup bound, lease/queue
refusal and watchdog protections. No automatic budget or timeout increases.

Before each acquisition, require fresh observations and private scoped approval:
free disk >=5 GiB, swap <2048 MiB, no resident model/unowned listener, no concurrent
runtime. Verify private operator configuration and tensor fingerprints again:

- BGE revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, SHA-256
  `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.
- Qwen SHA-256
  `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.

Verify current offline regression and the exact stored source eligibility before
execution. The longer instruction template has not been tokenized by Qwen or
measured at runtime in Phase 9D. Request construction preserves full content and
the existing exposure gate; actual 512-token context compatibility still needs
verification. Refuse overflow; do not truncate, raise limits or repeatedly retry.
Keep the existing loopback-only sandbox, offline/local-files-only loading and no
cloud/fixture fallback for explicit real requests.

## Required sequence, outcomes and stop

For each authorized RAG request: BGE retrieval → verified BGE release/process and
listener disappearance → fresh resource check → Qwen generation → strict schema,
citation and privacy validation → verified Qwen release. Never overlap residency.

Positive PASS requires at least one directly supported claim with the existing owned
cuisine evidence UUID and full exact quote, successful post-generation eligibility
revalidation and no authority fields/actions. A valid abstention on the positive
question is a failed positive test, even if the application returns DONE.

Second-cycle PASS requires a valid explicit abstention with no claims. An irrelevant
but correctly quoted citation is not a valid answer to the spacecraft question.
Do not introduce a similarity cutoff to force abstention or relabel a failure.

Stop after either failed cycle, resource/security violation, identity mismatch,
unexpected network activity, unverified termination or unavailable configured runtime.
No repeated regeneration, schema repair, evidence fabrication or limit relaxation.
Terminate task-owned runtimes in finally, disable private real configurations and
close the scoped attestation. Preserve original aliases, models, vectors and all
application/cache/volume data. No commit, push, remote, external message or Phase 10.

Record safe run/request IDs, model fingerprints, actual token usage or UNKNOWN,
HTTP/acquisition/inference/validation/release durations at their observed scopes,
sampled RSS, disk/swap before and after, result category and verified unload.
Do not persist raw private prompts/completions or source contents in diagnostics.
Report positive answers, abstentions and failures separately. No general AI-quality,
production-readiness or historical-query-success claim follows from two finite cases.

**Await fresh explicit approval. No execution is authorized by Phase 9D.**
