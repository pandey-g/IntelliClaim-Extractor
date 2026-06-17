"""Insurance claim field extractor using layout and OCR data."""

from __future__ import annotations

import re

from intelliclaim.application.interfaces.services import IFieldExtractor
from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.entities.ocr_result import OCRResult
from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.ml.field_patterns import (
    FIELD_VALUE_PATTERNS,
    match_field_from_label,
)


class InsuranceFieldExtractor(IFieldExtractor):
    """Extract structured insurance fields from layout analysis and OCR results."""

    async def extract(
        self,
        document_id: DocumentId,
        layout_data: dict[str, object],
        ocr_results: list[OCRResult],
    ) -> list[ExtractedField]:
        """Extract insurance claim fields from layout and OCR data."""
        candidates: dict[ExtractionField, ExtractedField] = {}

        pages = layout_data.get("pages", [])
        if isinstance(pages, list):
            for page in pages:
                if not isinstance(page, dict):
                    continue
                page_number = page.get("page_number")
                pairs = page.get("key_value_pairs", [])
                if not isinstance(pairs, list):
                    continue
                for pair in pairs:
                    if not isinstance(pair, dict):
                        continue
                    self._add_from_key_value_pair(
                        candidates,
                        document_id=document_id,
                        pair=pair,
                        page_number=page_number if isinstance(page_number, int) else None,
                    )

        for ocr_result in ocr_results:
            self._add_from_ocr_patterns(candidates, document_id, ocr_result)

        return list(candidates.values())

    def _add_from_key_value_pair(
        self,
        candidates: dict[ExtractionField, ExtractedField],
        *,
        document_id: DocumentId,
        pair: dict[str, object],
        page_number: int | None,
    ) -> None:
        key = pair.get("key")
        value = pair.get("value")
        if not isinstance(key, str) or not isinstance(value, str):
            return

        field_name = match_field_from_label(key)
        if field_name is None:
            return

        confidence_raw = pair.get("confidence", 0.5)
        confidence = ConfidenceScore(
            value=float(confidence_raw) if isinstance(confidence_raw, (int, float)) else 0.5
        )

        value_bbox = pair.get("value_bbox")
        bounding_box = None
        if isinstance(value_bbox, dict):
            bounding_box = BoundingBox(
                x=int(value_bbox.get("x", 0)),
                y=int(value_bbox.get("y", 0)),
                width=int(value_bbox.get("width", 0)),
                height=int(value_bbox.get("height", 0)),
            )

        self._upsert_candidate(
            candidates,
            ExtractedField.create(
                document_id=document_id,
                field_name=field_name,
                field_value=value.strip(),
                confidence=confidence,
                bounding_box=bounding_box,
                page_number=page_number,
            ),
        )

    def _add_from_ocr_patterns(
        self,
        candidates: dict[ExtractionField, ExtractedField],
        document_id: DocumentId,
        ocr_result: OCRResult,
    ) -> None:
        text = ocr_result.full_text
        if not text.strip():
            return

        base_confidence = 0.6
        if ocr_result.average_confidence is not None:
            base_confidence = ocr_result.average_confidence.value * 0.85

        for field_name, pattern in FIELD_VALUE_PATTERNS.items():
            if field_name in candidates:
                continue
            match = pattern.search(text)
            if match is None:
                continue

            value = match.group(0).strip()
            if field_name in {ExtractionField.CLAIM_AMOUNT, ExtractionField.INVOICE_AMOUNT}:
                value = re.sub(r"[^\d.,]", "", value)

            self._upsert_candidate(
                candidates,
                ExtractedField.create(
                    document_id=document_id,
                    field_name=field_name,
                    field_value=value,
                    confidence=ConfidenceScore(value=base_confidence),
                    page_number=ocr_result.page_number,
                ),
            )

    @staticmethod
    def _upsert_candidate(
        candidates: dict[ExtractionField, ExtractedField],
        field: ExtractedField,
    ) -> None:
        existing = candidates.get(field.field_name)
        if existing is None or field.confidence.value > existing.confidence.value:
            candidates[field.field_name] = field
