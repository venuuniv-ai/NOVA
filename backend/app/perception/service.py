import hashlib
import io
import logging
import time
from datetime import UTC, datetime
from uuid import uuid4

from PIL import Image
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.model_routing.contracts import ModelRequest
from app.model_routing.service import ModelRoutingService
from app.models import Device
from app.perception.contracts import (
    ContextEvidence,
    ObservationRead,
    PerceptionRequest,
    PerceptionResult,
    Region,
    VisionOutput,
    VisualOutput,
)
from app.perception.media import MediaIngestionService, fixture_bytes
from app.perception.models import (
    MediaArtifact,
    PerceptionRun,
    ProcessorRun,
    VisualObservation,
)
from app.perception.processors import processors
from app.perception.vision import INTERPRETATION
from app.service import fail, find_task

logger = logging.getLogger("nova.perception")


class PerceptionOrchestrator:
    def __init__(self, providers=None, router=None):
        self.providers = providers if providers is not None else processors()
        self.router = router or ModelRoutingService()
        self.media = MediaIngestionService()

    def run(self, task_id, payload: PerceptionRequest, correlation_id):
        digest = hashlib.sha256(payload.model_dump_json().encode()).hexdigest()
        lock = int.from_bytes(
            hashlib.sha256(f"perception:{task_id}:{payload.idempotency_key}".encode()).digest()[:8],
            "big",
        ) % (2**63)
        with (
            engine.connect() as connection,
            Session(bind=connection, expire_on_commit=False) as session,
        ):
            session.execute(text("SELECT pg_advisory_lock(:key)"), {"key": lock})
            session.commit()
            try:
                media = self.media.owned(session, task_id, payload.media_id)
                prior = session.scalar(
                    select(PerceptionRun).where(
                        PerceptionRun.task_id == task_id,
                        PerceptionRun.idempotency_key == payload.idempotency_key,
                    )
                )
                if prior:
                    if prior.request_hash != digest:
                        fail(
                            409,
                            "IDEMPOTENCY_CONFLICT",
                            "Perception key belongs to another request.",
                        )
                    result = self.read(session, task_id, prior.id)
                    result.replayed = True
                    return result
                data = self.media.verified_bytes(media)
                fixture = media.source == "FIXTURE_IMAGE"
                if fixture and data != self.media.normalize(fixture_bytes(), "image/png")[0]:
                    fail(
                        409,
                        "FIXTURE_INTEGRITY",
                        "Fixture content no longer matches its provenance.",
                    )
                device = session.get(Device, media.device_id)
                device_type, user_id = device.type, media.user_id
                run = PerceptionRun(
                    id=uuid4(),
                    media_id=media.id,
                    task_id=task_id,
                    trace_id=uuid4(),
                    idempotency_key=payload.idempotency_key,
                    request_hash=digest,
                    privacy_class=payload.privacy_class,
                    status="RUNNING",
                    simulation=fixture,
                )
                session.add(run)
                session.commit()
                for provider in self.providers:
                    if provider.processor not in payload.processors:
                        continue
                    try:
                        status = provider.status()
                    except Exception:
                        status = "UNAVAILABLE"
                    processor = ProcessorRun(
                        id=uuid4(),
                        perception_run_id=run.id,
                        processor=provider.processor,
                        model=provider.model,
                        status="SKIPPED"
                        if status == "DISABLED"
                        else "UNAVAILABLE"
                        if status != "AVAILABLE"
                        else "FAILED",
                        simulation=provider.simulation,
                        latency_ms=None,
                    )
                    session.add(processor)
                    session.commit()
                    if status != "AVAILABLE":
                        continue
                    if provider.simulation and (not fixture or not payload.allow_fixture):
                        processor.status = "SKIPPED"
                        processor.safe_error = "FIXTURE_NOT_PERMITTED"
                        session.commit()
                        continue
                    start = time.perf_counter()
                    try:
                        output = provider.process(data, fixture)
                        if provider.processor == "SAM":
                            output = self.save_masks(session, media, processor, output)
                        if (
                            not isinstance(output, list)
                            or len(output)
                            > {"FIXTURE_VISION": 4, "CLIP": 4, "DINOV2": 1, "SAM": 3}[
                                provider.processor
                            ]
                        ):
                            raise ValueError("Unbounded processor output")
                        checked = [
                            VisualOutput.model_validate(
                                item.model_dump() if hasattr(item, "model_dump") else item
                            )
                            for item in output
                        ]
                        if any(
                            item.processor != provider.processor
                            or item.model != provider.model
                            or item.simulation != provider.simulation
                            for item in checked
                        ):
                            raise ValueError("Forged processor provenance")
                        for item in checked:
                            session.add(
                                VisualObservation(
                                    perception_run_id=run.id,
                                    processor_run_id=processor.id,
                                    output=item.model_dump(mode="json"),
                                )
                            )
                        processor.status = "DONE"
                        session.commit()
                    except Exception:
                        session.rollback()
                        processor = session.get(ProcessorRun, processor.id)
                        processor.status, processor.safe_error = (
                            "FAILED",
                            "PROCESSOR_OUTPUT_INVALID",
                        )
                        session.commit()
                    processor.latency_ms = round((time.perf_counter() - start) * 1000, 3)
                    session.commit()
                if payload.use_vlm:
                    model_request = ModelRequest(
                        task_id=task_id,
                        user_id=user_id,
                        trace_id=run.trace_id,
                        purpose="VISUAL_CONTEXT",
                        modality="IMAGE",
                        media_id=media.id,
                        media_sha256=media.sha256,
                        vision_fixture=fixture,
                        vision_simulation_allowed=payload.allow_fixture,
                        required_capabilities=["VISION", "STRUCTURED"],
                        privacy_class=payload.privacy_class,
                        current_device=device_type,
                        structured_input={"media_id": str(media.id), "sha256": media.sha256},
                        max_output_tokens=512,
                    )
                    session.commit()
                    response = self.router.run(model_request, correlation_id)
                    processor = ProcessorRun(
                        id=uuid4(),
                        perception_run_id=run.id,
                        processor="FIXTURE_VLM",
                        model=response.model or "NOT_CONFIGURED",
                        simulation=True,
                        status="FAILED",
                        latency_ms=response.latency_ms,
                        safe_error=response.safe_error,
                    )
                    session.add(processor)
                    if response.status == "DONE" and response.output:
                        try:
                            visual = VisionOutput.model_validate(response.output)
                            if (
                                any(
                                    o.processor != "FIXTURE_VLM"
                                    or o.model != response.model
                                    or not o.simulation
                                    for o in visual.observations
                                )
                                or not fixture
                            ):
                                raise ValueError("Invalid VLM provenance")
                            for item in visual.observations:
                                session.add(
                                    VisualObservation(
                                        perception_run_id=run.id,
                                        processor_run_id=processor.id,
                                        output=item.model_dump(mode="json"),
                                    )
                                )
                            processor.status = "DONE"
                        except Exception:
                            processor.safe_error = "VLM_OUTPUT_INVALID"
                    session.commit()
                records = session.scalars(
                    select(ProcessorRun).where(ProcessorRun.perception_run_id == run.id)
                ).all()
                observations = session.scalars(
                    select(VisualObservation).where(VisualObservation.perception_run_id == run.id)
                ).all()
                run.simulation = bool(observations) and all(
                    o.output["simulation"] for o in observations
                )
                failures = any(p.status in {"FAILED", "UNAVAILABLE"} for p in records)
                run.status = (
                    "PARTIAL" if observations and failures else "DONE" if observations else "FAILED"
                )
                run.warnings = [
                    "Visual evidence is untrusted; no location verification, "
                    "authorization or permanent memory."
                ]
                if failures:
                    run.warnings += ["One or more processors failed; results are partial."]
                run.completed_at = datetime.now(UTC)
                run.context = [
                    self.evidence(o, media, device_type).model_dump(mode="json")
                    for o in observations
                ]
                session.commit()
                logger.info(
                    "perception_complete",
                    extra={
                        "trace_id": str(run.trace_id),
                        "task_id": str(task_id),
                        "correlation_id": correlation_id,
                        "media_id": str(media.id),
                    },
                )
                return self.read(session, task_id, run.id)
            finally:
                session.rollback()
                session.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": lock})
                session.commit()

    def save_masks(self, session, media, processor, output):
        import os

        masks, scores = output["masks"], output["scores"]
        # Optional real SAM: one prompted point, at most three binary mask PNGs.
        masks = masks.reshape(-1, media.height, media.width)
        scores = scores.reshape(-1)
        if len(masks) > 3 or len(masks) != len(scores):
            raise ValueError("Unbounded masks")
        results = []
        for mask, score in zip(masks, scores, strict=True):
            values = (mask.detach().cpu().numpy() > 0).astype("uint8") * 255
            image = Image.fromarray(values)
            bounds = image.getbbox()
            if not bounds:
                continue
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            data = buf.getvalue()
            artifact = MediaArtifact(
                id=uuid4(),
                media_id=media.id,
                processor_run_id=processor.id,
                sha256=hashlib.sha256(data).hexdigest(),
                byte_size=len(data),
            )
            artifact.sanitized_reference = f"{artifact.id}.png"
            path = self.media.path(artifact)
            with path.open("xb") as handle:
                os.chmod(path, 0o600)
                handle.write(data)
            session.add(artifact)
            x1, y1, x2, y2 = bounds
            results.append(
                VisualOutput(
                    observation_type="SEGMENT",
                    label="prompted_segment",
                    description=(
                        "SAM mask around server-owned center point; "
                        "semantic object identity unknown."
                    ),
                    processor="SAM",
                    model=processor.model,
                    simulation=False,
                    score=float(score),
                    score_type="SAM_IOU",
                    mask_reference=artifact.id,
                    region=Region(
                        x=x1 / media.width,
                        y=y1 / media.height,
                        width=(x2 - x1) / media.width,
                        height=(y2 - y1) / media.height,
                    ),
                )
            )
        return results

    def evidence(self, observation, media, device):
        output = VisualOutput.model_validate(observation.output)
        interpretation = (
            INTERPRETATION
            if output.processor == "FIXTURE_VLM" and media.source == "FIXTURE_IMAGE"
            else "Untrusted observation; no verified physical fact."
        )
        return ContextEvidence(
            observation_id=observation.id,
            media_id=media.id,
            processor=output.processor,
            model=output.model,
            simulation=output.simulation,
            score=output.score,
            score_type=output.score_type,
            timestamp=observation.created_at,
            device=device,
            source=media.source,
            sha256=media.sha256,
            label=output.label,
            interpretation=interpretation,
        )

    def read(self, session, task_id, run_id):
        find_task(session, task_id)
        run = session.scalar(
            select(PerceptionRun).where(
                PerceptionRun.id == run_id, PerceptionRun.task_id == task_id
            )
        )
        if run is None:
            fail(404, "PERCEPTION_NOT_FOUND", "Perception run was not found.")
        media = self.media.owned(session, task_id, run.media_id)
        device = session.get(Device, media.device_id)
        processor_records = session.scalars(
            select(ProcessorRun)
            .where(ProcessorRun.perception_run_id == run.id)
            .order_by(ProcessorRun.processor)
        ).all()
        observations = session.scalars(
            select(VisualObservation)
            .where(VisualObservation.perception_run_id == run.id)
            .order_by(VisualObservation.created_at, VisualObservation.id)
        ).all()
        return PerceptionResult(
            id=run.id,
            task_id=task_id,
            media_id=media.id,
            trace_id=run.trace_id,
            privacy_class=run.privacy_class,
            status=run.status,
            simulation=run.simulation,
            warnings=run.warnings,
            context=run.context,
            started_at=run.started_at,
            completed_at=run.completed_at,
            processors=[
                {
                    "id": str(p.id),
                    "processor": p.processor,
                    "model": p.model,
                    "status": p.status,
                    "simulation": p.simulation,
                    "latency_ms": p.latency_ms,
                    "safe_error": p.safe_error,
                }
                for p in processor_records
            ],
            observations=[
                ObservationRead(
                    **o.output,
                    id=o.id,
                    media_id=media.id,
                    sha256=media.sha256,
                    source=media.source,
                    device=device.type,
                    created_at=o.created_at,
                )
                for o in observations
            ],
        )


def recover_perception():
    with SessionLocal.begin() as session:
        for run in session.scalars(
            select(PerceptionRun).where(PerceptionRun.status == "RUNNING").with_for_update()
        ):
            run.status = "FAILED"
            run.completed_at = datetime.now(UTC)
            run.warnings = ["APPLICATION_RESTARTED; partial processor records retained."]


class VisualReasoningService:
    """Evidence is data; the existing agent and Phase 3 policy retain all authority."""

    def run(self, task_id, run_id, payload, correlation_id):
        from app.intelligence.models import AgentExecution
        from app.intelligence.orchestrator import AgentOrchestrator
        from app.proactive.contracts import ContextEventInput
        from app.proactive.service import ProactiveService

        operation = hashlib.sha256(f"{run_id}:{payload.idempotency_key}".encode()).hexdigest()
        key = f"visual:{operation}:{int(payload.propose_action)}"
        opposite = f"visual:{operation}:{int(not payload.propose_action)}"
        lock = int.from_bytes(
            hashlib.sha256(f"visual-reason:{task_id}:{operation}".encode()).digest()[:8], "big"
        ) % (2**63)
        with engine.connect() as connection, Session(bind=connection) as session:
            session.execute(text("SELECT pg_advisory_lock(:key)"), {"key": lock})
            session.commit()
            try:
                run = PerceptionOrchestrator().read(session, task_id, run_id)
                if not run.context or run.status not in {"DONE", "PARTIAL"}:
                    fail(
                        409,
                        "VISUAL_CONTEXT_UNAVAILABLE",
                        "No completed visual context is available.",
                    )
                if session.scalar(
                    select(AgentExecution.id).where(
                        AgentExecution.task_id == task_id,
                        AgentExecution.idempotency_key == opposite,
                    )
                ):
                    fail(
                        409,
                        "IDEMPOTENCY_CONFLICT",
                        "Reasoning key belongs to different action intent.",
                    )
                session.commit()
                execution = AgentOrchestrator(visual_context=run.context).run(
                    task_id, key, correlation_id
                )
                proposal = None
                if payload.propose_action and execution.execution.status == "DONE":
                    # Only server-owned calendar/travel facts justify this draft.
                    proposal = ProactiveService().evaluate(
                        ContextEventInput(task_id=task_id, idempotency_key=key), correlation_id
                    )
                return {
                    "task_id": str(task_id),
                    "perception_id": str(run_id),
                    "context": [e.model_dump(mode="json") for e in run.context],
                    "execution": execution,
                    "proposal": proposal,
                    "memory_written": False,
                    "external_message_sent": False,
                }
            finally:
                session.rollback()
                session.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": lock})
                session.commit()
