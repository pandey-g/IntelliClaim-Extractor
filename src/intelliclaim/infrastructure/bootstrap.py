"""Application infrastructure bootstrap and dependency wiring."""

from dataclasses import dataclass

from intelliclaim.application.interfaces.repositories import (
    IAuditLogRepository,
    IDocumentPageRepository,
    IDocumentRepository,
    IExtractedFieldRepository,
    IOCRResultRepository,
    IProcessingJobRepository,
)
from intelliclaim.infrastructure.database.session import DatabaseSessionManager
from intelliclaim.infrastructure.repositories import (
    AuditLogRepository,
    DocumentPageRepository,
    DocumentRepository,
    ExtractedFieldRepository,
    OCRResultRepository,
    ProcessingJobRepository,
)


@dataclass(frozen=True, slots=True)
class RepositoryBundle:
    """Collection of wired repository adapters."""

    document_repository: IDocumentRepository
    document_page_repository: IDocumentPageRepository
    ocr_result_repository: IOCRResultRepository
    extracted_field_repository: IExtractedFieldRepository
    processing_job_repository: IProcessingJobRepository
    audit_log_repository: IAuditLogRepository


def create_repositories(db_manager: DatabaseSessionManager) -> RepositoryBundle:
    """Instantiate all repository adapters with a shared session factory."""
    session_factory = db_manager.session_factory
    return RepositoryBundle(
        document_repository=DocumentRepository(session_factory),
        document_page_repository=DocumentPageRepository(session_factory),
        ocr_result_repository=OCRResultRepository(session_factory),
        extracted_field_repository=ExtractedFieldRepository(session_factory),
        processing_job_repository=ProcessingJobRepository(session_factory),
        audit_log_repository=AuditLogRepository(session_factory),
    )
