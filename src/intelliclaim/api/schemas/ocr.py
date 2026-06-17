"""OCR-related API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field

from intelliclaim.domain.enums.document_status import DocumentStatus


class ProcessDocumentResponse(BaseModel):
    """Response after synchronous document processing."""

    document_id: UUID
    status: DocumentStatus
    page_count: int
    ocr_results_count: int = Field(ge=0)
    extracted_fields_count: int = Field(default=0, ge=0)


class OCRWordResponse(BaseModel):
    """Single OCR word in API response."""

    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    x: int
    y: int
    width: int
    height: int


class OCRPageResultResponse(BaseModel):
    """OCR output for a single page."""

    page_number: int
    full_text: str
    average_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    words: list[OCRWordResponse]


class OCRResultsResponse(BaseModel):
    """All OCR results for a document."""

    document_id: UUID
    pages: list[OCRPageResultResponse]
