"""Unit tests for extracted field entity."""

import pytest

from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId


@pytest.mark.unit
class TestExtractedField:
    def test_create_extracted_field(self) -> None:
        doc_id = DocumentId.generate()
        field = ExtractedField.create(
            document_id=doc_id,
            field_name=ExtractionField.CLAIM_ID,
            field_value="CLM-12345",
            confidence=ConfidenceScore(value=0.97),
            page_number=1,
        )
        assert field.document_id == doc_id
        assert field.field_name == ExtractionField.CLAIM_ID
        assert field.field_value == "CLM-12345"
        assert field.confidence.value == 0.97
        assert field.page_number == 1
