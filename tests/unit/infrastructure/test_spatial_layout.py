"""Unit tests for spatial layout utilities."""

import pytest

from intelliclaim.domain.entities.ocr_result import OCRWord
from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.infrastructure.ml.spatial_layout import (
    detect_key_value_pairs,
    group_words_into_lines,
    normalize_box,
    words_to_tokens,
)


def _word(text: str, x: int, y: int, width: int = 50, height: int = 12) -> OCRWord:
    return OCRWord(
        text=text,
        confidence=ConfidenceScore(value=0.9),
        bounding_box=BoundingBox(x=x, y=y, width=width, height=height),
    )


@pytest.mark.unit
class TestSpatialLayout:
    def test_normalize_box_scales_to_layoutlm_range(self) -> None:
        box = BoundingBox(x=100, y=50, width=200, height=100)
        normalized = normalize_box(box, page_width=1000, page_height=500)
        assert normalized == [100, 100, 300, 300]

    def test_group_words_into_lines(self) -> None:
        words = [
            _word("Claim", 10, 20),
            _word("ID:", 70, 22),
            _word("CLM-123", 200, 20),
            _word("Policy", 10, 80),
        ]
        lines = group_words_into_lines(words)
        assert len(lines) == 2
        assert len(lines[0]) == 3

    def test_detect_key_value_pairs_from_colon(self) -> None:
        words = [
            _word("Claim", 10, 20),
            _word("ID:", 70, 20),
            _word("CLM-12345", 200, 20),
        ]
        pairs = detect_key_value_pairs(
            words,
            page_number=1,
            page_width=400,
            page_height=120,
        )
        assert len(pairs) == 1
        assert pairs[0]["key"] == "Claim ID"
        assert pairs[0]["value"] == "CLM-12345"

    def test_detect_key_value_pairs_from_columns(self) -> None:
        words = [
            _word("Policy", 20, 40),
            _word("Number", 80, 40),
            _word("POL-9988", 260, 40),
        ]
        pairs = detect_key_value_pairs(
            words,
            page_number=1,
            page_width=400,
            page_height=120,
        )
        assert len(pairs) == 1
        assert "Policy" in str(pairs[0]["key"])
        assert pairs[0]["value"] == "POL-9988"

    def test_words_to_tokens_includes_normalized_bbox(self) -> None:
        words = [_word("CLM-1", 10, 10)]
        tokens = words_to_tokens(words, page_number=1, page_width=200, page_height=100)
        assert tokens[0]["text"] == "CLM-1"
        assert "normalized_bbox" in tokens[0]
