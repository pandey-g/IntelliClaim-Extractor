"""Document processing lifecycle states."""

from enum import StrEnum


class DocumentStatus(StrEnum):
    """Represents the lifecycle state of a document in the processing pipeline."""

    PENDING = "pending"
    PREPROCESSING = "preprocessing"
    OCR_IN_PROGRESS = "ocr_in_progress"
    LAYOUT_ANALYSIS = "layout_analysis"
    EXTRACTION = "extraction"
    VALIDATION = "validation"
    COMPLETED = "completed"
    FAILED = "failed"
