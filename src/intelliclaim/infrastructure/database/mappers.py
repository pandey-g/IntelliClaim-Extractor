"""Mappers between domain entities and ORM models."""

from typing import Any

from intelliclaim.domain.entities.audit_log import AuditLog
from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.entities.document_page import DocumentPage
from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.entities.ocr_result import OCRResult, OCRWord
from intelliclaim.domain.entities.processing_job import ProcessingJob
from intelliclaim.domain.enums.document_status import DocumentStatus
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.domain.enums.job_status import JobStatus
from intelliclaim.domain.value_objects.bounding_box import BoundingBox
from intelliclaim.domain.value_objects.confidence_score import ConfidenceScore
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.database.models.audit_log import AuditLogModel
from intelliclaim.infrastructure.database.models.document import DocumentModel
from intelliclaim.infrastructure.database.models.document_page import DocumentPageModel
from intelliclaim.infrastructure.database.models.extracted_field import ExtractedFieldModel
from intelliclaim.infrastructure.database.models.ocr_result import OCRResultModel
from intelliclaim.infrastructure.database.models.processing_job import ProcessingJobModel


def document_to_domain(model: DocumentModel) -> Document:
    """Map ORM document model to domain entity."""
    return Document(
        id=DocumentId(model.id),
        filename=model.filename,
        content_type=model.content_type,
        document_type=DocumentType(model.document_type),
        file_size_bytes=model.file_size_bytes,
        storage_path=model.storage_path,
        status=DocumentStatus(model.status),
        page_count=model.page_count,
        created_at=model.created_at,
        updated_at=model.updated_at,
        error_message=model.error_message,
    )


def document_to_model(entity: Document) -> DocumentModel:
    """Map domain document entity to ORM model."""
    return DocumentModel(
        id=entity.id.value,
        filename=entity.filename,
        content_type=entity.content_type,
        document_type=entity.document_type.value,
        file_size_bytes=entity.file_size_bytes,
        storage_path=entity.storage_path,
        status=entity.status.value,
        page_count=entity.page_count,
        error_message=entity.error_message,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def update_document_model(model: DocumentModel, entity: Document) -> None:
    """Update ORM document model from domain entity."""
    model.filename = entity.filename
    model.content_type = entity.content_type
    model.document_type = entity.document_type.value
    model.file_size_bytes = entity.file_size_bytes
    model.storage_path = entity.storage_path
    model.status = entity.status.value
    model.page_count = entity.page_count
    model.error_message = entity.error_message
    model.updated_at = entity.updated_at


def document_page_to_domain(model: DocumentPageModel) -> DocumentPage:
    """Map ORM document page model to domain entity."""
    return DocumentPage(
        id=model.id,
        document_id=DocumentId(model.document_id),
        page_number=model.page_number,
        storage_path=model.storage_path,
        width=model.width,
        height=model.height,
        created_at=model.created_at,
    )


def document_page_to_model(entity: DocumentPage) -> DocumentPageModel:
    """Map domain document page entity to ORM model."""
    return DocumentPageModel(
        id=entity.id,
        document_id=entity.document_id.value,
        page_number=entity.page_number,
        storage_path=entity.storage_path,
        width=entity.width,
        height=entity.height,
        created_at=entity.created_at,
    )


def _word_to_dict(word: OCRWord) -> dict[str, Any]:
    return {
        "text": word.text,
        "confidence": word.confidence.value,
        "bounding_box": word.bounding_box.to_dict(),
    }


def _word_from_dict(data: dict[str, Any]) -> OCRWord:
    bbox = data["bounding_box"]
    return OCRWord(
        text=data["text"],
        confidence=ConfidenceScore(value=data["confidence"]),
        bounding_box=BoundingBox(
            x=bbox["x"],
            y=bbox["y"],
            width=bbox["width"],
            height=bbox["height"],
        ),
    )


def ocr_result_to_domain(model: OCRResultModel) -> OCRResult:
    """Map ORM OCR result model to domain entity."""
    words = [_word_from_dict(w) for w in model.words]
    avg_confidence = (
        ConfidenceScore(value=model.average_confidence)
        if model.average_confidence is not None
        else None
    )
    return OCRResult(
        id=model.id,
        document_id=DocumentId(model.document_id),
        page_number=model.page_number,
        full_text=model.full_text,
        words=words,
        average_confidence=avg_confidence,
        created_at=model.created_at,
    )


def ocr_result_to_model(entity: OCRResult) -> OCRResultModel:
    """Map domain OCR result entity to ORM model."""
    return OCRResultModel(
        id=entity.id,
        document_id=entity.document_id.value,
        page_number=entity.page_number,
        full_text=entity.full_text,
        words=[_word_to_dict(w) for w in entity.words],
        average_confidence=entity.average_confidence.value if entity.average_confidence else None,
        created_at=entity.created_at,
    )


def extracted_field_to_domain(model: ExtractedFieldModel) -> ExtractedField:
    """Map ORM extracted field model to domain entity."""
    bounding_box: BoundingBox | None = None
    if model.bbox_x is not None and model.bbox_y is not None:
        bounding_box = BoundingBox(
            x=model.bbox_x,
            y=model.bbox_y,
            width=model.bbox_width or 0,
            height=model.bbox_height or 0,
        )
    return ExtractedField(
        id=model.id,
        document_id=DocumentId(model.document_id),
        field_name=ExtractionField(model.field_name),
        field_value=model.field_value,
        confidence=ConfidenceScore(value=model.confidence),
        bounding_box=bounding_box,
        page_number=model.page_number,
        created_at=model.created_at,
    )


def extracted_field_to_model(entity: ExtractedField) -> ExtractedFieldModel:
    """Map domain extracted field entity to ORM model."""
    bbox = entity.bounding_box
    return ExtractedFieldModel(
        id=entity.id,
        document_id=entity.document_id.value,
        field_name=entity.field_name.value,
        field_value=entity.field_value,
        confidence=entity.confidence.value,
        bbox_x=bbox.x if bbox else None,
        bbox_y=bbox.y if bbox else None,
        bbox_width=bbox.width if bbox else None,
        bbox_height=bbox.height if bbox else None,
        page_number=entity.page_number,
        created_at=entity.created_at,
    )


def processing_job_to_domain(model: ProcessingJobModel) -> ProcessingJob:
    """Map ORM processing job model to domain entity."""
    return ProcessingJob(
        id=model.id,
        document_id=DocumentId(model.document_id),
        status=JobStatus(model.status),
        celery_task_id=model.celery_task_id,
        retry_count=model.retry_count,
        error_message=model.error_message,
        started_at=model.started_at,
        completed_at=model.completed_at,
        created_at=model.created_at,
    )


def processing_job_to_model(entity: ProcessingJob) -> ProcessingJobModel:
    """Map domain processing job entity to ORM model."""
    return ProcessingJobModel(
        id=entity.id,
        document_id=entity.document_id.value,
        status=entity.status.value,
        celery_task_id=entity.celery_task_id,
        retry_count=entity.retry_count,
        error_message=entity.error_message,
        started_at=entity.started_at,
        completed_at=entity.completed_at,
        created_at=entity.created_at,
    )


def update_processing_job_model(model: ProcessingJobModel, entity: ProcessingJob) -> None:
    """Update ORM processing job model from domain entity."""
    model.status = entity.status.value
    model.celery_task_id = entity.celery_task_id
    model.retry_count = entity.retry_count
    model.error_message = entity.error_message
    model.started_at = entity.started_at
    model.completed_at = entity.completed_at


def audit_log_to_domain(model: AuditLogModel) -> AuditLog:
    """Map ORM audit log model to domain entity."""
    return AuditLog(
        id=model.id,
        action=model.action,
        actor=model.actor,
        document_id=DocumentId(model.document_id) if model.document_id else None,
        details=model.details,
        created_at=model.created_at,
    )


def audit_log_to_model(entity: AuditLog) -> AuditLogModel:
    """Map domain audit log entity to ORM model."""
    return AuditLogModel(
        id=entity.id,
        document_id=entity.document_id.value if entity.document_id else None,
        action=entity.action,
        actor=entity.actor,
        details=entity.details,
        created_at=entity.created_at,
    )
