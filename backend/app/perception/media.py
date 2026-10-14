"""Bounded decode/re-encode. Original bytes/filename/metadata never reach storage or logs."""

import hashlib
import io
import os
import struct
import warnings
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw, ImageOps
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import Device
from app.perception.models import MediaAsset
from app.seed import DEMO_USER_ID
from app.service import fail, find_task

MIMES = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}


def fixture_bytes():
    image = Image.new("RGB", (480, 300), "#20272b")
    draw = ImageDraw.Draw(image)
    draw.rectangle((25, 20, 220, 65), fill="#c0d7c9")
    draw.text((35, 35), "MEETING ROOM / FIXTURE", fill="#172019")
    draw.rectangle((20, 210, 460, 225), fill="#7b6b5a")
    draw.rectangle((85, 120, 230, 205), fill="#617989")
    draw.rectangle((95, 130, 220, 195), fill="#1b242b")
    draw.polygon([(70, 215), (245, 215), (230, 205), (85, 205)], fill="#a4afb2")
    draw.rounded_rectangle((320, 130, 400, 210), radius=15, fill="#997554")
    draw.arc((340, 105, 380, 160), 180, 360, fill="#c0ad92", width=4)
    draw.rectangle((260, 175, 290, 210), fill="#e4d5be")
    draw.ellipse((280, 182, 305, 202), outline="#e4d5be", width=4)
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def check_container(data, fmt):
    # Reject appended polyglots and malformed chunk lengths where readily detectable.
    if fmt == "JPEG":
        if not data.startswith(b"\xff\xd8") or not data.endswith(b"\xff\xd9"):
            raise ValueError("Ambiguous JPEG framing")
    elif fmt == "WEBP":
        if (
            data[:4] != b"RIFF"
            or data[8:12] != b"WEBP"
            or len(data) != int.from_bytes(data[4:8], "little") + 8
        ):
            raise ValueError("Ambiguous WEBP framing")
    else:
        pos = 8
        while pos + 12 <= len(data):
            size = int.from_bytes(data[pos : pos + 4], "big")
            kind = data[pos + 4 : pos + 8]
            pos += size + 12
            if pos > len(data):
                raise ValueError("Truncated PNG")
            if kind == b"IEND":
                if size or pos != len(data):
                    raise ValueError("Ambiguous PNG framing")
                return
        raise ValueError("Missing PNG end")


class MediaIngestionService:
    def normalize(self, data: bytes, mime: str):
        if not data or len(data) > settings.max_image_bytes:
            fail(413, "IMAGE_SIZE_LIMIT", "Image must fit the server byte limit.")
        if mime not in MIMES.values():
            fail(415, "UNSUPPORTED_IMAGE", "JPEG, PNG and WEBP only.")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                with Image.open(io.BytesIO(data), formats=list(MIMES)) as image:
                    fmt = image.format
                    if MIMES.get(fmt) != mime or getattr(image, "n_frames", 1) != 1:
                        raise ValueError("Format mismatch or animation")
                    w, h = image.size
                    if (
                        not 0 < w <= settings.max_image_width
                        or not 0 < h <= settings.max_image_height
                        or w * h > settings.max_image_pixels
                    ):
                        fail(413, "IMAGE_DIMENSION_LIMIT", "Image dimensions exceed server limits.")
                    check_container(data, fmt)
                    image.verify()
                with Image.open(io.BytesIO(data), formats=list(MIMES)) as image:
                    metadata = bool(image.info or image.getexif())
                    exif = image.info.get("exif")
                    if exif and (
                        not isinstance(exif, bytes)
                        or len(exif) < 14
                        or exif[:10] not in {b"Exif\x00\x00II*\x00", b"Exif\x00\x00MM\x00*"}
                    ):
                        raise ValueError("Malformed EXIF header")
                    image.load()
                    oriented = ImageOps.exif_transpose(image).convert("RGB")
                    clean = Image.frombytes("RGB", oriented.size, oriented.tobytes())
                    out = io.BytesIO()
                    clean.save(out, format="PNG")
                    normalized = out.getvalue()
                    if len(normalized) > settings.max_normalized_image_bytes:
                        fail(
                            413, "NORMALIZED_SIZE_LIMIT", "Normalized image exceeds server limits."
                        )
                    return normalized, clean.width, clean.height, metadata
        except (Image.DecompressionBombError, Image.DecompressionBombWarning):
            fail(413, "IMAGE_BOMB", "Image decompression limit exceeded.")
        except (OSError, ValueError, SyntaxError, Warning, struct.error):
            fail(422, "INVALID_IMAGE", "Image cannot be safely decoded.")

    async def read_upload(self, request):
        import asyncio

        data = bytearray()
        try:
            async with asyncio.timeout(8):
                async for chunk in request.stream():
                    if len(data) + len(chunk) > settings.max_image_bytes:
                        fail(413, "IMAGE_SIZE_LIMIT", "Image exceeds server byte limit.")
                    data.extend(chunk)
        except TimeoutError:
            fail(408, "UPLOAD_TIMEOUT", "Upload exceeded its deadline.")
        return bytes(data)

    def path(self, media):
        root = Path(settings.media_directory).resolve()
        expected = f"{media.id}.png"
        if media.sanitized_reference != expected:
            fail(409, "MEDIA_REFERENCE_INVALID", "Media reference is invalid.")
        path = root / expected
        if path.is_symlink() or path.resolve().parent != root:
            fail(409, "MEDIA_REFERENCE_INVALID", "Media reference is invalid.")
        return path

    def owned(self, session, task_id, media_id):
        find_task(session, task_id)
        media = session.scalar(
            select(MediaAsset).where(
                MediaAsset.id == media_id,
                MediaAsset.task_id == task_id,
                MediaAsset.user_id == DEMO_USER_ID,
            )
        )
        if media is None:
            fail(404, "MEDIA_NOT_FOUND", "Media was not found for this task.")
        return media

    def ingest(self, task_id, key, data, mime, fixture=False):
        normalized, width, height, removed = self.normalize(data, mime)
        digest = hashlib.sha256(normalized).hexdigest()
        source = "FIXTURE_IMAGE" if fixture else "IMAGE"
        if fixture and normalized != self.normalize(fixture_bytes(), "image/png")[0]:
            fail(422, "INVALID_FIXTURE", "Controlled fixture required.")
        with SessionLocal.begin() as session:
            task = find_task(session, task_id, lock=True)
            previous = session.scalar(
                select(MediaAsset).where(
                    MediaAsset.task_id == task_id, MediaAsset.idempotency_key == key
                )
            )
            if previous:
                if previous.sha256 != digest or previous.source != source:
                    fail(409, "IDEMPOTENCY_CONFLICT", "Media key belongs to different input.")
                return self.read(previous)
            device = session.get(Device, task.current_device_id)
            if fixture and device.type != "WEARABLE":
                fail(409, "WEARABLE_REQUIRED", "Handoff to Wearable before attaching the fixture.")
            media = MediaAsset(
                id=uuid4(),
                user_id=task.user_id,
                task_id=task.id,
                device_id=device.id,
                sha256=digest,
                width=width,
                height=height,
                byte_size=len(normalized),
                source=source,
                metadata_removed=removed,
                idempotency_key=key,
            )
            media.sanitized_reference = f"{media.id}.png"
            root = Path(settings.media_directory)
            root.mkdir(parents=True, exist_ok=True, mode=0o700)
            path = self.path(media)
            try:
                with path.open("xb") as handle:
                    os.chmod(path, 0o600)
                    handle.write(normalized)
                session.add(media)
                session.flush()
            except Exception:
                path.unlink(missing_ok=True)
                raise
            result = self.read(media)
        return result

    def read(self, media):
        return {
            "id": str(media.id),
            "task_id": str(media.task_id),
            "device_id": str(media.device_id),
            "sha256": media.sha256,
            "mime_type": media.mime_type,
            "width": media.width,
            "height": media.height,
            "byte_size": media.byte_size,
            "source": media.source,
            "sanitized": True,
            "metadata_removed": media.metadata_removed,
            "created_at": media.created_at,
        }

    def verified_bytes(self, media):
        path = self.path(media)
        if not path.exists() or path.stat().st_size != media.byte_size:
            fail(409, "MEDIA_UNAVAILABLE", "Sanitized media is unavailable.")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != media.sha256:
            fail(409, "MEDIA_INTEGRITY", "Sanitized media integrity failed.")
        return data
