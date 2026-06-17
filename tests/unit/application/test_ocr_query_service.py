"""Unit tests for OCR query service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from intelliclaim.application.services.ocr_query_service import OCRQueryService
from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.entities.ocr_result import OCRResult, OCRWord
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.exceptions.document import DocumentNotFoundError
from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId


@pytest.mark.unit
class TestOCRQueryService:
    @pytest.fixture
    def document_id(self) -> DocumentId:
        return DocumentId.generate()

    async def test_get_ocr_results(self, document_id: DocumentId) -> None:
        document = Document(
            id=document_id,
            filename="claim.png",
            content_type="image/png",
            document_type=DocumentType.PNG,
            file_size_bytes=100,
            storage_path="/storage/claim.png",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        ocr_result = OCRResult.create(
            document_id=document_id,
            page_number=1,
            full_text="CLM-12345",
            words=[
                OCRWord(
                    text="CLM-12345",
                    confidence=ConfidenceScore(value=0.95),
                    bounding_box=BoundingBox(x=1, y=2, width=3, height=4),
                )
            ],
        )

        doc_repo = AsyncMock()
        doc_repo.get_by_id = AsyncMock(return_value=document)
        ocr_repo = AsyncMock()
        ocr_repo.get_by_document_id = AsyncMock(return_value=[ocr_result])

        service = OCRQueryService(doc_repo, ocr_repo)
        pages = await service.get_ocr_results(document_id)

        assert len(pages) == 1
        assert pages[0]["full_text"] == "CLM-12345"
        assert pages[0]["words"][0]["text"] == "CLM-12345"

    async def test_get_ocr_results_not_found(self, document_id: DocumentId) -> None:
        service = OCRQueryService(
            AsyncMock(get_by_id=AsyncMock(return_value=None)),
            AsyncMock(),
        )
        with pytest.raises(DocumentNotFoundError):
            await service.get_ocr_results(document_id)
