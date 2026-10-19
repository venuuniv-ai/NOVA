# Phase 9 resource preflight — October 16, 2026

Read-only inspection: Apple M2 arm64, 8 GiB unified physical RAM; Metal 4 hardware
reported (8 GPU cores), not verified as an inference backend. macOS memory_pressure
reports 55% free under its own accounting; only about 62 MiB free pages, 4.0 GiB
active/inactive pages and 1.9 GiB compressed pages were observed, so this is not
4.4 GiB guaranteed allocatable RAM. Swap: 5149.56 MiB used of 6144 MiB. Data volume:
3.7 GiB free, 99% capacity. Docker: 4106604544 bytes memory, 8 CPUs. No allocation
change, cache deletion, model download or runtime install.

Installed host packages: mlx 0.32.3, pip 26.2.1, wheel 0.48.0. No host torch,
transformers or sentence-transformers. Ollama client 0.35.1 exists; version probe
reported no running instance. No llama-server/MLX-LM executable found. No runtime
was launched. Standard Hugging Face/LM Studio cache directories were absent.

Existing Ollama cache: about 940 MiB, qwen2.5:1.5b. Model layer 986048512 bytes,
digest 183715c435899236895da3869489cc30ac241476b4971a20285b1a462818a5b4.
Metadata: Qwen2.5 1.5B Instruct, GGUF type 15 (quantization interpretation not
verified), declared context 32768, Apache-2.0. Cached license text exists. The existing 986048512-byte model layer was SHA-256 verified read-only against
its manifest digest. This is not runtime validation. No embedding or
vision weights were found in these standard caches; other disks were not scanned.

Resource-safe recommendation: fixture development; zero incremental inference
dependency installation. Existing text-model execution estimated 1.5–3 GiB with
small context (planning estimate, not measured); it is BLOCKED by current swap
pressure and resource policy. Do not run it alongside the complete infrastructure.
Candidate embedding: BAAI/bge-small-en-v1.5, 33.4M parameters, MIT, 384 dimensions,
about 134 MB FP32 weights and roughly 0.3–1 GiB runtime estimate excluding any
framework install. These are estimates, not benchmark measurements. Proposed
future download is that model's safetensors/config/tokenizer from a pinned reviewed
revision of https://huggingface.co/BAAI/bge-small-en-v1.5 ; the exact revision/file sizes and weight SHA-256 are recorded in
phase-9-model-download-proposal.json for approval. No download command has been executed.
Source: https://huggingface.co/BAAI/bge-small-en-v1.5 and
https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct .

Gate: local real inference requires at least 5 GiB free disk, swap below 2 GiB,
operator-declared memory <= 2048 MiB, explicit resource approval and configured
artifact identity. These are conservative application policy thresholds, not
model-vendor minima. Present result: BLOCKED_BY_RESOURCES. No real LLM, embedding,
vision or judge execution is claimed. Model download approval remains outstanding.
