# Phase 9F minimal grounded diagnostic — NOT APPROVED / NOT EXECUTED

Prepared October 17, 2026. Phase 9F authorizes offline investigation only. All
earlier inference approvals are closed. This proposal requires fresh explicit
operator approval; it does not authorize activation.

The pinned llama.cpp schema converter emits required properties before optional
properties. Our unchanged schema requires `abstain` and makes `claims` optional.
The earlier prompt's claims-first examples conflict with that grammar order.
Only the examples have been corrected to abstain-first. Their meaning, the schema
and application validators are unchanged. This defect is confirmed by source
inspection; its causal contribution to the prior abstentions is unproven.

## Exact scope to approve

Authorize **one authenticated LOCAL_REAL HYBRID RAG diagnostic cycle**, with the
corrected example order as the only intended request-construction change from 9E:

- Query: **Which cuisine does review_fixture prefer?**
- Task: `70b45f12-b509-4443-a66f-81b86caf872c`.
- Namespace: `bge-small-en-v1.5@bd60ce951a6ec4edab8518c1b3301686`.
- Existing alias: `nova-qwen-phase9-rag96`; max_output_tokens=96.
- Expected existing cuisine evidence: `4d4b4842-c804-4e72-90c9-7162d6436c37`.
- Maximum **one BGE query embedding, one Qwen generation, one RAG request,
  zero retries**. No separate model probe, insufficiency cycle, reindex or benchmark.

Use the existing authenticated `/api/v1/inference/generate` operation RAG and a
fresh request UUID. Require an actual invocation/cache MISS. Verify ownership,
ACTIVE eligibility, namespace/fingerprint and the existing controlled source
against the pinned public corpus without exposing private text. Do not supply
the answer or a forced output prefix. Keep the existing schema and untrusted-data
boundary. Preserve all source records and historical vectors.

Sequence: fresh gates and integrity/authentication checks → BGE retrieval → verified
BGE termination → fresh gate → Qwen generation → unchanged schema/citation/privacy
validation → verified Qwen termination. Do not overlap model residency.

Keep context 512, output <=96, CPU threads 2, GPU layers 0, temperature 0,
concurrency 1; BGE CPU float32/batch one/input <=128 tokens. Retain memory ceilings
1024 MiB BGE / 2048 MiB Qwen, startup 30 seconds, inference eight seconds and
existing lease/watchdog/zero-queue safeguards. Require disk >=5 GiB, swap <2048
MiB, fresh private scoped attestation, no resident model/unowned listener and
verified private operator configuration. Retain sandbox and offline network rules.

Reverify the existing tensors before activation:

- BGE revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, SHA-256
  `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.
- Qwen SHA-256
  `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.

## Interpretation and mandatory stop

A supported positive result requires the correct owned UUID, full exact quote,
successful post-generation privacy revalidation and no external authority/action.
Record a valid positive-question abstention as failed positive acceptance. Record
invalid JSON/schema/citation, incorrect source selection or any safety failure
separately. Changed selected evidence makes comparison with 9E inconclusive.
Do not regenerate, repair output, change schema/limits, force a claim or introduce
a relevance cutoff. Stop after this one cycle, including if it fails.

Record safe IDs, selected evidence ID/fingerprint, cache/invocation provenance,
finish reason, token usage, timing scopes, sampled RSS, resource boundaries and
verified termination. Do not persist raw private prompts/completions/evidence.
Stop all task-owned services, disable private real configurations and close the
approval in finally. Preserve aliases, artifacts, application data and volumes.

This isolates the corrected prompt/grammar mismatch while retaining the 9E path;
one outcome cannot prove causality or general model reliability. Even if positive
succeeds, the separate insufficiency acceptance remains pending another explicit
approval. No download, installation, paid/cloud API, external message, commit,
push, remote configuration or Phase 10 is included.

**No execution occurred in Phase 9F. Await fresh approval for this exact scope.**
