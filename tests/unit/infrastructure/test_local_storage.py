"""Unit tests for local document storage."""

import pytest

from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.config.settings import Settings
from intelliclaim.infrastructure.storage.local_document_storage import LocalDocumentStorage

MINIMAL_PDF = b"%PDF-1.4\ncontent"


@pytest.mark.unit
class TestLocalDocumentStorage:
    @pytest.fixture
    def storage(self, tmp_path) -> LocalDocumentStorage:
        settings = Settings(
            secret_key="test-secret-key-for-pytest-runs-32chars",
            document_storage_path=str(tmp_path / "documents"),
        )
        return LocalDocumentStorage(settings)

    async def test_store_and_retrieve(self, storage: LocalDocumentStorage) -> None:
        doc_id = DocumentId.generate()
        path = await storage.store(doc_id, "claim.pdf", MINIMAL_PDF)

        content = await storage.retrieve(path)
        assert content == MINIMAL_PDF

    async def test_store_page_image(self, storage: LocalDocumentStorage) -> None:
        doc_id = DocumentId.generate()
        page_bytes = b"\x89PNG\r\n\x1a\n"
        path = await storage.store_page_image(doc_id, page_number=1, image_bytes=page_bytes)
        assert "pages/page_1.png" in path
        content = await storage.retrieve(path)
        assert content == page_bytes

    async def test_get_working_directory(self, storage: LocalDocumentStorage) -> None:
        doc_id = DocumentId.generate()
        working_dir = storage.get_working_directory(doc_id)
        assert working_dir.is_dir()
        assert str(doc_id) in str(working_dir)

    async def test_delete(self, storage: LocalDocumentStorage) -> None:
        doc_id = DocumentId.generate()
        path = await storage.store(doc_id, "claim.pdf", MINIMAL_PDF)

        await storage.delete(path)
        with pytest.raises(FileNotFoundError):
            await storage.retrieve(path)
