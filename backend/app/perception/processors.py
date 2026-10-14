"""Optional CPU adapters load only explicitly configured local directories, never Hub weights."""

import importlib.util
import io
from pathlib import Path

from PIL import Image

from app.config import settings
from app.perception.contracts import VisualOutput

LABELS = ["meeting_room_sign_present", "laptop_present", "backpack_present", "coffee_cup_present"]


class FixtureVisionProvider:
    processor = "FIXTURE_VISION"
    model = "fixture-vision-v1"
    simulation = True

    def status(self):
        return "AVAILABLE"

    def process(self, data, fixture):
        if not fixture:
            raise ValueError("Fixture is restricted to the controlled scene.")
        return [
            VisualOutput(
                observation_type="OBJECT",
                label=label,
                description=f"Simulated fixture annotation: {label.replace('_', ' ')}.",
                processor=self.processor,
                model=self.model,
                simulation=True,
            )
            for label in LABELS
        ]


class LocalFeatureAdapter:
    simulation = False

    def __init__(self, processor, enabled=False, model_path="", runtime=None):
        self.processor, self.enabled, self.model_path = processor, enabled, model_path
        self.model = Path(model_path).name or "NOT_CONFIGURED"
        self.runtime = runtime

    def status(self):
        if not self.enabled:
            return "DISABLED"
        if self.runtime:
            return "AVAILABLE"
        if not self.model_path or not Path(self.model_path).is_dir():
            return "UNAVAILABLE"
        if not importlib.util.find_spec("torch") or not importlib.util.find_spec("transformers"):
            return "UNAVAILABLE"
        return "AVAILABLE"

    def load(self):
        if self.runtime:
            return self.runtime
        if self.status() != "AVAILABLE":
            raise ValueError("Local processor unavailable")
        import torch
        from transformers import (
            AutoImageProcessor,
            CLIPModel,
            CLIPProcessor,
            Dinov2Model,
            SamModel,
            SamProcessor,
        )

        path = str(Path(self.model_path).resolve())
        # No torch.hub, pickle checkpoints, trust_remote_code, or network fallback.
        if self.processor == "CLIP":
            model = CLIPModel.from_pretrained(path, local_files_only=True, use_safetensors=True)
            processor = CLIPProcessor.from_pretrained(path, local_files_only=True)
        elif self.processor == "DINOV2":
            model = Dinov2Model.from_pretrained(path, local_files_only=True, use_safetensors=True)
            processor = AutoImageProcessor.from_pretrained(
                path, local_files_only=True, trust_remote_code=False
            )
        else:
            model = SamModel.from_pretrained(path, local_files_only=True, use_safetensors=True)
            processor = SamProcessor.from_pretrained(path, local_files_only=True)
        model.eval()
        self.runtime = (torch, model, processor)
        return self.runtime

    def representations(self, data, texts=None):
        torch, model, processor = self.load()
        with Image.open(io.BytesIO(data)) as image, torch.inference_mode():
            if self.processor == "CLIP":
                inputs = processor(images=image, text=texts, return_tensors="pt", padding=True)
                result = model(**inputs)
                image_embedding = result.image_embeds
                text_embedding = result.text_embeds
                # Normalized representations, cosine rather than calibrated probability.
                cosine = (image_embedding / image_embedding.norm(dim=-1, keepdim=True)) @ (
                    text_embedding / text_embedding.norm(dim=-1, keepdim=True)
                ).T
                return image_embedding, text_embedding, cosine
            if self.processor == "DINOV2":
                result = model(**processor(images=image, return_tensors="pt"))
                return result.last_hidden_state
            inputs = processor(
                images=image,
                input_points=[[[image.width / 2, image.height / 2]]],
                return_tensors="pt",
            )
            result = model(**inputs)
            masks = processor.image_processor.post_process_masks(
                result.pred_masks, inputs["original_sizes"], inputs["reshaped_input_sizes"]
            )[0]
            return masks, result.iou_scores

    def process(self, data, fixture=False):
        if self.processor == "CLIP":
            labels = ["meeting room", "outdoor park", "kitchen", "server room"]
            _, _, scores = self.representations(data, labels)
            values = scores[0].tolist()
            return [
                VisualOutput(
                    observation_type="SEMANTIC_MATCH",
                    label=label,
                    description="CLIP cosine image/text similarity; not detection or certainty.",
                    score=float(value),
                    score_type="CLIP_COSINE",
                    processor="CLIP",
                    model=self.model,
                    simulation=False,
                )
                for label, value in zip(labels, values, strict=True)
            ]
        if self.processor == "DINOV2":
            features = self.representations(data)
            return [
                VisualOutput(
                    observation_type="REGION",
                    label="visual_feature_representation",
                    description=(
                        f"DINOv2 features computed; shape {list(features.shape)}. "
                        "No semantic classification or vector persistence."
                    ),
                    processor="DINOV2",
                    model=self.model,
                    simulation=False,
                )
            ]
        # The orchestrator saves PNG mask artifacts, never raw arrays in JSONB.
        masks, scores = self.representations(data)
        return {"masks": masks, "scores": scores}


def processors():
    return [
        FixtureVisionProvider(),
        LocalFeatureAdapter("CLIP", settings.vision_clip_enabled, settings.vision_clip_model_path),
        LocalFeatureAdapter(
            "DINOV2", settings.vision_dino_enabled, settings.vision_dino_model_path
        ),
        LocalFeatureAdapter("SAM", settings.vision_sam_enabled, settings.vision_sam_model_path),
    ]
