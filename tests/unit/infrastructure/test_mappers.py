"""Unit tests for ORM mappers."""

import pytest

from intelliclaim.domain.entities.audit_log import AuditLog
from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.entities.ocr_result import OCRResult, OCRWord
from intelliclaim.domain.entities.processing_job import ProcessingJob
from intelliclaim.domain.enums.document_status import DocumentStatus
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.database.mappers import (
    audit_log_to_domain,
    audit_log_to_model,
    document_to_domain,
    document_to_model,
    extracted_field_to_domain,
    extracted_field_to_model,
    ocr_result_to_domain,
    ocr_result_to_model,
    processing_job_to_domain,
    processing_job_to_model,
)


@pytest.mark.unit
class TestMappers:
    def test_document_round_trip(self) -> None:
        entity = Document(
            id=DocumentId.generate(),
            filename="test.pdf",
            content_type="application/pdf",
            document_type=DocumentType.PDF,
            file_size_bytes=100,
            storage_path="/tmp/test.pdf",
            status=DocumentStatus.PENDING,
        )
        model = document_to_model(entity)
        restored = document_to_domain(model)
        assert restored.filename == entity.filename
        assert restored.status == entity.status

    def test_ocr_result_round_trip(self) -> None:
        doc_id = DocumentId.generate()
        entity = OCRResult.create(
            document_id=doc_id,
            page_number=1,
            full_text="hello",
            words=[
                OCRWord(
                    text="hello",
                    confidence=ConfidenceScore(value=0.9),
                    bounding_box=BoundingBox(x=1, y=2, width=3, height=4),
                )
            ],
        )
        model = ocr_result_to_model(entity)
        restored = ocr_result_to_domain(model)
        assert restored.full_text == "hello"
        assert len(restored.words) == 1
        assert restored.words[0].bounding_box.width == 3

    def test_extracted_field_round_trip(self) -> None:
        entity = ExtractedField.create(
            document_id=DocumentId.generate(),
            field_name=ExtractionField.POLICY_NUMBER,
            field_value="POL-998877",
            confidence=ConfidenceScore(value=0.88),
            bounding_box=BoundingBox(x=5, y=5, width=50, height=10),
        )
        model = extracted_field_to_model(entity)
        restored = extracted_field_to_domain(model)
        assert restored.field_value == "POL-998877"
        assert restored.bounding_box is not None
        assert restored.bounding_box.width == 50

    def test_processing_job_round_trip(self) -> None:
        entity = ProcessingJob.create(DocumentId.generate())
        model = processing_job_to_model(entity)
        restored = processing_job_to_domain(model)
        assert restored.id == entity.id

    def test_audit_log_round_trip(self) -> None:
        doc_id = DocumentId.generate()
        entity = AuditLog.create(
            action="document.processed",
            actor="worker",
            document_id=doc_id,
            details={"status": "completed"},
        )
        model = audit_log_to_model(entity)
        restored = audit_log_to_domain(model)
        assert restored.document_id == doc_id
        assert restored.details["status"] == "completed"
