"""Document API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from intelliclaim.domain.enums.document_status import DocumentStatus


class DocumentUploadResponse(BaseModel):
    """Response after successful document upload."""

    document_id: UUID = Field(examples=["550e8400-e29b-41d4-a716-446655440000"])


class DocumentDetailResponse(BaseModel):
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


class DocumentStatusResponse(BaseModel):
    """Document processing status response."""

    document_id: UUID
    status: DocumentStatus
    updated_at: datetime
    error_message: str | None = None
