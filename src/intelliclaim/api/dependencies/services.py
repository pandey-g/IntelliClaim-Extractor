"""Application service dependencies."""

from typing import Annotated

from fastapi import Depends, Request

from intelliclaim.api.dependencies.container import get_container
from intelliclaim.application.container import Container
from intelliclaim.application.services.document_processing_service import DocumentProcessingService
from intelliclaim.application.services.document_query_service import DocumentQueryService
from intelliclaim.application.services.document_upload_service import DocumentUploadService
from intelliclaim.application.services.document_validator import DocumentValidator
from intelliclaim.application.services.extraction_query_service import ExtractionQueryService
from intelliclaim.application.services.ocr_query_service import OCRQueryService
from intelliclaim.infrastructure.config.settings import Settings, get_settings


def get_app_settings(request: Request) -> Settings:
    """Retrieve settings bound to the active application instance."""
    settings = getattr(request.app.state, "settings", None)
    if settings is None:
        return get_settings()
    return settings


def get_upload_service(
    request: Request,
    container: Annotated[Container, Depends(get_container)],
) -> DocumentUploadService:
    """Provide document upload service with wired dependencies."""
    settings = get_app_settings(request)
    return DocumentUploadService(
        document_repository=container.documents,
        audit_log_repository=container.audit_logs,
        document_storage=container.document_storage_service,
        validator=DocumentValidator(settings),
    )


def get_query_service(
    container: Annotated[Container, Depends(get_container)],
) -> DocumentQueryService:
    """Provide document query service."""
    return DocumentQueryService(document_repository=container.documents)


def get_processing_service(
    container: Annotated[Container, Depends(get_container)],
) -> DocumentProcessingService:
    """Provide document processing service."""
    return DocumentProcessingService(
        document_repository=container.documents,
        document_page_repository=container.document_pages,
        ocr_result_repository=container.ocr_results,
        extracted_field_repository=container.extracted_fields,
        audit_log_repository=container.audit_logs,
        document_storage=container.document_storage_service,
        page_renderer=container.page_renderer_service,
        ocr_service=container.ocr_service_instance,
        layout_analyzer=container.layout_analyzer_service,
        field_extractor=container.field_extractor_service,
    )


def get_ocr_query_service(
    container: Annotated[Container, Depends(get_container)],
) -> OCRQueryService:
    """Provide OCR results query service."""
    return OCRQueryService(
        document_repository=container.documents,
        ocr_result_repository=container.ocr_results,
    )


def get_extraction_query_service(
    container: Annotated[Container, Depends(get_container)],
) -> ExtractionQueryService:
    """Provide extraction results query service."""
    return ExtractionQueryService(
        document_repository=container.documents,
        extracted_field_repository=container.extracted_fields,
    )
