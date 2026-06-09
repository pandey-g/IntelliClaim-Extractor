"""Service port interfaces for external capabilities."""

from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID

from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.entities.ocr_result import OCRResult
from intelliclaim.domain.value_objects.document_id import DocumentId


class IDocumentStorage(ABC):
    """Port for document file storage."""

    @abstractmethod
    async def store(
        self,
        document_id: DocumentId,
        filename: str,
        content: bytes,
    ) -> str:
        """Store document bytes and return storage path."""

    @abstractmethod
    async def retrieve(self, storage_path: str) -> bytes:
        """Retrieve document bytes from storage."""

    @abstractmethod
    async def delete(self, storage_path: str) -> None:
        """Delete document from storage."""


class IOCRService(ABC):
    """Port for OCR execution."""

    @abstractmethod
    async def extract_text(self, image_path: Path, page_number: int) -> OCRResult:
        """Run OCR on a preprocessed page image."""


class ILayoutAnalyzer(ABC):
    """Port for layout understanding via LayoutLMv3."""

    @abstractmethod
    async def analyze(
        self,
        document_id: DocumentId,
        image_path: Path,
        ocr_result: OCRResult,
    ) -> dict[str, object]:
        """Analyze document layout and return structured tokens."""


class IFieldExtractor(ABC):
    """Port for structured field extraction."""

    @abstractmethod
    async def extract(
        self,
        document_id: DocumentId,
        layout_data: dict[str, object],
        ocr_results: list[OCRResult],
    ) -> list[ExtractedField]:
        """Extract insurance claim fields from layout and OCR data."""


class ITaskQueue(ABC):
    """Port for asynchronous task dispatch."""

    @abstractmethod
    async def enqueue_document_processing(self, document_id: DocumentId) -> str:
        """Enqueue document for background processing and return task ID."""

    @abstractmethod
    async def get_task_status(self, task_id: str) -> str:
        """Get status of a background task."""
