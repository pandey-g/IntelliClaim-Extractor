"""OCR result domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId


@dataclass
class OCRWord:
    """Single word recognized by OCR."""

    text: str
    confidence: ConfidenceScore
    bounding_box: BoundingBox


@dataclass
class OCRResult:
    """OCR output for a single document page."""

    id: UUID
    document_id: DocumentId
    page_number: int
    full_text: str
    words: list[OCRWord] = field(default_factory=list)
    average_confidence: ConfidenceScore | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        document_id: DocumentId,
        page_number: int,
        full_text: str,
        words: list[OCRWord] | None = None,
    ) -> "OCRResult":
        """Factory method for creating OCR results."""
        word_list = words or []
        avg_confidence: ConfidenceScore | None = None
        if word_list:
            avg_value = sum(w.confidence.value for w in word_list) / len(word_list)
            avg_confidence = ConfidenceScore(value=avg_value)
        return cls(
            id=uuid4(),
            document_id=document_id,
            page_number=page_number,
            full_text=full_text,
            words=word_list,
            average_confidence=avg_confidence,
        )
