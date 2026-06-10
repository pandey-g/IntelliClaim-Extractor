"""Unit tests for OCR result entity."""

import pytest

from intelliclaim.domain.entities.ocr_result import OCRResult, OCRWord
from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId


@pytest.mark.unit
class TestOCRResult:
    def test_create_without_words(self) -> None:
        doc_id = DocumentId.generate()
        result = OCRResult.create(doc_id, page_number=1, full_text="Hello")
        assert result.document_id == doc_id
        assert result.page_number == 1
        assert result.full_text == "Hello"
        assert result.average_confidence is None

    def test_create_with_words_computes_average_confidence(self) -> None:
        doc_id = DocumentId.generate()
        words = [
            OCRWord(
                text="Hello",
                confidence=ConfidenceScore(value=0.8),
                bounding_box=BoundingBox(x=0, y=0, width=10, height=10),
            ),
            OCRWord(
                text="World",
                confidence=ConfidenceScore(value=1.0),
                bounding_box=BoundingBox(x=10, y=0, width=10, height=10),
            ),
        ]
        result = OCRResult.create(doc_id, page_number=1, full_text="Hello World", words=words)
        assert result.average_confidence is not None
        assert result.average_confidence.value == pytest.approx(0.9)
