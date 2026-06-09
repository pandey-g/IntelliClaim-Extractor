"""Repository port interfaces."""

from abc import ABC, abstractmethod
from uuid import UUID

from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.entities.ocr_result import OCRResult
from intelliclaim.domain.entities.processing_job import ProcessingJob
from intelliclaim.domain.value_objects.document_id import DocumentId


class IDocumentRepository(ABC):
    """Persistence port for documents."""

    @abstractmethod
    async def save(self, document: Document) -> Document:
        """Persist a new or updated document."""

    @abstractmethod
    async def get_by_id(self, document_id: DocumentId) -> Document | None:
        """Retrieve document by identifier."""

    @abstractmethod
    async def update(self, document: Document) -> Document:
        """Update an existing document."""


class IOCRResultRepository(ABC):
    """Persistence port for OCR results."""

    @abstractmethod
    async def save(self, result: OCRResult) -> OCRResult:
        """Persist OCR result."""

    @abstractmethod
    async def get_by_document_id(self, document_id: DocumentId) -> list[OCRResult]:
        """Retrieve all OCR results for a document."""


class IExtractedFieldRepository(ABC):
    """Persistence port for extracted fields."""

    @abstractmethod
    async def save_many(self, fields: list[ExtractedField]) -> list[ExtractedField]:
        """Persist multiple extracted fields."""

    @abstractmethod
    async def get_by_document_id(self, document_id: DocumentId) -> list[ExtractedField]:
        """Retrieve all extracted fields for a document."""


class IProcessingJobRepository(ABC):
    """Persistence port for processing jobs."""

    @abstractmethod
    async def save(self, job: ProcessingJob) -> ProcessingJob:
        """Persist a processing job."""

    @abstractmethod
    async def get_by_id(self, job_id: UUID) -> ProcessingJob | None:
        """Retrieve job by identifier."""

    @abstractmethod
    async def get_by_document_id(self, document_id: DocumentId) -> ProcessingJob | None:
        """Retrieve the latest job for a document."""

    @abstractmethod
    async def update(self, job: ProcessingJob) -> ProcessingJob:
        """Update an existing processing job."""
