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
from intelliclaim.application.interfaces.services import (
    IDocumentStorage,
    IFieldExtractor,
    IImagePreprocessor,
    ILayoutAnalyzer,
    IOCRService,
    IPageRenderer,
)
from intelliclaim.infrastructure.config.settings import Settings
from intelliclaim.infrastructure.database.session import DatabaseSessionManager
from intelliclaim.infrastructure.ocr import (
    DocumentPageRenderer,
    OpenCVImagePreprocessor,
    TesseractOCRService,
)
from intelliclaim.infrastructure.ml import InsuranceFieldExtractor, LayoutLMv3LayoutAnalyzer
from intelliclaim.infrastructure.storage import LocalDocumentStorage
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


@dataclass(frozen=True, slots=True)
class OCRBundle:
    """Collection of wired OCR pipeline adapters."""

    page_renderer: IPageRenderer
    image_preprocessor: IImagePreprocessor
    ocr_service: IOCRService


@dataclass(frozen=True, slots=True)
class ExtractionBundle:
    """Collection of wired layout and extraction adapters."""

    layout_analyzer: ILayoutAnalyzer
    field_extractor: IFieldExtractor


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


def create_document_storage(settings: Settings) -> IDocumentStorage:
    """Instantiate the local filesystem document storage adapter."""
    return LocalDocumentStorage(settings)


def create_extraction_pipeline(settings: Settings) -> ExtractionBundle:
    """Instantiate layout analysis and field extraction adapters."""
    return ExtractionBundle(
        layout_analyzer=LayoutLMv3LayoutAnalyzer(settings),
        field_extractor=InsuranceFieldExtractor(),
    )


def create_ocr_pipeline(settings: Settings) -> OCRBundle:
    """Instantiate OCR preprocessing, rendering, and extraction adapters."""
    preprocessor = OpenCVImagePreprocessor()
    page_renderer = DocumentPageRenderer()
    ocr_service = TesseractOCRService(settings, preprocessor)
    return OCRBundle(
        page_renderer=page_renderer,
        image_preprocessor=preprocessor,
        ocr_service=ocr_service,
    )
