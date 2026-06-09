"""Immutable domain value objects."""

from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId

__all__ = ["BoundingBox", "ConfidenceScore", "DocumentId"]
