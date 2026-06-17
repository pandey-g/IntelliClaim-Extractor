"""Unit tests for insurance field extractor."""

import pytest

from intelliclaim.domain.entities.ocr_result import OCRResult, OCRWord
from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.ml.field_extractor import InsuranceFieldExtractor


@pytest.mark.unit
class TestInsuranceFieldExtractor:
    @pytest.fixture
    def document_id(self) -> DocumentId:
        return DocumentId.generate()

    async def test_extract_from_layout_key_value_pairs(self, document_id: DocumentId) -> None:
        layout_data = {
            "pages": [
                {
                    "page_number": 1,
                    "key_value_pairs": [
                        {
                            "key": "Claim ID",
                            "value": "CLM-98765",
                            "confidence": 0.92,
                            "value_bbox": {"x": 1, "y": 2, "width": 3, "height": 4},
                        },
                        {
                            "key": "Policy Number",
                            "value": "POL-1122",
                            "confidence": 0.88,
                        },
                    ],
                }
            ]
        }
        ocr_results = [
            OCRResult.create(document_id=document_id, page_number=1, full_text="")
        ]

        extractor = InsuranceFieldExtractor()
        fields = await extractor.extract(document_id, layout_data, ocr_results)

        field_map = {field.field_name: field for field in fields}
        assert field_map[ExtractionField.CLAIM_ID].field_value == "CLM-98765"
        assert field_map[ExtractionField.POLICY_NUMBER].field_value == "POL-1122"

    async def test_extract_from_ocr_patterns_fallback(self, document_id: DocumentId) -> None:
        layout_data: dict[str, object] = {"pages": []}
        ocr_results = [
            OCRResult.create(
                document_id=document_id,
                page_number=1,
                full_text="Claim reference CLM-55555",
                words=[
                    OCRWord(
                        text="CLM-55555",
                        confidence=ConfidenceScore(value=0.95),
                        bounding_box=BoundingBox(x=0, y=0, width=10, height=10),
                    )
                ],
            )
        ]

        extractor = InsuranceFieldExtractor()
        fields = await extractor.extract(document_id, layout_data, ocr_results)

        assert len(fields) == 1
        assert fields[0].field_name == ExtractionField.CLAIM_ID
        assert fields[0].field_value == "CLM-55555"
