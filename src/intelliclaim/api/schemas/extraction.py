"""Extraction-related API schemas."""

from uuid import UUID

from pydantic import BaseModel, Field


class ExtractedFieldResponse(BaseModel):
    """Single extracted field in API response."""

    field_name: str
    field_value: str
    confidence: float = Field(ge=0.0, le=1.0)
    page_number: int | None = None


class ExtractionResultsResponse(BaseModel):
    """Aggregated extraction results for a document."""

    document_id: UUID
    fields: list[ExtractedFieldResponse]
    confidence_score: float = Field(ge=0.0, le=1.0)
