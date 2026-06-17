"""Local filesystem document storage adapter."""

from pathlib import Path

import aiofiles
import aiofiles.os

from intelliclaim.application.interfaces.services import IDocumentStorage
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.config.settings import Settings
from intelliclaim.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class LocalDocumentStorage(IDocumentStorage):
    """Stores documents on the local filesystem."""

    def __init__(self, settings: Settings) -> None:
        self._base_path = Path(settings.document_storage_path)
        self._base_path.mkdir(parents=True, exist_ok=True)

    async def store(
        self,
        document_id: DocumentId,
        filename: str,
        content: bytes,
    ) -> str:
        """Store document bytes under a document-specific directory."""
        extension = Path(filename).suffix.lower()
        document_dir = self._base_path / str(document_id)
        document_dir.mkdir(parents=True, exist_ok=True)

        storage_path = document_dir / f"original{extension}"
        async with aiofiles.open(storage_path, "wb") as file:
            await file.write(content)

        logger.info(
            "document_stored",
            document_id=str(document_id),
            storage_path=str(storage_path),
            size_bytes=len(content),
        )
        return str(storage_path)

    async def store_page_image(
        self,
        document_id: DocumentId,
        page_number: int,
        image_bytes: bytes,
    ) -> str:
        """Store a rendered page image under the document directory."""
        pages_dir = self._base_path / str(document_id) / "pages"
        pages_dir.mkdir(parents=True, exist_ok=True)

        storage_path = pages_dir / f"page_{page_number}.png"
        async with aiofiles.open(storage_path, "wb") as file:
            await file.write(image_bytes)

        return str(storage_path)

    def get_working_directory(self, document_id: DocumentId) -> Path:
        """Return scratch directory for intermediate processing artifacts."""
        working_dir = self._base_path / str(document_id) / "working"
        working_dir.mkdir(parents=True, exist_ok=True)
        return working_dir

    async def retrieve(self, storage_path: str) -> bytes:
        """Read document bytes from storage."""
        path = Path(storage_path)
        if not path.is_file():
            msg = f"Document not found at storage path: {storage_path}"
            raise FileNotFoundError(msg)

        async with aiofiles.open(path, "rb") as file:
            return await file.read()

    async def delete(self, storage_path: str) -> None:
        """Delete a stored document file."""
        path = Path(storage_path)
        if path.is_file():
            await aiofiles.os.remove(path)
            logger.info("document_deleted", storage_path=storage_path)
