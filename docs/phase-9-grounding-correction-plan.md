# Phase 9 grounding correction plan — offline scope

October 19, 2026. No model activation is authorized. Preserve all existing work.

1. Confirmed bugs: decode_local_result masks ProviderFailure as USAGE_INVALID;
   selected-source content and visual lifecycle are not revalidated; privacy
   validation commits before final run acceptance; visual gathering lacks run
   privacy/status checks. Fix these with bounded diagnostics and transactional
   source validation, preserving the existing owner mutation lock.
2. Demonstrated limitations: LOCAL_REAL selects the first hit regardless of its
   structured subject/predicate, exact citations do not prove general entailment,
   and the user-byte exposure gate omits system/framing/output reservation.
3. Implement a deliberately narrow support contract for named-subject cuisine/
   beverage preference questions and their conjunction. Match structured metadata,
   never a similarity score; arbitrary/first-person/visual questions are outside
   this independently verifiable subset and receive no asserted supporting context.
   Retain full retrieved-set conflict refusal and provenance. Multiple small
   supporting records may fit; never truncate text or fill with unrelated records.
4. Add an explicit private pinned Qwen/ChatML budget declaration. Verify artifact,
   unchanged prompt fingerprint and bounded output; reserve a conservative system/
   framing margin plus serialized-user-byte upper bound and output tokens. Refuse
   unknown profiles or overflow before inference. No context/resource increase.
5. Revalidate all retrieved and sent evidence, exact content and bindings, plus
   current relevant conflicts under the owner lock through terminal run acceptance.
   Visual rows require valid owner/task/media/run/processor joins and privacy.
6. Defer prompt rewriting, freeform semantic entailment and answer/schema changes:
   neither 9G nor 9I-F proves a justified prompt fix. Keep the existing extractive
   GroundedOutput and model abstention. Do not claim this subset is general RAG.
7. Add deterministic provider, selection, support, lifecycle/race and visual tests;
   run offline full backend/controller/lint checks sequentially. Prepare conditional
   authenticated positive/insufficiency acceptance and a staging manifest only.
   Stop for fresh real-model approval. Final cross-stack qualification remains
   deferred until separately approved real acceptance passes.
