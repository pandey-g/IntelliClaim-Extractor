"""Unit tests for extraction query service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from intelliclaim.application.services.extraction_query_service import ExtractionQueryService
from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.domain.exceptions.document import DocumentNotFoundError
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId


@pytest.mark.unit
class TestExtractionQueryService:
    @pytest.fixture
    def document_id(self) -> DocumentId:
        return DocumentId.generate()

    async def test_get_extractions(self, document_id: DocumentId) -> None:
        document = Document(
            id=document_id,
            filename="claim.png",
            content_type="image/png",
            document_type=DocumentType.PNG,
            file_size_bytes=100,
            storage_path="/storage/claim.png",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        extracted = ExtractedField.create(
            document_id=document_id,
            field_name=ExtractionField.CLAIM_ID,
            field_value="CLM-12345",
            confidence=ConfidenceScore(value=0.95),
            page_number=1,
        )

        doc_repo = AsyncMock()
        doc_repo.get_by_id = AsyncMock(return_value=document)
        field_repo = AsyncMock()
        field_repo.get_by_document_id = AsyncMock(return_value=[extracted])

        service = ExtractionQueryService(doc_repo, field_repo)
        result = await service.get_extractions(document_id)

        assert result.document_id == document_id.value
        assert len(result.fields) == 1
        assert result.fields[0].field_value == "CLM-12345"
        assert result.confidence_score == 0.95

    async def test_get_extractions_not_found(self, document_id: DocumentId) -> None:
        service = ExtractionQueryService(
            AsyncMock(get_by_id=AsyncMock(return_value=None)),
            AsyncMock(),
        )
        with pytest.raises(DocumentNotFoundError):
            await service.get_extractions(document_id)
