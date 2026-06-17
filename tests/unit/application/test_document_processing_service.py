"""Unit tests for document processing service."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from intelliclaim.application.services.document_processing_service import DocumentProcessingService
from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.entities.ocr_result import OCRResult
from intelliclaim.domain.enums.document_status import DocumentStatus
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.domain.exceptions.document import DocumentNotFoundError
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId

MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx"
    b"\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x05\xfe\xd4\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.mark.unit
class TestDocumentProcessingService:
    @pytest.fixture
    def document_id(self) -> DocumentId:
        return DocumentId.generate()

    @pytest.fixture
    def document(self, document_id: DocumentId) -> Document:
        return Document(
            id=document_id,
            filename="scan.png",
            content_type="image/png",
            document_type=DocumentType.PNG,
            file_size_bytes=len(MINIMAL_PNG),
            storage_path="/storage/scan.png",
        )

    @pytest.fixture
    def processing_service(self, document: Document, tmp_path) -> DocumentProcessingService:
        document_repo = AsyncMock()
        document_repo.get_by_id = AsyncMock(return_value=document)
        document_repo.update = AsyncMock(side_effect=lambda doc: doc)

        page_repo = AsyncMock()
        page_repo.save_many = AsyncMock(side_effect=lambda pages: pages)

        ocr_repo = AsyncMock()
        ocr_repo.save = AsyncMock(side_effect=lambda result: result)

        field_repo = AsyncMock()
        field_repo.save_many = AsyncMock(side_effect=lambda fields: fields)

        audit_repo = AsyncMock()

        storage = MagicMock()
        storage.retrieve = AsyncMock(return_value=MINIMAL_PNG)
        storage.get_working_directory = MagicMock(return_value=tmp_path / "working")
        storage.store_page_image = AsyncMock(return_value="/storage/page_1.png")

        page_renderer = AsyncMock()
        rendered_page = tmp_path / "rendered" / "page_1.png"
        rendered_page.parent.mkdir(parents=True, exist_ok=True)
        rendered_page.write_bytes(MINIMAL_PNG)
        page_renderer.render_pages = AsyncMock(return_value=[rendered_page])

        ocr_service = AsyncMock()
        ocr_service.extract_text = AsyncMock(
            return_value=OCRResult.create(
                document_id=document.id,
                page_number=1,
                full_text="CLAIM-123",
            )
        )

        layout_analyzer = AsyncMock()
        layout_analyzer.analyze = AsyncMock(
            return_value={
                "page_number": 1,
                "tokens": [],
                "key_value_pairs": [
                    {"key": "Claim ID", "value": "CLM-123", "confidence": 0.9}
                ],
            }
        )

        field_extractor = AsyncMock()
        field_extractor.extract = AsyncMock(
            return_value=[
                ExtractedField.create(
                    document_id=document.id,
                    field_name=ExtractionField.CLAIM_ID,
                    field_value="CLM-123",
                    confidence=ConfidenceScore(value=0.9),
                    page_number=1,
                )
            ]
        )

        return DocumentProcessingService(
            document_repository=document_repo,
            document_page_repository=page_repo,
            ocr_result_repository=ocr_repo,
            extracted_field_repository=field_repo,
            audit_log_repository=audit_repo,
            document_storage=storage,
            page_renderer=page_renderer,
            ocr_service=ocr_service,
            layout_analyzer=layout_analyzer,
            field_extractor=field_extractor,
        )

    async def test_process_document_success(
        self,
        processing_service: DocumentProcessingService,
        document_id: DocumentId,
    ) -> None:
        result = await processing_service.process_document(document_id, actor="tester")

        assert result["page_count"] == 1
        assert result["ocr_results_count"] == 1
        assert result["extracted_fields_count"] == 1
        assert result["status"] == DocumentStatus.COMPLETED.value
        processing_service._ocr_result_repository.save.assert_awaited_once()  # type: ignore[attr-defined]
        processing_service._extracted_field_repository.save_many.assert_awaited_once()  # type: ignore[attr-defined]
        processing_service._audit_log_repository.save.assert_awaited_once()  # type: ignore[attr-defined]

    async def test_process_document_not_found(
        self,
        document_id: DocumentId,
    ) -> None:
        service = DocumentProcessingService(
            document_repository=AsyncMock(get_by_id=AsyncMock(return_value=None)),
            document_page_repository=AsyncMock(),
            ocr_result_repository=AsyncMock(),
            extracted_field_repository=AsyncMock(),
            audit_log_repository=AsyncMock(),
            document_storage=MagicMock(),
            page_renderer=AsyncMock(),
            ocr_service=AsyncMock(),
            layout_analyzer=AsyncMock(),
            field_extractor=AsyncMock(),
        )
        with pytest.raises(DocumentNotFoundError):
            await service.process_document(document_id)
