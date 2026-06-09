"""Domain entities."""

from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.entities.ocr_result import OCRResult
from intelliclaim.domain.entities.processing_job import ProcessingJob

__all__ = ["Document", "ExtractedField", "OCRResult", "ProcessingJob"]
