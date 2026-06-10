"""Unit tests for application DTOs."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from intelliclaim.application.dto.document import (
    DocumentResponseDTO,
    DocumentStatusDTO,
    DocumentUploadDTO,
    ExtractedFieldDTO,
    ExtractionResponseDTO,
)
from intelliclaim.domain.enums.document_status import DocumentStatus


@pytest.mark.unit
class TestDocumentDTOs:
    def test_document_upload_dto(self) -> None:
        doc_id = uuid4()
        dto = DocumentUploadDTO(document_id=doc_id)
        assert dto.document_id == doc_id

    def test_document_response_dto(self) -> None:
        now = datetime.now(UTC)
        dto = DocumentResponseDTO(
            document_id=uuid4(),
            filename="claim.pdf",
            content_type="application/pdf",
            document_type="pdf",
            file_size_bytes=1024,
            status=DocumentStatus.PENDING,
            page_count=1,
            created_at=now,
            updated_at=now,
        )
        assert dto.status == DocumentStatus.PENDING

    def test_extraction_response_dto(self) -> None:
        dto = ExtractionResponseDTO(
            document_id=uuid4(),
            fields=[
                ExtractedFieldDTO(
                    field_name="claim_id",
                    field_value="CLM-12345",
                    confidence=0.97,
                )
            ],
            confidence_score=0.97,
        )
        assert dto.confidence_score == 0.97

    def test_extracted_field_confidence_bounds(self) -> None:
        with pytest.raises(ValueError):
            ExtractedFieldDTO(field_name="x", field_value="y", confidence=1.5)
