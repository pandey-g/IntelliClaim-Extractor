"""Domain entities."""

from intelliclaim.domain.entities.audit_log import AuditLog
from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.entities.document_page import DocumentPage
from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.entities.ocr_result import OCRResult
from intelliclaim.domain.entities.processing_job import ProcessingJob

__all__ = [
    "AuditLog",
    "Document",
    "DocumentPage",
    "ExtractedField",
    "OCRResult",
    "ProcessingJob",
]
