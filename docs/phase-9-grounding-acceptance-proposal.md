# Corrected grounding application acceptance — NOT APPROVED / NOT EXECUTED

Prepared October 19, 2026. Current authorization covers offline correction only.
All earlier inference approvals are closed. This proposal activates nothing.

## Exact new approval requested

Authorize at most **two conditional owner-authenticated LOCAL_REAL RAG requests**,
zero retries, two BGE query embeddings and two Qwen generations. Case 2 runs only
if Case 1 passes. Stop on the first failure, safety violation or failed unload.
No warmup, health-generation probe, reindex, third request or output repair.

Both requests use task `70b45f12-b509-4443-a66f-81b86caf872c`, its independently
authenticated owner and existing namespace
`bge-small-en-v1.5@bd60ce951a6ec4edab8518c1b3301686`, HYBRID retrieval,
`nova-qwen-phase9-rag96`, output allowance 96. Verify the selected embedding
provider's namespace equals the requested namespace before submitting either
request; the API does not accept an arbitrary namespace override.

1. **Positive:** `Which cuisine does review_fixture prefer?`
   Require DONE, simulation=false, no fallback, valid non-abstaining GroundedOutput,
   the supported cuisine value in the full extractive answer, owned evidence UUID
   `4d4b4842-c804-4e72-90c9-7162d6436c37`, its unchanged exact quote, deterministic
   subject/predicate/value agreement and transactional source/privacy revalidation.
   A valid abstention is a failed positive acceptance. Invalid output, wrong
   citation, altered/stale quote or unsupported claim fails; do not repair/retry.
2. **Insufficiency, conditional on positive PASS:**
   `What is review_fixture's spacecraft launch authorization code?`
   Require DONE with explicit `abstain=true`, `claims=[]`, no invented evidence or
   action. This question lies outside the declared deterministic preference
   subset: retrieval still executes, but the application supplies no asserted
   supporting context. Report this as abstention on empty selected evidence,
   **not** proof of general model relevance calibration or unknown-answer detection.

The new code corrects source integrity, transaction timing, error classification
and context accounting. **The positive prompt/schema/user content may be identical
to the historical failed request.** Over-abstention is unresolved; no measured
model-behavior improvement justifies a success prediction. This is a proposed
application acceptance check after safety corrections, not a demonstrated prompt
fix or permission to repeat until successful.

## Prerequisites and unchanged limits

- Fresh explicit approval of this exact conditional sequence. Re-read current
  source/proposal and refuse drift; applicable offline tests must pass first.
- Fresh disk >=5 GiB, used swap <2048 MiB, private scoped host attestation,
  owner authentication/task authorization, private controller bearer verification,
  no resident/unowned model processes or listeners. Never reuse an old attestation.
- BGE revision `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, tensor 133466304 bytes,
  SHA-256 `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.
  CPU float32, 384 dimensions, existing batch-one/128-token bridge, two threads,
  RSS ceiling 1024 MiB. No artifact changes or installation.
- Qwen existing tensor 986048512 bytes, SHA-256
  `183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.
  Verify alias manifest/blob integrity and context 512, max output 96, CPU threads
  2, GPU layers 0, temperature 0, concurrency 1, sampled RSS ceiling 2048 MiB.
- Explicitly declare private `grounded_budget_profile="QWEN2_CHATML_0351"` only
  after verifying existing Ollama 0.35.1 and the reviewed Qwen2/ChatML template/
  grammar path. Unknown runtime/template/profile must refuse. This declaration
  adds no resource or inference authority. No private config is enabled by this
  proposal. Historical prompt-at-96 SHA-256 remains
  `1a722aaf032c5aa2949f0ea576d781870ea18bce6cbb0354b2d4447cccffda76`.
- Conservative request bound is 136 system + 32 framing + 16 margin + serialized
  user UTF-8 bytes + 96 output, <=512. Pinned runtime schema is supplied as grammar,
  not appended prompt text; unknown paths cannot claim zero schema prompt tokens.
  Full UUID/text must fit without truncation. Output completion remains unproven.
- Keep startup 30 seconds and inference eight seconds, existing lease, immediate
  busy refusal, watchdog, OS loopback sandbox and local-files-only/no-cloud policy.

## Required sequence and evidence

For each approved case: acquire BGE, perform one retrieval embedding, release and
verify all BGE descendants/listeners gone; fresh resource check; acquire Qwen,
perform one generation, release and verify termination. Existing application
validation checks schema/citations and current retrieved/sent source integrity
under the owner mutation lock through DONE commit. Record these actual timing
scopes without claiming privacy validation occurred before transport release.

Record request/run/retrieval IDs, namespace/fingerprints, classification (supported
claim / valid abstention / invalid response / safety failure), citation/privacy
results, reported tokens or UNKNOWN, model-call and HTTP latency, sampled RSS and
resource boundaries. No rejected raw output, private prompts or evidence logging.
Read-only vector IDs/digests/dimensions/namespace and reindex state must match
before/after; no reindex or historical-vector replacement is authorized.

Always stop task-owned services, disable scoped real configurations and close the
attestation in finally; verify no resident models/listeners. Preserve artifacts,
aliases, application data, vectors, caches and volumes. No downloads, packages,
paid/cloud calls, external messages, security weakening, resource increases,
Git staging/commit/push/remotes or Phase 10. Final cross-stack qualification occurs
only after separately approved real acceptance passes. Phase 9 remains NOT COMPLETE.

**STOP here. Fresh explicit operator approval is required before activation.**
