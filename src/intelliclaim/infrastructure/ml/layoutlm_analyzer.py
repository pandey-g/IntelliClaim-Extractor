"""LayoutLMv3-based document layout analyzer."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

from intelliclaim.application.interfaces.services import ILayoutAnalyzer
from intelliclaim.domain.entities.ocr_result import OCRResult
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.config.settings import Settings
from intelliclaim.infrastructure.ml.spatial_layout import (
    detect_key_value_pairs,
    words_to_tokens,
)

if TYPE_CHECKING:
    from PIL import Image as PILImage

logger = structlog.get_logger(__name__)


class LayoutLMv3LayoutAnalyzer(ILayoutAnalyzer):
    """Analyze document layout using LayoutLMv3 with spatial key-value pairing."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._processor: Any | None = None
        self._model: Any | None = None
        self._device: str = "cpu"
        self._load_failed = False

    async def analyze(
        self,
        document_id: DocumentId,
        image_path: Path,
        ocr_result: OCRResult,
    ) -> dict[str, object]:
        """Analyze document layout and return structured tokens."""
        del document_id
        return await asyncio.to_thread(self._analyze_sync, image_path, ocr_result)

    def _analyze_sync(self, image_path: Path, ocr_result: OCRResult) -> dict[str, object]:
        from PIL import Image

        image = Image.open(image_path).convert("RGB")
        page_width, page_height = image.size

        tokens = words_to_tokens(
            ocr_result.words,
            page_number=ocr_result.page_number,
            page_width=page_width,
            page_height=page_height,
        )
        pairs = detect_key_value_pairs(
            ocr_result.words,
            page_number=ocr_result.page_number,
            page_width=page_width,
            page_height=page_height,
        )

        model_confidence = self._compute_layout_confidence(image, ocr_result)
        for pair in pairs:
            base_confidence = float(pair["confidence"])
            pair["confidence"] = min(1.0, (base_confidence * 0.7) + (model_confidence * 0.3))

        return {
            "page_number": ocr_result.page_number,
            "tokens": tokens,
            "key_value_pairs": pairs,
            "layoutlm_available": self._try_load_model(),
            "layout_confidence": model_confidence,
        }

    def _try_load_model(self) -> bool:
        """Lazily load LayoutLMv3 model and processor."""
        if self._model is not None:
            return True
        if self._load_failed:
            return False

        try:
            import torch
            from transformers import LayoutLMv3Model, LayoutLMv3Processor

            self._processor = LayoutLMv3Processor.from_pretrained(
                self._settings.layoutlm_model_name,
                apply_ocr=False,
            )
            self._model = LayoutLMv3Model.from_pretrained(self._settings.layoutlm_model_name)
            self._model.eval()

            device = self._settings.layoutlm_device
            if device == "cuda" and not torch.cuda.is_available():
                device = "cpu"
            if device == "mps" and not torch.backends.mps.is_available():
                device = "cpu"

            self._device = device
            self._model.to(self._device)
            logger.info(
                "layoutlm_model_loaded",
                model=self._settings.layoutlm_model_name,
                device=self._device,
            )
            return True
        except Exception as exc:
            self._load_failed = True
            logger.warning("layoutlm_model_load_failed", error=str(exc))
            return False

    def _compute_layout_confidence(self, image: PILImage.Image, ocr_result: OCRResult) -> float:
        """Run LayoutLMv3 forward pass to derive layout confidence."""
        if not self._try_load_model() or not ocr_result.words:
            if ocr_result.average_confidence is not None:
                return ocr_result.average_confidence.value
            return 0.5

        try:
            import torch

            words = [word.text for word in ocr_result.words]
            boxes = [
                [
                    word.bounding_box.x,
                    word.bounding_box.y,
                    word.bounding_box.x + word.bounding_box.width,
                    word.bounding_box.y + word.bounding_box.height,
                ]
                for word in ocr_result.words
            ]

            encoding = self._processor(
                image,
                text=words,
                boxes=boxes,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding="max_length",
            )
            encoding = {key: value.to(self._device) for key, value in encoding.items()}

            with torch.no_grad():
                outputs = self._model(**encoding)

            hidden_states = outputs.last_hidden_state
            norms = torch.norm(hidden_states, dim=-1)
            attention_mask = encoding.get("attention_mask")
            if attention_mask is not None:
                masked = norms * attention_mask
                valid_tokens = attention_mask.sum().item()
                if valid_tokens > 0:
                    return float((masked.sum() / valid_tokens).item() / 100.0)

            return float(norms.mean().item() / 100.0)
        except Exception as exc:
            logger.warning("layoutlm_inference_failed", error=str(exc))
            if ocr_result.average_confidence is not None:
                return ocr_result.average_confidence.value
            return 0.5
