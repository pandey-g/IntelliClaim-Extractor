"""Document-related DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from intelliclaim.domain.enums.document_status import DocumentStatus


class DocumentUploadDTO(BaseModel):
    """Response after successful document upload."""

    document_id: UUID


class DocumentResponseDTO(BaseModel):
    """Full document metadata response."""

    document_id: UUID
    filename: str
    content_type: str
    document_type: str
    file_size_bytes: int
    status: DocumentStatus
    page_count: int
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None


class DocumentStatusDTO(BaseModel):
    """Document processing status response."""

    document_id: UUID
    status: DocumentStatus
    updated_at: datetime
    error_message: str | None = None


class ExtractedFieldDTO(BaseModel):
    """Single extracted field in API response."""

    field_name: str
    field_value: str
    confidence: float = Field(ge=0.0, le=1.0)
    page_number: int | None = None


class ExtractionResponseDTO(BaseModel):
    """Aggregated extraction results for a document."""

    document_id: UUID
    fields: list[ExtractedFieldDTO]
    confidence_score: float = Field(ge=0.0, le=1.0)
