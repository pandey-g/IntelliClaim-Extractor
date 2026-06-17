"""Unit tests for document query service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from intelliclaim.application.services.document_query_service import DocumentQueryService
from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.enums.document_status import DocumentStatus
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.exceptions.document import DocumentNotFoundError
from intelliclaim.domain.value_objects.document_id import DocumentId


@pytest.mark.unit
class TestDocumentQueryService:
    @pytest.fixture
    def document_id(self) -> DocumentId:
        return DocumentId.generate()

    @pytest.fixture
    def sample_document(self, document_id: DocumentId) -> Document:
        now = datetime.now(UTC)
        return Document(
            id=document_id,
            filename="claim.pdf",
            content_type="application/pdf",
            document_type=DocumentType.PDF,
            file_size_bytes=1024,
            storage_path="/storage/claim.pdf",
            created_at=now,
            updated_at=now,
        )

    async def test_get_document(self, document_id: DocumentId, sample_document: Document) -> None:
        repo = AsyncMock()
        repo.get_by_id = AsyncMock(return_value=sample_document)
        service = DocumentQueryService(repo)

        result = await service.get_document(document_id)
        assert result.filename == "claim.pdf"
        assert result.status == DocumentStatus.PENDING

    async def test_get_document_not_found(self, document_id: DocumentId) -> None:
        repo = AsyncMock()
        repo.get_by_id = AsyncMock(return_value=None)
        service = DocumentQueryService(repo)

        with pytest.raises(DocumentNotFoundError):
            await service.get_document(document_id)

    async def test_get_status(self, document_id: DocumentId, sample_document: Document) -> None:
        repo = AsyncMock()
        repo.get_by_id = AsyncMock(return_value=sample_document)
        service = DocumentQueryService(repo)

        result = await service.get_status(document_id)
        assert result.status == DocumentStatus.PENDING
