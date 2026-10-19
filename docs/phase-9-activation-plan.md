# Phase 9 proposed activation plan — NOT APPROVED / NOT EXECUTED

Prepared October 16, 2026. This is a reviewable plan, not authorization to install,
download or load a model. Existing Phase 9 adapters/routing/memory stay in place.
No package wheel, model file, runtime installation or model startup was performed.
Only public package-index metadata was read to resolve the proposed environment.

## Resource and authorization separation

Current disk/swap thresholds pass; the fresh private attestation is saved in the
ignored `.secrets/phase9-post-restart-attestation.json`, mode 0600, valid one hour.
It records measurements and proposed budgets, **operator_resource_approved=false**
and no download/install/load approvals. It has not been exported into any process.
The stopped application's registry has not been activated. Attestation creation
does not grant model-load authority. Remeasure immediately before any action.

Proposed BGE CPU memory declaration: 1024 MiB; first Qwen declaration: 2048 MiB.
These satisfy the schema's declaration ceiling, not a demonstrated memory fit.
Monitor actual process footprint and global swap; refuse/stop at the declared
budget, disk <5 GiB or swap >=2048 MiB. Do not raise ceilings to force a pass.
macOS free/inactive memory is reclaimable to varying degrees, not a guaranteed
allocation. No Docker allocation changes, host restarts or cache/volume deletion.

## A. Approved artifact and installation scope to request

Only BAAI/bge-small-en-v1.5 revision
`5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, exactly the files in
[existing authoritative model manifest](phase-9-model-download-proposal.json).
Model tensor SHA-256:
`3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`.
License declared MIT; preserve the pinned model card/license notice. Do not fetch
ONNX, GGUF, additional weights, sentence-transformers or another model/runtime.

Use an isolated host Python 3.14.8 arm64 virtual environment under ignored `.local`,
not the backend environment, global pip or Anaconda. The existing Anaconda 3.13.5
arm64 interpreter was inspected: NumPy exists but torch/transformers/tokenizers/
safetensors/FastAPI/uvicorn/sentence-transformers do not. Reusing it would still
require installation and would alter a shared environment, so it is not proposed.

Choose PyTorch CPU + Transformers/Tokenizer/Safetensors only, without optional
GPU/vision/audio/train/serving extras. No FastAPI/uvicorn install is needed for a
small loopback standard-library HTTP bridge. Existing Ollama remains the sole text
runtime. This adds one necessary embedding backend, not competing text runtimes.
The bridge must expose the existing LocalProvider /v1/embeddings contract; it is
not a parallel memory/routing service. Its host-server implementation is a
follow-up prerequisite, not an already tested or installed runtime.

The following binary package closure was resolved from PyPI JSON metadata and
compatible interpreter wheel tags; dependency markers exclude Linux CUDA stacks.
All selected direct/transitive version constraints were checked. This is **not**
a successful pip install, advisory scan or proof of runtime compatibility. No
wheel/sdist was downloaded and no model/framework imported to load weights.

| Distribution | Exact version | Selected arm64/universal wheel | Archive bytes |
| --- | --- | --- | --- |
| annotated-doc | 0.0.5 | annotated_doc-0.0.5-py3-none-any.whl | 5302 |
| anyio | 4.15.1 | anyio-4.15.1-py3-none-any.whl | 132079 |
| click | 8.5.0 | click-8.5.0-py3-none-any.whl | 125251 |
| filelock | 4.2.0 | filelock-4.2.0-py3-none-any.whl | 135032 |
| fsspec | 2026.9.0 | fsspec-2026.9.0-py3-none-any.whl | 221738 |
| h11 | 0.16.0 | h11-0.16.0-py3-none-any.whl | 37515 |
| hf-xet | 1.7.0 | hf_xet-1.7.0-cp38-abi3-macosx_11_0_arm64.whl | 3560352 |
| httpcore2 | 2.13.1 | httpcore2-2.13.1-py3-none-any.whl | 83423 |
| httpx2 | 2.13.1 | httpx2-2.13.1-py3-none-any.whl | 95597 |
| huggingface-hub | 2.2.0 | huggingface_hub-2.2.0-py3-none-any.whl | 839884 |
| idna | 3.20 | idna-3.20-py3-none-any.whl | 69583 |
| jinja2 | 3.1.6 | jinja2-3.1.6-py3-none-any.whl | 134899 |
| markdown-it-py | 4.2.0 | markdown_it_py-4.2.0-py3-none-any.whl | 91687 |
| markupsafe | 3.0.4 | markupsafe-3.0.4-cp314-cp314-macosx_11_0_arm64.whl | 12061 |
| mdurl | 0.1.2 | mdurl-0.1.2-py3-none-any.whl | 9979 |
| mpmath | 1.3.0 | mpmath-1.3.0-py3-none-any.whl | 536198 |
| networkx | 3.7 | networkx-3.7-py3-none-any.whl | 2142205 |
| numpy | 2.5.4 | numpy-2.5.4-cp314-cp314-macosx_14_0_arm64.whl | 5455617 |
| packaging | 26.3 | packaging-26.3-py3-none-any.whl | 129956 |
| pygments | 2.21.0 | pygments-2.21.0-py3-none-any.whl | 1250147 |
| pyyaml | 6.0.3 | pyyaml-6.0.3-cp314-cp314-macosx_11_0_arm64.whl | 173809 |
| regex | 2026.9.29 | regex-2026.9.29-cp314-cp314-macosx_11_0_arm64.whl | 293518 |
| rich | 15.0.0 | rich-15.0.0-py3-none-any.whl | 310654 |
| safetensors | 0.8.0 | safetensors-0.8.0-cp310-abi3-macosx_11_0_arm64.whl | 484562 |
| setuptools | 84.0.0 | setuptools-84.0.0-py3-none-any.whl | 818216 |
| shellingham | 1.5.4 | shellingham-1.5.4-py2.py3-none-any.whl | 9755 |
| sympy | 1.14.0 | sympy-1.14.0-py3-none-any.whl | 6299353 |
| tokenizers | 0.23.3 | tokenizers-0.23.3-cp310-abi3-macosx_11_0_arm64.whl | 3101381 |
| torch | 2.14.1 | torch-2.14.1-cp314-cp314-macosx_14_0_arm64.whl | 127325330 |
| tqdm | 4.70.1 | tqdm-4.70.1-py3-none-any.whl | 80199 |
| transformers | 5.20.0 | transformers-5.20.0-py3-none-any.whl | 12826514 |
| truststore | 0.10.5 | truststore-0.10.5-py3-none-any.whl | 19017 |
| typer | 0.27.3 | typer-0.27.3-py3-none-any.whl | 123312 |
| typing-extensions | 4.16.0 | typing_extensions-4.16.0-py3-none-any.whl | 45571 |

Total package archives: **166979696 bytes** (159.24 MiB).
Pinned model/config/tokenizer/model-card files: **134505225 bytes**
(128.27 MiB). Combined known archives/artifacts:
**301484921 bytes** (287.52 MiB).

Expected installed environment/model footprint: roughly **0.6–1.5 GiB**; unverified
planning range. Unpacked size cannot be measured without downloading packages.
Reserve **3 GiB incremental disk** for the environment, artifacts, transient wheel
unpacking, venv pip and small logs/metadata. This is an approval budget, not an
exact installed-size claim. No persistent wheel cache (`--no-cache-dir`), no source
builds, no automatic dependency substitutions. Abort if the budget is exceeded.
No model conversion or duplicate weight format is included.

## B. Exact proposed installation commands — DO NOT RUN BEFORE APPROVAL

After approval and a fresh passing preflight, materialize the lock block below
verbatim as `.local/phase9/embedding-runtime.lock`. Then:

```sh
python3 -m venv .local/phase9/embedding-venv
.local/phase9/embedding-venv/bin/python -m pip install \
  --no-cache-dir --only-binary=:all: --require-hashes \
  -r .local/phase9/embedding-runtime.lock
.local/phase9/embedding-venv/bin/python -m pip check
```

No pip upgrade or editable/source install is included. Download only manifest
files into `.local/phase9/models/bge-small-en-v1.5`, using each exact URL:

```text
https://huggingface.co/BAAI/bge-small-en-v1.5/resolve/5c38ec7c405ec4b44b94cc5a9bb96e735b38267a/<manifest path>
```

The approved bounded transfer must stop if file bytes exceed the manifest size,
verify final byte count, verify the weight SHA-256 above, and retain the pinned
revision for non-LFS files. Model approval must explicitly include these transfers;
`from_pretrained(repository-name)` is forbidden. It must use only local files
with `local_files_only=True`, `use_safetensors=True`, `trust_remote_code=False`.
Force `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1`
for imports, runtime and tests. No network model initialization.

Hash-locked proposed package set (hashes from PyPI distribution metadata):

```requirements
annotated-doc==0.0.5 --hash=sha256:117bac03a25ede5df5440e855b32d556049ca169ead221505badf432fed4b101
anyio==4.15.1 --hash=sha256:6152fdbbf9a77fdec97731721bebf7c4c44f7c29b424b0065826173efc7ed101
click==8.5.0 --hash=sha256:255bc9599cf7748b4b1a446ccc735421bd08a2ae529a8b88597d3de5664ee360
filelock==4.2.0 --hash=sha256:2ff5690882e8cdb00ef31fb3d01a3094c29f30985426c59495afb1733f3b7238
fsspec==2026.9.0 --hash=sha256:8dd6e646e99ea382bd85f97a45e6b526a442d79423a7dc673f1e2756d05fcb5f
h11==0.16.0 --hash=sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86
hf-xet==1.7.0 --hash=sha256:59fba37039233c7fcbe196817d6cdcf1b40dfb17b410f229d85b0cf0a1848da4
httpcore2==2.13.1 --hash=sha256:e1e05d4f25f7d7d496bfb96748f6f4b67657b03da069b3a68c36069f3db73d0a
httpx2==2.13.1 --hash=sha256:6dff50fabc270ee5fd25d845d0b078ed20564579744d6d962850975996d2f9a4
huggingface-hub==2.2.0 --hash=sha256:1667f145dc56dc210d60966069397df9ecfca9607a5d43db88b308c89dae56b3
idna==3.20 --hash=sha256:ab7ae7122974553370f0bdb919e1a960b2cd1bc1ef0276416d896db81c14582c
jinja2==3.1.6 --hash=sha256:85ece4451f492d0c13c5dd7c13a64681a86afae63a5f347908daf103ce6d2f67
markdown-it-py==4.2.0 --hash=sha256:9f7ebbcd14fe59494226453aed97c1070d83f8d24b6fc3a3bcf9a38092641c4a
markupsafe==3.0.4 --hash=sha256:52704c5d36eb6dda8866493decd61111fff86244c9b1ad225ca01b9e91e5970f
mdurl==0.1.2 --hash=sha256:84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8
mpmath==1.3.0 --hash=sha256:a0b2b9fe80bbcd81a6647ff13108738cfb482d481d826cc0e02f5b35e5c88d2c
networkx==3.7 --hash=sha256:e3fd2c13a7814cee3746340d8d7f8598a67f16a58bf47fb7f8793fab6efca1b0
numpy==2.5.4 --hash=sha256:956555e0603a4d38019ae6925711cb9dc43195c076a928accf7ea5d50bddfe53
packaging==26.3 --hash=sha256:d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c
pygments==2.21.0 --hash=sha256:2363c69b61c4a97c838da3b130dcd6468f4848992b21a82f2a63ec34377137d9
pyyaml==6.0.3 --hash=sha256:34d5fcd24b8445fadc33f9cf348c1047101756fd760b4dacb5c3e99755703310
regex==2026.9.29 --hash=sha256:0166844493626c5015c6088ee15c9ca2fd060ca15b7641d1657da6a58432ae33
rich==15.0.0 --hash=sha256:33bd4ef74232fb73fe9279a257718407f169c09b78a87ad3d296f548e27de0bb
safetensors==0.8.0 --hash=sha256:c80201d22cbf405b80647a60ada77bba06c8fba2da2743ba1e89cdcc39a81f25
setuptools==84.0.0 --hash=sha256:51a52592b3b99e102b609654876bd65f19f999935166d1352678931132b0c670
shellingham==1.5.4 --hash=sha256:7ecfff8f2fd72616f7481040475a65b2bf8af90a56c89140852d1120324e8686
sympy==1.14.0 --hash=sha256:e091cc3e99d2141a0ba2847328f5479b05d94a6635cb96148ccb3f34671bd8f5
tokenizers==0.23.3 --hash=sha256:68649e97d5b43c44c031d8d848874a6eecae8f8fe40ea989aa777a5a83aca716
torch==2.14.1 --hash=sha256:cee091caf2a6229e248daf41d18ceebf590ba02d9179205610062c64ee5fef03
tqdm==4.70.1 --hash=sha256:c293e525e6fef9c20e8728fd4612df02a0aa31bb5fe91ecd93e123b1b7bffa73
transformers==5.20.0 --hash=sha256:5f4afd201f9ae5118b006513a0f647962b531de5592043e558a66d326378685b
truststore==0.10.5 --hash=sha256:9aaaedaefaf06d8b206278cf8b5012bc897f485a874503501e12d776df78951c
typer==0.27.3 --hash=sha256:e50022f28b82a86313e54501317a1db64bf8f8d036ff8cfe5ca7e47675454aff
typing-extensions==4.16.0 --hash=sha256:481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8
```

## C. Bounded first embedding load — separate explicit approval

Only after A/B approval, successful install/integrity checks and another resource
check: implement/review the minimal loopback CPU bridge, then request/confirm the
first load approval. Bind 127.0.0.1:11435, no arbitrary model/path/URL parameters,
32 KB request / 64 KB response bounds, one request slot and no waiting queue.
Expose /v1/models and /v1/embeddings only. First probe: **one controlled text,
batch=1, max 128 input tokens, 2 CPU threads, CPU float32, 384 dimensions,
8-second request deadline, no retries**. Model load gets one bounded 30-second
operator watchdog, with no automatic increase if exceeded. A cold request may fail
the existing eight-second adapter deadline; record failure honestly.

Use pinned tokenizer + AutoModel, model.eval()/torch.inference_mode(), the model
card's CLS pooling then L2 normalization. Test finite nonzero vectors, dimension,
model identity/fingerprint, repeated controlled request and invalid input. Do not
mistake pooler/classification output for the 384-dimensional CLS representation.
Connect the bridge through VersionedEmbedding/LocalProvider and the existing
private registry JSON (alias bge-small-en-v1.5, capabilities EMBED, pinned tensor
fingerprint, dimension 384, version matching revision, estimated_memory_mib=1024).
Do not put raw artifacts or private registry paths into Git or API inputs.

Then, only while resource gates still pass, use the existing explicit reindex
workflow with one owned bounded batch, preserving fixture vectors and namespace
provenance. Real evaluation uses the existing labels/thresholds without changing
historic fixture results. Dataset size is five positives and cannot establish
general semantic quality. Stop the task-owned bridge/process to unload BGE before
any Qwen load; confirm termination and memory/swap recovery. Do not delete caches,
model files or application volumes for rollback. A failed install stays isolated
and unused; any filesystem removal needs a separate deliberate cleanup action.

## D. Existing Qwen bounded activation — separate explicit approval

No Qwen download or new text runtime. Existing 986048512-byte artifact SHA-256:
`183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4`.
Cached Apache-2.0 metadata/license was inspected; artifact hash was checked again.
Use existing Ollama 0.35.1 only. BGE must be stopped, with fresh passing resource
measurements. Initial **CPU-only**, context **512**, output **32 tokens**,
temperature 0, concurrency 1, 2 threads, no tools or external messages. Expected
RSS planning range **1.2–2 GiB**, not verified; stop if 2048 MiB budget or global
swap gate is reached. If the required safe residency cannot be demonstrated,
record BLOCKED rather than raising the declaration.

Proposed task-owned local server, only after approval:

```sh
OLLAMA_HOST=127.0.0.1:11434 OLLAMA_NO_CLOUD=1 \
OLLAMA_MAX_LOADED_MODELS=1 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_QUEUE=1 \
OLLAMA_KEEP_ALIVE=0 ollama serve
```

Before first generation, register a **new task-owned metadata alias**
`nova-qwen-phase9` FROM qwen2.5:1.5b with num_ctx=512, num_predict=32,
num_thread=2, CPU-only num_gpu=0 and temperature=0. Approval must include this
small new alias metadata; original manifests/weight blobs are never edited or
redownloaded. Validate that the installed runtime accepts these options without
claiming support from documentation alone; refuse the probe if CPU/context bounds
cannot be established. Alias metadata disk impact estimated <1 MiB, no new weights.

Then use existing Phase 9 LOCAL_REAL structured-summary path, private artifact
binding and fresh attestation; one controlled request, max_output_tokens=32,
request deadline **8 seconds** and an operator hard-stop watchdog **15 seconds**.
Inspect exact model ID, fingerprint, measured wall time, reported tokens or UNKNOWN,
JSON validity and process RSS. No quality/agent/autonomy claim follows from one
response. HTTP cancellation alone is not proof the runtime unloaded its weights.

Finally, `ollama stop nova-qwen-phase9`, confirm no loaded model with `ollama ps`,
and terminate only the task-owned server if needed. Do not run `ollama rm`, pull,
prune or alter existing model artifacts. Keep any alias metadata until explicitly
reviewed for cleanup. API/native unload controls and environment behavior are
verified only when executed; this plan does not claim they already worked.

## E. Sequencing and remaining approvals

The current shared semaphore bounds **requests**, not resident models in separate
servers. Never leave embedding and Qwen models loaded simultaneously. Initial
approvals cover standalone probes only. Combined real-semantic RAG remains blocked
until explicit sequential unload/activation handoff is implemented and verified;
do not enable LOCAL_REAL HYBRID against two permanently resident model servers.
A lexical-only Qwen grounding probe can be reviewed separately after Qwen works.

Required approvals, independently selectable:

1. Download the exact BGE manifest and the exact 34 hash-locked wheels; create the
   isolated environment within the 3 GiB disk reservation. No model load included.
2. First BGE CPU load and bounded vector test, after integrity checks and recheck.
3. Start existing Ollama, create the small new alias and perform **one** Qwen load/
   generation under the limits above, with stop/unload in finally. No download.

No approval is assumed. Fresh attestation expires after one hour and must be
regenerated from new observations before execution. No runtime/model activation,
benchmark, real retrieval, paid service, commit or Phase 10 occurred in this task.

Sources: [PyTorch installation](https://pytorch.org/get-started/locally/),
[BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5),
[PyPI torch metadata](https://pypi.org/pypi/torch/2.14.1/json),
[PyPI Transformers metadata](https://pypi.org/pypi/transformers/5.20.0/json),
[Ollama environment implementation](https://github.com/ollama/ollama/blob/main/envconfig/config.go),
[Ollama FAQ](https://github.com/ollama/ollama/blob/main/docs/faq.mdx).
Package metadata/version constraints were read for all selected distributions;
compatibility is metadata-resolved and awaits actual isolated validation.
