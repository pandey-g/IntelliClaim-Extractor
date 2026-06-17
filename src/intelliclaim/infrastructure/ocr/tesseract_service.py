"""Tesseract OCR service adapter."""

import asyncio
from pathlib import Path

import pytesseract
from pytesseract import Output

from intelliclaim.application.interfaces.services import IImagePreprocessor, IOCRService
from intelliclaim.domain.entities.ocr_result import OCRResult, OCRWord
from intelliclaim.domain.exceptions.document import DocumentProcessingError
from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.config.settings import Settings
from intelliclaim.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class TesseractOCRService(IOCRService):
    """Executes OCR using Tesseract with OpenCV preprocessing."""

    def __init__(self, settings: Settings, preprocessor: IImagePreprocessor) -> None:
        self._preprocessor = preprocessor
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    async def extract_text(
        self,
        document_id: DocumentId,
        image_path: Path,
        page_number: int,
    ) -> OCRResult:
        """Preprocess image and extract text with word-level bounding boxes."""
        preprocessed_path = image_path.parent / f"preprocessed_{image_path.name}"

        try:
            return await asyncio.to_thread(
                self._run_ocr,
                document_id,
                image_path,
                preprocessed_path,
                page_number,
            )
        except DocumentProcessingError:
            raise
        except Exception as exc:
            raise DocumentProcessingError(
                f"OCR failed for page {page_number}: {exc}",
                document_id=str(document_id),
            ) from exc

    def _run_ocr(
        self,
        document_id: DocumentId,
        image_path: Path,
        preprocessed_path: Path,
        page_number: int,
    ) -> OCRResult:
        self._preprocessor.preprocess(image_path, output_path=preprocessed_path)

        try:
            data = pytesseract.image_to_data(
                str(preprocessed_path),
                output_type=Output.DICT,
                config="--oem 3 --psm 3",
            )
        except pytesseract.TesseractError as exc:
            raise DocumentProcessingError(
                f"Tesseract execution failed: {exc}",
                document_id=str(document_id),
            ) from exc

        words: list[OCRWord] = []
        text_parts: list[str] = []

        count = len(data["text"])
        for index in range(count):
            text = data["text"][index].strip()
            if not text:
                continue

            confidence_raw = float(data["conf"][index])
            if confidence_raw < 0:
                continue

            confidence = ConfidenceScore(value=confidence_raw / 100.0)
            bounding_box = BoundingBox(
                x=int(data["left"][index]),
                y=int(data["top"][index]),
                width=int(data["width"][index]),
                height=int(data["height"][index]),
            )
            words.append(
                OCRWord(
                    text=text,
                    confidence=confidence,
                    bounding_box=bounding_box,
                )
            )
            text_parts.append(text)

        full_text = " ".join(text_parts)
        result = OCRResult.create(
            document_id=document_id,
            page_number=page_number,
            full_text=full_text,
            words=words,
        )

        logger.info(
            "ocr_completed",
            document_id=str(document_id),
            page_number=page_number,
            word_count=len(words),
            avg_confidence=result.average_confidence.value if result.average_confidence else None,
        )
        return result
