from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import and_, or_, select

from app.database import SessionLocal
from app.inference.contracts import GroundedOutput, GroundedSelection
from app.inference.grounding import select_context, supports
from app.inference.models import EmbeddingVersion, InferenceModel, InferenceRun, ReindexJob
from app.inference.providers import selected, strict_registry
from app.inference.registry import inventory
from app.memory.contracts import EmbeddingRequest, MemoryQuery
from app.memory.models import MemoryEmbedding, MemoryRecord
from app.memory.service import MemoryService, digest
from app.model_routing.contracts import ModelRequest
from app.model_routing.service import ModelRoutingService
from app.models import Device, User
from app.security.identity import current_user_id
from app.service import fail, find_task


def safe_failure(error):
    if isinstance(error, HTTPException):
        return error.detail.get("code", "INFERENCE_FAILED")
    return "INFERENCE_FAILED"


def model_inventory():
    snapshot = inventory()
    with SessionLocal.begin() as session:
        for item in snapshot["models"]:
            row = session.get(InferenceModel, item["model_id"])
            if row is None:
                session.add(InferenceModel(id=item["model_id"], metadata_snapshot=item))
            else:
                row.metadata_snapshot, row.updated_at = item, datetime.now(UTC)
    return snapshot


def conflict(evidence):
    facts = {}
    for x in evidence:
        if x["kind"] != "MEMORY":
            continue
        key = (x["subject"], x["predicate"])
        facts.setdefault(key, set()).add(x["text"])
    return any(len(v) > 1 for v in facts.values())


def verified_output(raw, evidence, query=None):
    result = GroundedOutput.model_validate(raw)
    allowed = {}
    for item in evidence:
        key = str(item["id"])
        if result.claims and key in allowed and allowed[key] != item["text"]:
            fail(409, "UNSUPPORTED_CITATION", "Ambiguous source UUID in evidence.")
        allowed[key] = item["text"]
    for claim in result.claims:
        # Deliberately extractive: valid citation alone does not establish entailment.
        if allowed.get(str(claim.evidence_id)) != claim.quote:
            fail(409, "UNSUPPORTED_CITATION", "Citation/quote not in the authorized evidence set.")
        if query is not None and not any(
            str(item["id"]) == str(claim.evidence_id)
            and item["text"] == claim.quote
            and supports(query, item)
            for item in evidence
        ):
            fail(409, "UNSUPPORTED_CLAIM", "Claim outside the deterministic support contract.")
    if conflict(evidence) and not result.abstain:
        fail(409, "CONFLICTING_EVIDENCE", "Conflicting evidence requires abstention.")
    return result


def verified_selection(raw, evidence, query):
    result = GroundedSelection.model_validate(raw, strict=True)
    if result.abstain:
        return verified_output({"abstain": True, "claims": []}, evidence, query), None
    index = result.evidence_index
    if index >= len(evidence):
        fail(409, "UNSUPPORTED_CITATION", "Selection outside the supplied evidence set.")
    source = evidence[index]
    if not supports(query, source) or result.answer != source.get("value"):
        fail(409, "UNSUPPORTED_CLAIM", "Answer does not match the supported relationship.")
    # Attach existing source metadata only after independently checking the model's
    # selected item AND exact answer value. This is application-derived citation,
    # never a claim that the model emitted a UUID or copied the full source quote.
    grounded = verified_output(
        {"abstain": False, "claims": [{"evidence_id": source["id"], "quote": source["text"]}]},
        evidence,
        query,
    )
    return grounded, result.answer


def grounding_context(query, evidence, mode, output_tokens=96, selection=False):
    # Conflict checks cover the entire retrieved set before selecting bounded context.
    if conflict(evidence):
        return evidence, {"query": query, "evidence": []}
    if mode == "LOCAL_REAL":
        return select_context(query, evidence, output_tokens, selection=selection)
    return evidence, {"query": query, "evidence": evidence}


def gather(task_id, query, strategy, provider):
    retrieval = MemoryService(provider=provider).search(
        MemoryQuery(task_id=task_id, query=query, retrieval_strategy=strategy, limit=8)
    )
    evidence = [
        {
            "id": str(h.memory_id),
            "text": h.memory.normalized_text,
            "subject": h.memory.subject,
            "predicate": h.memory.predicate,
            "value": h.memory.value,
            "kind": "MEMORY",
            "origin": h.memory.origin,
            "binding": memory_binding(h.memory),
            "retrieval_provenance": h.model_dump(mode="json", exclude={"memory"}),
            "retrieved_at": datetime.now(UTC).isoformat(),
        }
        for h in retrieval.hits
    ]
    with SessionLocal() as session:
        for observation, run, media, processor in session.execute(
            visual_sources(task_id).limit(4)
        ).all():
            evidence.append(
                {
                    "id": str(observation.id),
                    "text": observation.output["description"],
                    "kind": "VISUAL",
                    "media_id": str(media.id),
                    "simulation": run.simulation,
                    "provenance": observation.output.get("model"),
                    "binding": visual_binding(observation, run, media, processor),
                    "retrieved_at": datetime.now(UTC).isoformat(),
                }
            )
    return retrieval, evidence


def run(payload, correlation):
    user = current_user_id()
    signature = digest(payload.model_dump(mode="json", exclude={"request_id"}))
    with SessionLocal.begin() as session:
        session.scalar(select(User.id).where(User.id == user).with_for_update())
        task = find_task(session, payload.task_id)
        device = session.get(Device, task.current_device_id).type
        prior = session.scalar(
            select(InferenceRun).where(
                InferenceRun.user_id == user, InferenceRun.request_id == payload.request_id
            )
        )
        if prior:
            if prior.request_hash != signature:
                fail(409, "IDEMPOTENCY_CONFLICT", "Inference key has different intent.")
            return {
                "id": str(prior.id),
                **prior.metadata_snapshot,
                "state": prior.state,
                "replayed": True,
                "output": None,
            }
        row = InferenceRun(
            id=uuid4(),
            user_id=user,
            task_id=task.id,
            request_id=payload.request_id,
            request_hash=signature,
            state="RUNNING",
            metadata_snapshot={"mode": payload.mode, "operation": payload.operation},
        )
        session.add(row)
        run_id = row.id
    meta = {
        "mode": payload.mode,
        "operation": payload.operation,
        "benchmark": payload.benchmark_label,
        "simulation": payload.mode == "FIXTURE",
        "error": None,
        "output_retained": False,
        "trace_id": str(payload.request_id),
    }
    output = None
    try:
        if payload.operation == "VISION":
            from app.perception.contracts import PerceptionRequest
            from app.perception.service import PerceptionOrchestrator

            provider = selected(payload.mode, "VISION")
            meta.update(provider.config.public())
            if not payload.media_id:
                fail(422, "MEDIA_REQUIRED", "Owned media required.")
            result = PerceptionOrchestrator(
                providers=[], router=ModelRoutingService(providers=strict_registry(provider))
            ).run(
                payload.task_id,
                PerceptionRequest(
                    media_id=payload.media_id,
                    idempotency_key=str(payload.request_id),
                    processors=[],
                    allow_fixture=False,
                ),
                correlation,
            )
            return finish_vision(run_id, meta, result)
        provider = selected(payload.mode, "EMBED" if payload.operation == "EMBED" else "STRUCTURED")
        model_config = getattr(provider, "config", None) or getattr(
            getattr(provider, "local", None), "config", None
        )
        if model_config:
            meta.update(model_config.public())
        if payload.operation == "EMBED":
            result = provider.embed(EmbeddingRequest(text=payload.query, privacy_class="PERSONAL"))
            output = {
                "dimension": result.dimension,
                "namespace": result.model,
                "simulation": result.simulation,
            }
            meta.update(output)
            meta["latency_ms"] = result.latency_ms
        else:
            evidence = []
            purpose = "SUMMARY"
            context = {"query": payload.query}
            if payload.operation == "RAG":
                # Explicit real generation may use lexical retrieval without an embedding model.
                embedder = (
                    selected("FIXTURE", "EMBED")
                    if payload.retrieval == "LEXICAL"
                    else selected(payload.mode, "EMBED")
                )
                retrieval, evidence = gather(
                    payload.task_id, payload.query, payload.retrieval, embedder
                )
                purpose = "GROUNDED"
                selection = (
                    payload.mode == "LOCAL_REAL"
                    and getattr(model_config, "grounded_generation_contract", None)
                    == "SELECTION_V1"
                )
                if selection:
                    purpose = "GROUNDED_SELECTION"
                    meta["grounding_contract"] = "SELECTION_V1"
                retrieved_evidence = evidence
                evidence, context = grounding_context(
                    payload.query,
                    evidence,
                    payload.mode,
                    payload.max_output_tokens,
                    selection=selection,
                )
                meta["retrieval_id"] = str(retrieval.id)
            request = ModelRequest(
                request_id=payload.request_id,
                task_id=payload.task_id,
                user_id=user,
                trace_id=payload.request_id,
                purpose=purpose,
                structured_input=context,
                required_capabilities=["STRUCTURED"],
                privacy_class="PERSONAL",
                current_device=device,
                max_output_tokens=payload.max_output_tokens,
            )
            response = ModelRoutingService(providers=strict_registry(provider)).run(
                request, correlation
            )
            if response.status != "DONE" or response.output is None:
                from app.model_routing.diagnostics import safe_diagnostic
                from app.model_routing.models import ModelCall

                with SessionLocal() as session:
                    call = session.scalar(
                        select(ModelCall).where(
                            ModelCall.user_id == user,
                            ModelCall.task_id == payload.task_id,
                            ModelCall.request_id == payload.request_id,
                        )
                    )
                    if call:
                        detail = next(
                            (
                                item.get("diagnostic")
                                for item in reversed(call.attempts)
                                if item.get("diagnostic")
                            ),
                            None,
                        )
                        if detail:
                            meta["diagnostic"] = safe_diagnostic(detail)
                fail(
                    409,
                    response.safe_error or "INFERENCE_FAILED",
                    "Inference did not produce a validated result.",
                )
            output = response.output
            meta.update(
                {
                    "model": response.model,
                    "latency_ms": response.latency_ms,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "usage_source": response.usage_source,
                    "fallback_used": response.fallback_used,
                }
            )
            if purpose in {"GROUNDED", "GROUNDED_SELECTION"}:
                import time

                validation_started = time.perf_counter()
                # Serialize cooperative memory mutations through final acceptance,
                # rather than releasing the owner lock before marking the run DONE.
                with SessionLocal.begin() as session:
                    session.scalar(select(User.id).where(User.id == user).with_for_update())
                    find_task(session, payload.task_id)
                    fresh_conflict = revalidate_evidence(
                        retrieved_evidence, payload.task_id, session=session
                    )
                    fresh_conflict |= revalidate_evidence(
                        evidence, payload.task_id, session=session
                    )
                    if fresh_conflict and not output.get("abstain"):
                        fail(409, "CONFLICTING_EVIDENCE", "Current facts require abstention.")
                    model_answer = None
                    if purpose == "GROUNDED_SELECTION":
                        answer, model_answer = verified_selection(output, evidence, payload.query)
                        meta["citation_origin"] = "APPLICATION_VERIFIED_SELECTION"
                    else:
                        answer = verified_output(
                            output,
                            evidence,
                            query=payload.query if payload.mode == "LOCAL_REAL" else None,
                        )
                    meta["validation_latency_ms"] = round(
                        (time.perf_counter() - validation_started) * 1000, 3
                    )
                    output = {
                        **answer.model_dump(mode="json"),
                        "answer": " ".join(x.quote for x in answer.claims),
                        "boundary": "EXTRACTIVE CITATION CHECK / NOT GENERAL FACTUALITY",
                    }
                    if purpose == "GROUNDED_SELECTION":
                        output["response"] = model_answer
                    meta["citation_ids"] = [str(x.evidence_id) for x in answer.claims]
                    meta["abstain"] = answer.abstain
                    row = session.get(InferenceRun, run_id)
                    row.state, row.metadata_snapshot = "DONE", meta
                return {
                    "id": str(run_id),
                    "state": "DONE",
                    **meta,
                    "output": output,
                    "replayed": False,
                }
        state = "DONE"
    except Exception as error:
        output = None
        state, meta["error"] = "FAILED", safe_failure(error)
    with SessionLocal.begin() as session:
        row = session.get(InferenceRun, run_id)
        row.state, row.metadata_snapshot = state, meta
    return {"id": str(run_id), "state": state, **meta, "output": output, "replayed": False}


def read_run(id):
    with SessionLocal() as session:
        row = session.get(InferenceRun, id)
        if not row or row.user_id != current_user_id():
            fail(404, "INFERENCE_NOT_FOUND", "Run not found.")
        return {"id": str(row.id), "state": row.state, **row.metadata_snapshot}


def version(provider):
    config = getattr(getattr(provider, "local", None), "config", None)
    return dict(
        namespace=provider.model,
        model_id=config.model_id if config else provider.model,
        fingerprint=config.fingerprint if config else digest("fixture-token-hash-v1"),
        version=config.version if config else "1",
        dimension=provider.dimension,
        simulation=provider.simulation,
    )


def eligible(user, task):
    now = datetime.now(UTC)
    return select(MemoryRecord).where(
        MemoryRecord.user_id == user,
        MemoryRecord.status == "ACTIVE",
        MemoryRecord.privacy_class.in_(["INTERNAL", "PERSONAL"]),
        or_(
            MemoryRecord.scope == "USER",
            and_(MemoryRecord.scope == "TASK", MemoryRecord.task_id == task),
        ),
        or_(MemoryRecord.valid_from.is_(None), MemoryRecord.valid_from <= now),
        or_(MemoryRecord.valid_until.is_(None), MemoryRecord.valid_until > now),
    )


def create_reindex(payload):
    provider = selected(payload.mode, "EMBED")
    config = version(provider)
    signature = digest([payload.model_dump(mode="json", exclude={"request_id"}), config])
    with SessionLocal.begin() as session:
        user = current_user_id()
        session.scalar(select(User.id).where(User.id == user).with_for_update())
        find_task(session, payload.task_id)
        old = session.scalar(
            select(ReindexJob).where(
                ReindexJob.user_id == user, ReindexJob.request_id == payload.request_id
            )
        )
        if old:
            if old.request_hash != signature:
                fail(409, "IDEMPOTENCY_CONFLICT", "Reindex intent changed.")
            return job_read(old)
        existing = session.get(EmbeddingVersion, provider.model)
        if existing is None:
            session.add(EmbeddingVersion(**config))
            session.flush()
        elif any(getattr(existing, k) != v for k, v in config.items()):
            fail(409, "NAMESPACE_CONFLICT", "Embedding version changed.")
        last = session.scalar(eligible(user, payload.task_id).order_by(MemoryRecord.id.desc()))
        job = ReindexJob(
            id=uuid4(),
            user_id=user,
            task_id=payload.task_id,
            request_id=payload.request_id,
            request_hash=signature,
            namespace=provider.model,
            mode=payload.mode,
            state="READY",
            upper_bound=last.id if last else None,
            processed=0,
        )
        session.add(job)
        return job_read(job)


def job_read(job):
    return {
        k: str(v) if k in {"id", "cursor"} and v else v
        for k, v in {
            "id": job.id,
            "cursor": job.cursor,
            "namespace": job.namespace,
            "state": job.state,
            "processed": job.processed,
            "error": job.error,
        }.items()
    }


def _step_reindex(id):
    with SessionLocal.begin() as session:
        user = current_user_id()
        session.scalar(select(User.id).where(User.id == user).with_for_update())
        job = session.scalar(
            select(ReindexJob)
            .where(ReindexJob.id == id, ReindexJob.user_id == user)
            .with_for_update()
        )
        if not job:
            fail(404, "REINDEX_NOT_FOUND", "Job not found.")
        if job.state == "DONE":
            return job_read(job)
        provider = selected(job.mode, "EMBED")
        if provider.model != job.namespace:
            fail(409, "NAMESPACE_CONFLICT", "Resume requires original model version.")
        query = (
            eligible(user, job.task_id).where(MemoryRecord.id <= job.upper_bound)
            if job.upper_bound
            else None
        )
        if query is not None and job.cursor:
            query = query.where(MemoryRecord.id > job.cursor)
        rows = (
            session.scalars(query.order_by(MemoryRecord.id).limit(10)).all()
            if query is not None
            else []
        )
        service = MemoryService(provider=provider)
        for memory in rows:
            exists = session.scalar(
                select(MemoryEmbedding.id).where(
                    MemoryEmbedding.memory_id == memory.id,
                    MemoryEmbedding.model == provider.model,
                    MemoryEmbedding.provider == provider.provider,
                    MemoryEmbedding.dimension == provider.dimension,
                )
            )
            if not exists:
                service.embedding(session, memory)
            job.cursor, job.processed = memory.id, job.processed + 1
        job.state, job.error = ("DONE" if len(rows) < 10 else "READY"), None
        return job_read(job)


def recover():
    with SessionLocal.begin() as session:
        for row in session.scalars(select(InferenceRun).where(InferenceRun.state == "RUNNING")):
            row.state = "FAILED"
            row.metadata_snapshot = {**row.metadata_snapshot, "error": "APPLICATION_RESTARTED"}
    # Reindex cursor/vector writes share each batch transaction; READY jobs resume explicitly.


def step_reindex(id):
    try:
        return _step_reindex(id)
    except Exception as error:
        with SessionLocal.begin() as session:
            job = session.scalar(
                select(ReindexJob)
                .where(ReindexJob.id == id, ReindexJob.user_id == current_user_id())
                .with_for_update()
            )
            if job:
                job.state, job.error = "FAILED", safe_failure(error)
        raise


def finish_vision(run_id, meta, result):
    state = "DONE" if result.status == "DONE" else "FAILED"
    meta.update({"perception_id": str(result.id), "simulation": result.simulation})
    with SessionLocal.begin() as session:
        row = session.get(InferenceRun, run_id)
        row.state, row.metadata_snapshot = state, meta
    return {"id": str(run_id), "state": state, **meta, "output": result.model_dump(mode="json")}


def memory_binding(memory):
    return digest(
        {
            key: getattr(memory, key)
            for key in (
                "id",
                "user_id",
                "task_id",
                "subject",
                "predicate",
                "value",
                "normalized_text",
                "scope",
                "privacy_class",
                "status",
                "valid_from",
                "valid_until",
                "updated_at",
                "origin",
                "source_reference",
                "confirmed",
                "explicitness",
            )
        }
    )


def visual_sources(task_id):
    from app.perception.models import MediaAsset, PerceptionRun, ProcessorRun, VisualObservation

    return (
        select(VisualObservation, PerceptionRun, MediaAsset, ProcessorRun)
        .join(PerceptionRun, VisualObservation.perception_run_id == PerceptionRun.id)
        .join(MediaAsset, PerceptionRun.media_id == MediaAsset.id)
        .join(ProcessorRun, VisualObservation.processor_run_id == ProcessorRun.id)
        .where(
            PerceptionRun.task_id == task_id,
            MediaAsset.task_id == task_id,
            MediaAsset.user_id == current_user_id(),
            PerceptionRun.privacy_class.in_(["INTERNAL", "PERSONAL"]),
            PerceptionRun.status.in_(["DONE", "PARTIAL"]),
            ProcessorRun.perception_run_id == PerceptionRun.id,
            ProcessorRun.status == "DONE",
        )
        .order_by(VisualObservation.created_at.desc())
    )


def visual_binding(observation, run, media, processor):
    return digest(
        [
            str(observation.id),
            observation.output,
            str(observation.perception_run_id),
            str(observation.processor_run_id),
            str(media.id),
            str(media.user_id),
            str(media.task_id),
            media.sha256,
            run.status,
            run.privacy_class,
            str(run.task_id),
            run.simulation,
            processor.status,
            processor.model,
            processor.simulation,
        ]
    )


def revalidate_evidence(evidence, task_id, session=None):
    if session is None:
        with SessionLocal.begin() as owned_session:
            owned_session.scalar(
                select(User.id).where(User.id == current_user_id()).with_for_update()
            )
            find_task(owned_session, task_id)
            return revalidate_evidence(evidence, task_id, session=owned_session)
    # Caller holds the existing owner mutation lock through terminal run commit.
    memories = [x for x in evidence if x["kind"] == "MEMORY"]
    ids = [x["id"] for x in memories]
    current = {
        str(m.id): m
        for m in session.scalars(
            eligible(current_user_id(), task_id).where(MemoryRecord.id.in_(ids)).with_for_update()
        )
    }
    for item in memories:
        memory = current.get(str(item["id"]))
        if memory is None or any(
            item[key] != value
            for key, value in {
                "text": memory.normalized_text if memory else None,
                "subject": memory.subject if memory else None,
                "predicate": memory.predicate if memory else None,
                "value": memory.value if memory else None,
                "binding": memory_binding(memory) if memory else None,
            }.items()
            if key in item
        ):
            fail(409, "EVIDENCE_CHANGED", "Memory source or eligibility changed; retrieve again.")
    visual = [x for x in evidence if x["kind"] == "VISUAL"]
    if visual:
        from app.perception.models import VisualObservation

        rows = session.execute(
            visual_sources(task_id)
            .where(VisualObservation.id.in_([x["id"] for x in visual]))
            .with_for_update()
        ).all()
        available = {str(o.id): (o, r, m, p) for o, r, m, p in rows}
        for item in visual:
            source = available.get(str(item["id"]))
            if (
                source is None
                or item.get("binding") != visual_binding(*source)
                or item["text"] != source[0].output.get("description")
            ):
                fail(409, "EVIDENCE_CHANGED", "Visual source or eligibility changed.")
    # Recheck facts inserted/changed during generation, including records absent
    # from the original top-K retrieval. The owner lock serializes normal writes.
    keys = {(m.subject, m.predicate) for m in current.values()}
    if not keys:
        return False
    rows = session.scalars(
        eligible(current_user_id(), task_id)
        .where(
            or_(*(and_(MemoryRecord.subject == s, MemoryRecord.predicate == p) for s, p in keys))
        )
        .with_for_update()
    ).all()
    facts = {}
    for memory in rows:
        facts.setdefault((memory.subject, memory.predicate), set()).add(memory.normalized_text)
    return any(len(texts) > 1 for texts in facts.values())
