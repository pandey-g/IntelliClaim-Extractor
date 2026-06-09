"""Unit tests for domain value objects."""

import pytest
from uuid import UUID

from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId


@pytest.mark.unit
class TestDocumentId:
    def test_generate_returns_valid_uuid(self) -> None:
        doc_id = DocumentId.generate()
        assert isinstance(doc_id.value, UUID)

    def test_from_string_parses_uuid(self) -> None:
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        doc_id = DocumentId.from_string(uuid_str)
        assert str(doc_id) == uuid_str


@pytest.mark.unit
class TestConfidenceScore:
    def test_valid_score(self) -> None:
        score = ConfidenceScore(value=0.97)
        assert score.value == 0.97

    def test_from_percentage(self) -> None:
        score = ConfidenceScore.from_percentage(97.0)
        assert score.value == pytest.approx(0.97)

    def test_invalid_score_raises(self) -> None:
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            ConfidenceScore(value=1.5)


@pytest.mark.unit
class TestBoundingBox:
    def test_area_calculation(self) -> None:
        box = BoundingBox(x=10, y=20, width=100, height=50)
        assert box.area == 5000

    def test_negative_dimensions_raises(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            BoundingBox(x=0, y=0, width=-1, height=10)

    def test_to_dict(self) -> None:
        box = BoundingBox(x=1, y=2, width=3, height=4)
        assert box.to_dict() == {"x": 1, "y": 2, "width": 3, "height": 4}
