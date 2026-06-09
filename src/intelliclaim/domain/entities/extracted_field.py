"""Extracted field domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId


@dataclass
class ExtractedField:
    """A single structured field extracted from a document."""

    id: UUID
    document_id: DocumentId
    field_name: ExtractionField
    field_value: str
    confidence: ConfidenceScore
    bounding_box: BoundingBox | None = None
    page_number: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        document_id: DocumentId,
        field_name: ExtractionField,
        field_value: str,
        confidence: ConfidenceScore,
        *,
        bounding_box: BoundingBox | None = None,
        page_number: int | None = None,
    ) -> "ExtractedField":
        """Factory method for creating extracted fields."""
        return cls(
            id=uuid4(),
            document_id=document_id,
            field_name=field_name,
            field_value=field_value,
            confidence=confidence,
            bounding_box=bounding_box,
            page_number=page_number,
        )
