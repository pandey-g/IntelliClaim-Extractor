"""SQLAlchemy repository adapters."""

from intelliclaim.infrastructure.repositories.audit_log_repository import AuditLogRepository
from intelliclaim.infrastructure.repositories.document_page_repository import DocumentPageRepository
from intelliclaim.infrastructure.repositories.document_repository import DocumentRepository
from intelliclaim.infrastructure.repositories.extracted_field_repository import (
    ExtractedFieldRepository,
)
from intelliclaim.infrastructure.repositories.ocr_result_repository import OCRResultRepository
from intelliclaim.infrastructure.repositories.processing_job_repository import (
    ProcessingJobRepository,
)

__all__ = [
    "AuditLogRepository",
    "DocumentPageRepository",
    "DocumentRepository",
    "ExtractedFieldRepository",
    "OCRResultRepository",
    "ProcessingJobRepository",
]
