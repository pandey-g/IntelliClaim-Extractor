"""Extraction result validation application service."""

import re
from datetime import datetime

from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore

_AMOUNT_FIELDS = {ExtractionField.CLAIM_AMOUNT, ExtractionField.INVOICE_AMOUNT}
_DATE_FIELDS = {ExtractionField.INCIDENT_DATE, ExtractionField.SUBMISSION_DATE}
_DATE_FORMATS = ("%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y", "%Y-%m-%d")


class ExtractionValidator:
    """Validate and normalize extracted field values."""

    def validate(self, fields: list[ExtractedField]) -> list[ExtractedField]:
        """Validate extracted fields and adjust confidence scores."""
        validated: list[ExtractedField] = []
        for field in fields:
            validated.append(self._validate_field(field))
        return validated

    def _validate_field(self, field: ExtractedField) -> ExtractedField:
        if field.field_name in _AMOUNT_FIELDS:
            return self._validate_amount(field)
        if field.field_name in _DATE_FIELDS:
            return self._validate_date(field)
        if field.field_value.strip():
            return field
        return self._with_confidence(field, field.confidence.value * 0.5)

    def _validate_amount(self, field: ExtractedField) -> ExtractedField:
        cleaned = re.sub(r"[^\d.]", "", field.field_value)
        if not cleaned or not re.fullmatch(r"\d+(?:\.\d{1,2})?", cleaned):
            return self._with_confidence(field, field.confidence.value * 0.4)
        return field

    def _validate_date(self, field: ExtractedField) -> ExtractedField:
        for date_format in _DATE_FORMATS:
            try:
                datetime.strptime(field.field_value.strip(), date_format)
                return field
            except ValueError:
                continue
        return self._with_confidence(field, field.confidence.value * 0.4)

    @staticmethod
    def _with_confidence(field: ExtractedField, confidence: float) -> ExtractedField:
        clamped = max(0.0, min(1.0, confidence))
        field.confidence = ConfidenceScore(value=clamped)
        return field
