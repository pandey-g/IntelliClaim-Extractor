"""Integration tests for processing-related repositories."""

import pytest

from intelliclaim.domain.entities.audit_log import AuditLog
from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.entities.document_page import DocumentPage
from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.entities.ocr_result import OCRResult, OCRWord
from intelliclaim.domain.entities.processing_job import ProcessingJob
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.domain.enums.job_status import JobStatus
from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId


@pytest.mark.integration
class TestProcessingPipelineRepositories:
    @pytest.fixture
    async def document(self, repositories) -> Document:
        doc = Document(
            id=DocumentId.generate(),
            filename="invoice.png",
            content_type="image/png",
            document_type=DocumentType.PNG,
            file_size_bytes=512,
            storage_path="/storage/invoice.png",
        )
        return await repositories.document_repository.save(doc)

    async def test_document_pages_round_trip(self, repositories, document: Document) -> None:
        pages = [
            DocumentPage.create(
                document_id=document.id,
                page_number=1,
                storage_path="/storage/invoice_page_1.png",
                width=800,
                height=600,
            )
        ]
        saved = await repositories.document_page_repository.save_many(pages)
        assert len(saved) == 1

        fetched = await repositories.document_page_repository.get_by_document_id(document.id)
        assert len(fetched) == 1
        assert fetched[0].page_number == 1
        assert fetched[0].width == 800

    async def test_ocr_results_round_trip(self, repositories, document: Document) -> None:
        result = OCRResult.create(
            document_id=document.id,
            page_number=1,
            full_text="CLM-12345 John Doe",
            words=[
                OCRWord(
                    text="CLM-12345",
                    confidence=ConfidenceScore(value=0.95),
                    bounding_box=BoundingBox(x=10, y=20, width=100, height=20),
                )
            ],
        )
        saved = await repositories.ocr_result_repository.save(result)
        assert saved.average_confidence is not None

        fetched = await repositories.ocr_result_repository.get_by_document_id(document.id)
        assert len(fetched) == 1
        assert fetched[0].full_text == "CLM-12345 John Doe"
        assert len(fetched[0].words) == 1

    async def test_extracted_fields_round_trip(self, repositories, document: Document) -> None:
        fields = [
            ExtractedField.create(
                document_id=document.id,
                field_name=ExtractionField.CLAIM_ID,
                field_value="CLM-12345",
                confidence=ConfidenceScore(value=0.97),
            ),
            ExtractedField.create(
                document_id=document.id,
                field_name=ExtractionField.CLAIM_AMOUNT,
                field_value="15000.50",
                confidence=ConfidenceScore(value=0.92),
            ),
        ]
        saved = await repositories.extracted_field_repository.save_many(fields)
        assert len(saved) == 2

        fetched = await repositories.extracted_field_repository.get_by_document_id(document.id)
        assert len(fetched) == 2
        field_names = {field.field_name for field in fetched}
        assert ExtractionField.CLAIM_ID in field_names
        assert ExtractionField.CLAIM_AMOUNT in field_names

    async def test_processing_job_lifecycle(self, repositories, document: Document) -> None:
        job = ProcessingJob.create(document.id)
        saved = await repositories.processing_job_repository.save(job)
        assert saved.status == JobStatus.QUEUED

        saved.mark_running("celery-task-abc")
        updated = await repositories.processing_job_repository.update(saved)
        assert updated.status == JobStatus.RUNNING
        assert updated.celery_task_id == "celery-task-abc"

        latest = await repositories.processing_job_repository.get_by_document_id(document.id)
        assert latest is not None
        assert latest.id == saved.id

    async def test_audit_log_round_trip(self, repositories, document: Document) -> None:
        entry = AuditLog.create(
            action="document.uploaded",
            actor="api-client",
            document_id=document.id,
            details={"filename": document.filename},
        )
        saved = await repositories.audit_log_repository.save(entry)
        assert saved.action == "document.uploaded"

        logs = await repositories.audit_log_repository.get_by_document_id(document.id)
        assert len(logs) == 1
        assert logs[0].details["filename"] == document.filename
