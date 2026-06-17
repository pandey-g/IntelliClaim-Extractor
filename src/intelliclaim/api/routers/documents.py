"""Document upload and query endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Request, UploadFile, status

from intelliclaim.api.dependencies.auth import get_current_actor
from intelliclaim.api.dependencies.services import (
    get_app_settings,
    get_extraction_query_service,
    get_ocr_query_service,
    get_processing_service,
    get_query_service,
    get_upload_service,
)
from intelliclaim.api.schemas.document import (
    DocumentDetailResponse,
    DocumentStatusResponse,
    DocumentUploadResponse,
)
from intelliclaim.api.schemas.extraction import ExtractionResultsResponse, ExtractedFieldResponse
from intelliclaim.api.schemas.ocr import OCRPageResultResponse, OCRResultsResponse, ProcessDocumentResponse
from intelliclaim.application.services.document_processing_service import DocumentProcessingService
from intelliclaim.application.services.document_query_service import DocumentQueryService
from intelliclaim.application.services.document_upload_service import DocumentUploadService
from intelliclaim.application.services.extraction_query_service import ExtractionQueryService
from intelliclaim.application.services.ocr_query_service import OCRQueryService
from intelliclaim.domain.enums.document_status import DocumentStatus
from intelliclaim.domain.exceptions.document import InvalidDocumentError
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.config.settings import Settings

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document",
    description="Upload a PDF or image document for processing.",
)
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF, PNG, JPG, or TIFF file")],
    actor: Annotated[str, Depends(get_current_actor)],
    upload_service: Annotated[DocumentUploadService, Depends(get_upload_service)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> DocumentUploadResponse:
    """Accept and store an insurance claim document."""
    if file.filename is None:
        raise InvalidDocumentError("Filename is required")

    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise InvalidDocumentError(
            f"File exceeds maximum size of {settings.max_upload_size_mb} MB"
        )

    result = await upload_service.upload(file.filename, content, actor=actor)
    return DocumentUploadResponse(document_id=result.document_id)


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Get document metadata",
)
async def get_document(
    document_id: UUID,
    actor: Annotated[str, Depends(get_current_actor)],
    query_service: Annotated[DocumentQueryService, Depends(get_query_service)],
) -> DocumentDetailResponse:
    """Retrieve document metadata by identifier."""
    del actor
    result = await query_service.get_document(DocumentId.from_string(str(document_id)))
    return DocumentDetailResponse(**result.model_dump())


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
    summary="Get document processing status",
)
async def get_document_status(
    document_id: UUID,
    actor: Annotated[str, Depends(get_current_actor)],
    query_service: Annotated[DocumentQueryService, Depends(get_query_service)],
) -> DocumentStatusResponse:
    """Retrieve current processing status for a document."""
    del actor
    result = await query_service.get_status(DocumentId.from_string(str(document_id)))
    return DocumentStatusResponse(**result.model_dump())


@router.post(
    "/{document_id}/process",
    response_model=ProcessDocumentResponse,
    summary="Process document",
    description="Synchronously preprocess document pages, run OCR, and extract fields.",
)
async def process_document(
    document_id: UUID,
    actor: Annotated[str, Depends(get_current_actor)],
    processing_service: Annotated[DocumentProcessingService, Depends(get_processing_service)],
) -> ProcessDocumentResponse:
    """Run preprocessing, OCR, layout analysis, and extraction pipeline."""
    result = await processing_service.process_document(
        DocumentId.from_string(str(document_id)),
        actor=actor,
    )
    return ProcessDocumentResponse(
        document_id=result["document_id"],  # type: ignore[arg-type]
        status=DocumentStatus(result["status"]),  # type: ignore[arg-type]
        page_count=result["page_count"],  # type: ignore[arg-type]
        ocr_results_count=result["ocr_results_count"],  # type: ignore[arg-type]
        extracted_fields_count=result.get("extracted_fields_count", 0),  # type: ignore[arg-type]
    )


@router.get(
    "/{document_id}/extractions",
    response_model=ExtractionResultsResponse,
    summary="Get extracted fields",
)
async def get_extractions(
    document_id: UUID,
    actor: Annotated[str, Depends(get_current_actor)],
    extraction_query_service: Annotated[ExtractionQueryService, Depends(get_extraction_query_service)],
) -> ExtractionResultsResponse:
    """Retrieve structured field extraction results for a document."""
    del actor
    result = await extraction_query_service.get_extractions(
        DocumentId.from_string(str(document_id))
    )
    return ExtractionResultsResponse(
        document_id=result.document_id,
        fields=[ExtractedFieldResponse(**field.model_dump()) for field in result.fields],
        confidence_score=result.confidence_score,
    )


@router.get(
    "/{document_id}/ocr",
    response_model=OCRResultsResponse,
    summary="Get OCR results",
)
async def get_ocr_results(
    document_id: UUID,
    actor: Annotated[str, Depends(get_current_actor)],
    ocr_query_service: Annotated[OCRQueryService, Depends(get_ocr_query_service)],
) -> OCRResultsResponse:
    """Retrieve OCR extraction results for a document."""
    del actor
    pages = await ocr_query_service.get_ocr_results(DocumentId.from_string(str(document_id)))
    return OCRResultsResponse(
        document_id=document_id,
        pages=[OCRPageResultResponse(**page) for page in pages],  # type: ignore[arg-type]
    )
