"""Unit tests for extraction validator."""

import pytest

from intelliclaim.application.services.extraction_validator import ExtractionValidator
from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId


@pytest.mark.unit
class TestExtractionValidator:
    @pytest.fixture
    def document_id(self) -> DocumentId:
        return DocumentId.generate()

    def test_validate_amount_accepts_numeric(self, document_id: DocumentId) -> None:
        field = ExtractedField.create(
            document_id=document_id,
            field_name=ExtractionField.CLAIM_AMOUNT,
            field_value="12,345.67",
            confidence=ConfidenceScore(value=0.9),
        )
        validated = ExtractionValidator().validate([field])
        assert validated[0].confidence.value == 0.9

    def test_validate_amount_rejects_invalid(self, document_id: DocumentId) -> None:
        field = ExtractedField.create(
            document_id=document_id,
            field_name=ExtractionField.CLAIM_AMOUNT,
            field_value="N/A",
            confidence=ConfidenceScore(value=0.9),
        )
        validated = ExtractionValidator().validate([field])
        assert validated[0].confidence.value < 0.9

    def test_validate_date_accepts_known_format(self, document_id: DocumentId) -> None:
        field = ExtractedField.create(
            document_id=document_id,
            field_name=ExtractionField.INCIDENT_DATE,
            field_value="15/03/2024",
            confidence=ConfidenceScore(value=0.85),
        )
        validated = ExtractionValidator().validate([field])
        assert validated[0].confidence.value == 0.85

    def test_validate_date_rejects_invalid(self, document_id: DocumentId) -> None:
        field = ExtractedField.create(
            document_id=document_id,
            field_name=ExtractionField.INCIDENT_DATE,
            field_value="not-a-date",
            confidence=ConfidenceScore(value=0.85),
        )
        validated = ExtractionValidator().validate([field])
        assert validated[0].confidence.value < 0.85
