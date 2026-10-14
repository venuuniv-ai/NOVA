# ADR 0006: visual evidence has provenance and no authority

Accepted for Phase 5 local/fixture scope.

Keep raw media, processor output, structured observations, context interpretation,
agent reasoning and action policy distinct. CLIP compares image/text representations;
DINOv2 supplies features; SAM supplies masks; a VLM interprets. None authorizes
an action, declares physical truth, writes personal memory or grants new tools.

Every observation retains source media/hash, processor/model, simulation, device,
time and independent score_type. Never average unrelated scores. Fixtures are
restricted to controlled scene media and never claim real CLIP/DINO/SAM execution.
Typed validation and processor identity checks reject forged provenance.

Use the existing ModelRouter for VISION, and the existing Context/Planner/Critic
path for bounded contextual evidence. Preserve Phase 3 approval and canonical
payload hashes; image prose cannot justify sending or bypass human decisions.
No image bytes go to cloud in Phase 5. Real visual adapters are opt-in local-only.

Rejected: universal confidence, semantic labels from embeddings/masks alone,
image prompt instructions, automatic visual memory, decorative model activity.
See [architecture](../phase-5-architecture.md).
