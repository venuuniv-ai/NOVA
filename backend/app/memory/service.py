import hashlib
import json
import logging
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, uuid4, uuid5

from sqlalchemy import and_, func, or_, select

from app.database import SessionLocal
from app.memory.contracts import (
    EmbeddingRequest,
    MemoryCandidate,
    MemoryHit,
    MemoryInput,
    MemoryQuery,
    MemoryRead,
    RetrievalResult,
)
from app.memory.embeddings import FixtureEmbeddingProvider, embedding_provider
from app.memory.models import (
    MemoryAudit,
    MemoryEmbedding,
    MemoryMutation,
    MemoryRecord,
    MemoryRetrieval,
)
from app.memory.policy import MemoryPolicy
from app.models import Task, User
from app.seed import DEMO_USER_ID
from app.service import fail

logger = logging.getLogger("nova.memory")
PRIVACY = ["INTERNAL", "PERSONAL", "SENSITIVE_LOCAL_ONLY"]


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def canonical(subject, predicate, value, scope, task_id, kind, privacy, valid_from, valid_until):
    return digest(
        [
            subject.casefold().strip(),
            predicate,
            " ".join(value.casefold().split()),
            scope,
            str(task_id),
            kind,
            privacy,
            str(valid_from),
            str(valid_until),
        ]
    )


class MemoryService:
    def __init__(self, user_id=DEMO_USER_ID, provider=None, clock=None):
        self.user_id = user_id
        self.provider = provider or embedding_provider()
        self.clock = clock or (lambda: datetime.now(UTC))
        self.policy = MemoryPolicy()

    def owned_task(self, session, task_id):
        if task_id and not session.scalar(
            select(Task.id).where(Task.id == task_id, Task.user_id == self.user_id)
        ):
            fail(404, "TASK_NOT_FOUND", "Task was not found.")

    def owned(self, session, id):
        memory = session.scalar(
            select(MemoryRecord)
            .where(MemoryRecord.id == id, MemoryRecord.user_id == self.user_id)
            .with_for_update()
        )
        if not memory:
            fail(404, "MEMORY_NOT_FOUND", "Memory was not found.")
        return memory

    def audit(self, session, memory, event, trace):
        session.add(
            MemoryAudit(
                user_id=self.user_id,
                memory_id=memory.id,
                event_type=event,
                trace_id=trace,
                safe_metadata={
                    "status": memory.status,
                    "origin": memory.origin,
                    "scope": memory.scope,
                },
            )
        )
        logger.info(event, extra={"memory_id": str(memory.id), "trace_id": str(trace)})

    def expire(self, session):
        for m in session.scalars(
            select(MemoryRecord)
            .where(
                MemoryRecord.user_id == self.user_id,
                MemoryRecord.status.in_(["ACTIVE", "PENDING_CONFIRMATION"]),
                MemoryRecord.valid_until <= self.clock(),
            )
            .with_for_update()
        ):
            m.status = "EXPIRED"
            m.updated_at = self.clock()
            self.audit(session, m, "MEMORY_EXPIRED", uuid4())

    def embed(self, text, privacy):
        from app.memory.contracts import EmbeddingResult

        try:
            result = self.provider.embed(EmbeddingRequest(text=text, privacy_class=privacy))
            result = EmbeddingResult.model_validate(result)
        except Exception:
            fail(409, "EMBEDDING_UNAVAILABLE", "Configured local embedding could not be validated.")
        if (result.provider, result.model, result.dimension, result.simulation) != (
            self.provider.provider,
            self.provider.model,
            self.provider.dimension,
            self.provider.simulation,
        ):
            fail(
                409,
                "EMBEDDING_NAMESPACE_INVALID",
                "Embedding namespace differs from configuration.",
            )
        return result

    def embedding(self, session, memory):
        if memory.status != "ACTIVE":
            return
        result = self.embed(memory.normalized_text, memory.privacy_class)
        if (result.provider, result.model, result.dimension, result.simulation) != (
            self.provider.provider,
            self.provider.model,
            self.provider.dimension,
            self.provider.simulation,
        ):
            fail(
                409,
                "EMBEDDING_NAMESPACE_INVALID",
                "Embedding namespace differs from configured provider.",
            )
        session.add(
            MemoryEmbedding(
                memory_id=memory.id,
                provider=result.provider,
                model=result.model,
                dimension=result.dimension,
                embedding=result.vector,
                simulation=result.simulation,
            )
        )

    def conflict(self, session, data, exclude=None):
        return session.scalar(
            select(MemoryRecord).where(
                MemoryRecord.user_id == self.user_id,
                MemoryRecord.status == "ACTIVE",
                MemoryRecord.subject == data.subject.casefold(),
                MemoryRecord.predicate == data.predicate,
                MemoryRecord.scope == data.scope,
                MemoryRecord.task_id == data.task_id,
                MemoryRecord.value != data.value,
                MemoryRecord.id != exclude if exclude else True,
            )
        )

    def new_record(
        self,
        session,
        data,
        origin,
        reference,
        confidence=None,
        supersedes=None,
        confirmed=False,
        record_id=None,
    ):
        if data.privacy_class == "INTERNAL":
            data = data.model_copy(update={"privacy_class": "PERSONAL"})
        text = f"{data.subject.casefold()} {data.predicate}: {data.value}"
        decision, reason = self.policy.decide(
            origin,
            data.memory_type,
            data.scope,
            text,
            confidence,
            bool(self.conflict(session, data, supersedes)),
        )
        hashed = canonical(
            data.subject,
            data.predicate,
            data.value,
            data.scope,
            data.task_id,
            data.memory_type,
            data.privacy_class,
            data.valid_from,
            data.valid_until,
        )
        duplicate = session.scalar(
            select(MemoryRecord).where(
                MemoryRecord.user_id == self.user_id,
                MemoryRecord.canonical_hash == hashed,
                MemoryRecord.status.in_(["ACTIVE", "PENDING_CONFIRMATION"]),
                MemoryRecord.origin == origin,
            )
        )
        if duplicate:
            return duplicate
        memory = MemoryRecord(
            id=record_id or uuid4(),
            user_id=self.user_id,
            task_id=data.task_id,
            memory_type=data.memory_type,
            subject=data.subject.casefold(),
            predicate=data.predicate,
            value="[Rejected by memory policy]" if decision == "REJECT" else data.value,
            normalized_text="[Rejected by memory policy]" if decision == "REJECT" else text,
            canonical_hash=hashed,
            origin=origin,
            explicitness="EXPLICIT"
            if origin in {"USER_EXPLICIT", "USER_CORRECTION"}
            else "FIXTURE"
            if origin == "FIXTURE"
            else "INFERRED",
            confirmed=confirmed,
            confidence=confidence,
            status="REJECTED"
            if decision == "REJECT"
            else "PENDING_CONFIRMATION"
            if decision == "ASK_CONFIRMATION"
            else "ACTIVE",
            scope=data.scope,
            privacy_class=data.privacy_class,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
            source_reference=reference,
            supersedes_id=supersedes,
            policy_decision=decision,
            policy_reason=reason,
        )
        session.add(memory)
        session.flush()
        if confirmed and decision != "REJECT":
            memory.status = "ACTIVE"
            memory.policy_decision = "TASK_ONLY" if data.scope == "TASK" else "STORE"
            memory.policy_reason = "HUMAN_CONFIRMED_INFERENCE"
        self.embedding(session, memory)
        self.audit(session, memory, "MEMORY_CREATED", uuid4())
        return memory

    def mutate(self, operation, key, payload, id=None):
        request_hash = digest(
            {"operation": operation, "id": str(id), "payload": payload.model_dump(mode="json")}
        )
        with SessionLocal.begin() as session:
            # Serialize owned lifecycle changes and contradiction checks; no LLM chooses truth.
            if not session.scalar(select(User.id).where(User.id == self.user_id).with_for_update()):
                fail(404, "USER_NOT_FOUND", "User was not found.")
            prior = session.scalar(
                select(MemoryMutation).where(
                    MemoryMutation.user_id == self.user_id, MemoryMutation.idempotency_key == key
                )
            )
            if prior:
                if prior.request_hash != request_hash:
                    fail(409, "IDEMPOTENCY_CONFLICT", "Memory key belongs to another request.")
                return prior.response
            self.expire(session)
            if operation == "create":
                self.owned_task(session, payload.task_id)
                memory = self.new_record(session, payload, "USER_EXPLICIT", f"statement:{uuid4()}")
            elif operation == "visual":
                from app.perception.models import MediaAsset, PerceptionRun, VisualObservation

                self.owned_task(session, payload.task_id)
                source = session.execute(
                    select(VisualObservation, PerceptionRun, MediaAsset)
                    .join(PerceptionRun, VisualObservation.perception_run_id == PerceptionRun.id)
                    .join(MediaAsset, PerceptionRun.media_id == MediaAsset.id)
                    .where(
                        VisualObservation.id == payload.observation_id,
                        PerceptionRun.task_id == payload.task_id,
                        MediaAsset.user_id == self.user_id,
                    )
                ).first()
                if not source:
                    fail(404, "OBSERVATION_NOT_FOUND", "Observation was not found.")
                observation, run, media = source
                if observation.output.get("label") != "coffee_cup_present":
                    fail(
                        422,
                        "CANDIDATE_UNSUPPORTED",
                        "Only the controlled coffee candidate is supported.",
                    )
                data = MemoryInput(
                    idempotency_key=key,
                    value="Possible coffee-related preference",
                    predicate="preferred_beverage",
                    privacy_class=run.privacy_class,
                )
                memory = self.new_record(
                    session,
                    data,
                    "VISUAL_OBSERVATION",
                    f"observation:{observation.id}/trace:{run.trace_id}",
                    0.35,
                )
            elif operation == "candidate":
                candidate = MemoryCandidate.model_validate(payload)
                self.owned_task(session, candidate.task_id)
                from app.intelligence.models import AgentRun
                from app.models import TaskEvent
                from app.perception.models import PerceptionRun, VisualObservation

                if candidate.origin == "AGENT_INFERRED":
                    valid_source = session.scalar(
                        select(AgentRun.id).where(
                            AgentRun.id == candidate.source_reference,
                            AgentRun.task_id == candidate.task_id,
                        )
                    )
                elif candidate.origin == "TASK_OUTCOME":
                    valid_source = session.scalar(
                        select(TaskEvent.id).where(
                            TaskEvent.id == candidate.source_reference,
                            TaskEvent.task_id == candidate.task_id,
                        )
                    )
                else:
                    valid_source = session.scalar(
                        select(VisualObservation.id)
                        .join(
                            PerceptionRun, VisualObservation.perception_run_id == PerceptionRun.id
                        )
                        .where(
                            VisualObservation.id == candidate.source_reference,
                            PerceptionRun.task_id == candidate.task_id,
                        )
                    )
                if not valid_source:
                    fail(
                        404,
                        "MEMORY_SOURCE_NOT_FOUND",
                        "Candidate source is not owned task evidence.",
                    )
                data = MemoryInput(
                    idempotency_key=key,
                    memory_type=candidate.memory_type,
                    subject=candidate.subject,
                    predicate=candidate.predicate,
                    value=candidate.value,
                    scope=candidate.scope,
                    task_id=candidate.task_id if candidate.scope == "TASK" else None,
                    privacy_class=candidate.privacy_class,
                )
                memory = self.new_record(
                    session,
                    data,
                    candidate.origin,
                    f"task:{candidate.task_id}/evidence:{candidate.source_reference}",
                    candidate.confidence,
                )
            else:
                memory = self.owned(session, id)
                if operation == "delete":
                    if memory.status not in {"ACTIVE", "PENDING_CONFIRMATION"}:
                        fail(
                            409,
                            "MEMORY_STATE_CONFLICT",
                            "Only active or pending memories can be deleted.",
                        )
                    memory.status = "DELETED"
                    memory.updated_at = self.clock()
                    self.audit(session, memory, "MEMORY_DELETED", uuid4())
                elif operation == "reject":
                    if memory.status != "PENDING_CONFIRMATION":
                        fail(409, "MEMORY_STATE_CONFLICT", "Candidate is no longer pending.")
                    memory.status = "REJECTED"
                    memory.updated_at = self.clock()
                    self.audit(session, memory, "MEMORY_REJECTED", uuid4())
                elif operation in {"correct", "confirm"}:
                    expected = "ACTIVE" if operation == "correct" else "PENDING_CONFIRMATION"
                    if memory.status != expected:
                        fail(
                            409,
                            "MEMORY_STATE_CONFLICT",
                            "Memory lifecycle changed; reload before continuing.",
                        )
                    value = (
                        payload.value
                        if operation == "correct"
                        else payload.edited_value or memory.value
                    )
                    data = MemoryInput(
                        idempotency_key=key,
                        memory_type=memory.memory_type,
                        subject=memory.subject,
                        predicate=memory.predicate,
                        value=value,
                        scope=memory.scope,
                        task_id=memory.task_id,
                        privacy_class=memory.privacy_class,
                        valid_from=memory.valid_from,
                        valid_until=memory.valid_until,
                    )
                    decision, _ = self.policy.decide(
                        "USER_CORRECTION", memory.memory_type, memory.scope, data.value
                    )
                    if decision == "REJECT":
                        fail(
                            422, "MEMORY_POLICY_REJECTED", "Memory content was rejected by policy."
                        )
                    other = self.conflict(session, data, memory.id)
                    if other:
                        fail(
                            409,
                            "MEMORY_CONTRADICTION",
                            "Correct or delete the existing conflicting record first.",
                        )
                    if operation == "confirm" and not payload.edited_value:
                        memory.status = "ACTIVE"
                        memory.confirmed = True
                        memory.updated_at = self.clock()
                        memory.policy_decision = "TASK_ONLY" if memory.scope == "TASK" else "STORE"
                        memory.policy_reason = "HUMAN_CONFIRMED_INFERENCE"
                        self.embedding(session, memory)
                        self.audit(session, memory, "MEMORY_CONFIRMED", uuid4())
                    else:
                        old = memory
                        old.status = "SUPERSEDED"
                        old.updated_at = self.clock()
                        self.audit(session, old, "MEMORY_SUPERSEDED", uuid4())
                        memory = self.new_record(
                            session,
                            data,
                            "USER_CORRECTION" if operation == "correct" else old.origin,
                            f"correction:{old.id}"
                            if operation == "correct"
                            else old.source_reference,
                            None if operation == "correct" else old.confidence,
                            old.id,
                            operation == "confirm",
                        )
                else:
                    fail(422, "MEMORY_OPERATION_INVALID", "Unknown memory operation.")
            result = MemoryRead.model_validate(memory).model_dump(mode="json")
            session.add(
                MemoryMutation(
                    user_id=self.user_id,
                    idempotency_key=key,
                    request_hash=request_hash,
                    response=result,
                )
            )
            return result

    def list(self, pending=False):
        with SessionLocal.begin() as session:
            session.scalar(select(User.id).where(User.id == self.user_id).with_for_update())
            self.expire(session)
            q = select(MemoryRecord).where(MemoryRecord.user_id == self.user_id)
            if pending:
                q = q.where(MemoryRecord.status == "PENDING_CONFIRMATION")
            return [
                MemoryRead.model_validate(m)
                for m in session.scalars(q.order_by(MemoryRecord.created_at.desc()).limit(100))
            ]

    def detail(self, id):
        with SessionLocal() as session:
            return MemoryRead.model_validate(self.owned(session, id))

    def history(self, id):
        with SessionLocal() as session:
            self.owned(session, id)
            return [
                {
                    "id": str(a.id),
                    "memory_id": str(a.memory_id),
                    "event_type": a.event_type,
                    "trace_id": str(a.trace_id),
                    "safe_metadata": a.safe_metadata,
                    "created_at": a.created_at,
                }
                for a in session.scalars(
                    select(MemoryAudit)
                    .where(MemoryAudit.user_id == self.user_id, MemoryAudit.memory_id == id)
                    .order_by(MemoryAudit.created_at)
                )
            ]

    def search(self, query: MemoryQuery, trace_id=None):
        with SessionLocal.begin() as session:
            session.scalar(select(User.id).where(User.id == self.user_id).with_for_update())
            self.owned_task(session, query.task_id)
            moment = query.as_of_time or self.clock()
            allowed = PRIVACY[: PRIVACY.index(query.privacy_ceiling) + 1]
            eligible = select(MemoryRecord).where(
                MemoryRecord.user_id == self.user_id,
                MemoryRecord.status == "ACTIVE",
                MemoryRecord.memory_type.in_(query.types),
                MemoryRecord.privacy_class.in_(allowed),
                or_(
                    MemoryRecord.scope == "USER",
                    and_(MemoryRecord.scope == "TASK", MemoryRecord.task_id == query.task_id)
                    if query.task_id
                    else False,
                ),
                or_(MemoryRecord.valid_from.is_(None), MemoryRecord.valid_from <= moment),
                or_(MemoryRecord.valid_until.is_(None), MemoryRecord.valid_until > moment),
            )
            if query.scope:
                eligible = eligible.where(MemoryRecord.scope == query.scope)
            if query.subject:
                eligible = eligible.where(MemoryRecord.subject == query.subject.casefold())
            if query.predicate:
                eligible = eligible.where(MemoryRecord.predicate == query.predicate)
            rows = session.scalars(
                eligible.order_by(MemoryRecord.created_at, MemoryRecord.id).limit(200)
            ).all()
            ids = [m.id for m in rows]
            structured = (
                [m.id for m in rows] if query.subject or query.predicate or query.scope else []
            )
            lexical = []
            semantic = []
            similarities = {}
            if query.query and ids:
                ts = func.websearch_to_tsquery("simple", query.query)
                doc = func.to_tsvector("simple", MemoryRecord.normalized_text)
                lexical = list(
                    session.scalars(
                        select(MemoryRecord.id)
                        .where(MemoryRecord.id.in_(ids), doc.op("@@")(ts))
                        .order_by(func.ts_rank_cd(doc, ts).desc(), MemoryRecord.id)
                    ).all()
                )
                vector = self.embed(query.query, query.privacy_ceiling)
                distance = MemoryEmbedding.embedding.op("OPERATOR(public.<=>)")(vector.vector)
                nearest = session.execute(
                    select(MemoryEmbedding.memory_id, distance.label("distance"))
                    .where(
                        MemoryEmbedding.memory_id.in_(ids),
                        MemoryEmbedding.provider == vector.provider,
                        MemoryEmbedding.model == vector.model,
                        MemoryEmbedding.dimension == vector.dimension,
                    )
                    .order_by(distance, MemoryEmbedding.memory_id)
                    .limit(100)
                ).all()
                semantic = [r.memory_id for r in nearest]
                similarities = {r.memory_id: 1 - float(r.distance) for r in nearest}
            if not query.query and not structured:
                structured = ids
            ranks = [
                {id: i for i, id in enumerate(source, 1)}
                for source in [structured, lexical, semantic]
            ]
            scored = {
                id: sum(1 / (60 + r[id]) for r in ranks if id in r)
                for id in ids
                if any(id in r for r in ranks)
            }
            ordered = sorted(scored, key=lambda id: (-scored[id], str(id)))[: query.limit]
            by_id = {m.id: m for m in rows}
            hits = []
            for rank, id in enumerate(ordered, 1):
                memory = by_id[id]
                sources = [
                    name
                    for name, r in zip(["STRUCTURED", "LEXICAL", "SEMANTIC"], ranks, strict=True)
                    if id in r
                ]
                hits.append(
                    MemoryHit(
                        memory_id=id,
                        memory=MemoryRead.model_validate(memory),
                        retrieval_sources=sources,
                        reason_codes=[f"{s}_MATCH" for s in sources] + [f"{memory.scope}_SCOPE"],
                        structured_rank=ranks[0].get(id),
                        lexical_rank=ranks[1].get(id),
                        semantic_rank=ranks[2].get(id),
                        semantic_similarity=similarities.get(id),
                        fused_score=scored[id],
                        fused_rank=rank,
                        embedding_provider=self.provider.provider,
                        embedding_model=self.provider.model,
                        embedding_simulation=self.provider.simulation,
                    )
                )
            retrieval = MemoryRetrieval(
                id=uuid4(),
                user_id=self.user_id,
                task_id=query.task_id,
                trace_id=trace_id or uuid4(),
                query_hash=digest(query.model_dump(mode="json")),
                hits=[h.model_dump(mode="json") for h in hits],
            )
            session.add(retrieval)
            return RetrievalResult(
                id=retrieval.id,
                trace_id=retrieval.trace_id,
                hits=hits,
                disclosure="FIXTURE EMBEDDING / NOT A REAL SEMANTIC MODEL"
                if self.provider.simulation
                else "LOCAL EMBEDDING / RELEVANCE IS NOT TRUTH CONFIDENCE",
            )


def seed_memories():
    service = MemoryService(provider=FixtureEmbeddingProvider())
    with SessionLocal.begin() as session:
        session.scalar(select(User.id).where(User.id == DEMO_USER_ID).with_for_update())
        for subject, predicate, value, reference in [
            ("sarah", "preferred_cuisine", "Italian", "demo.memory.sarah.italian"),
            ("demo_user", "dinner_time", "after 6:00 PM", "demo.memory.user.dinner-time"),
        ]:
            id = uuid5(NAMESPACE_URL, "nova:memory:" + reference)
            if session.get(MemoryRecord, id):
                continue
            data = MemoryInput(
                idempotency_key="seed", subject=subject, predicate=predicate, value=value
            )
            service.new_record(session, data, "FIXTURE", reference, record_id=id)
