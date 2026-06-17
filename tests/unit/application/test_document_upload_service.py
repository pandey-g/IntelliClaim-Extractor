"""Unit tests for document upload service."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from intelliclaim.application.services.document_upload_service import DocumentUploadService
from intelliclaim.application.services.document_validator import DocumentValidator
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.infrastructure.config.settings import Settings

MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\nendobj\n"


@pytest.mark.unit
class TestDocumentUploadService:
    @pytest.fixture
    def upload_service(self) -> DocumentUploadService:
        settings = Settings(secret_key="test-secret-key-for-pytest-runs-32chars")
        storage = AsyncMock()
        storage.store = AsyncMock(return_value="/storage/doc.pdf")
        return DocumentUploadService(
            document_repository=AsyncMock(),
            audit_log_repository=AsyncMock(),
            document_storage=storage,
            validator=DocumentValidator(settings),
        )

    async def test_upload_persists_document_and_audit_log(
        self,
        upload_service: DocumentUploadService,
    ) -> None:

        result = await upload_service.upload("claim.pdf", MINIMAL_PDF, actor="test-user")

        assert result.document_id is not None
        upload_service._document_repository.save.assert_awaited_once()  # type: ignore[attr-defined]
        upload_service._audit_log_repository.save.assert_awaited_once()  # type: ignore[attr-defined]

        saved_document = upload_service._document_repository.save.await_args[0][0]  # type: ignore[attr-defined]
        assert saved_document.document_type == DocumentType.PDF
        assert saved_document.storage_path == "/storage/doc.pdf"
