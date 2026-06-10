"""Integration tests for document repository."""

import pytest

from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.enums.document_status import DocumentStatus
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.value_objects.document_id import DocumentId


@pytest.mark.integration
class TestDocumentRepository:
    @pytest.fixture
    def sample_document(self) -> Document:
        return Document(
            id=DocumentId.generate(),
            filename="claim_form.pdf",
            content_type="application/pdf",
            document_type=DocumentType.PDF,
            file_size_bytes=2048,
            storage_path="/storage/claim_form.pdf",
        )

    async def test_save_and_get_by_id(self, repositories, sample_document: Document) -> None:
        saved = await repositories.document_repository.save(sample_document)
        assert saved.id == sample_document.id

        fetched = await repositories.document_repository.get_by_id(sample_document.id)
        assert fetched is not None
        assert fetched.filename == "claim_form.pdf"
        assert fetched.status == DocumentStatus.PENDING

    async def test_get_by_id_returns_none_when_missing(self, repositories) -> None:
        result = await repositories.document_repository.get_by_id(DocumentId.generate())
        assert result is None

    async def test_update_document_status(self, repositories, sample_document: Document) -> None:
        await repositories.document_repository.save(sample_document)
        sample_document.mark_status(DocumentStatus.OCR_IN_PROGRESS)
        updated = await repositories.document_repository.update(sample_document)

        assert updated.status == DocumentStatus.OCR_IN_PROGRESS

        fetched = await repositories.document_repository.get_by_id(sample_document.id)
        assert fetched is not None
        assert fetched.status == DocumentStatus.OCR_IN_PROGRESS
