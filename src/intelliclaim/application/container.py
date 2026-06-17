"""Dependency injection container."""

from dataclasses import dataclass, field

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
    ITaskQueue,
)
from intelliclaim.infrastructure.config.settings import Settings


@dataclass
class Container:
    """Application-wide dependency container.

    Infrastructure adapters are wired at startup. Application services
    depend only on port interfaces defined in the application layer.
    """

    settings: Settings
    document_repository: IDocumentRepository | None = None
    document_page_repository: IDocumentPageRepository | None = None
    ocr_result_repository: IOCRResultRepository | None = None
    extracted_field_repository: IExtractedFieldRepository | None = None
    processing_job_repository: IProcessingJobRepository | None = None
    audit_log_repository: IAuditLogRepository | None = None
    document_storage: IDocumentStorage | None = None
    page_renderer: IPageRenderer | None = None
    image_preprocessor: IImagePreprocessor | None = None
    ocr_service: IOCRService | None = None
    layout_analyzer: ILayoutAnalyzer | None = None
    field_extractor: IFieldExtractor | None = None
    task_queue: ITaskQueue | None = None
    _repos_initialized: bool = field(default=False, repr=False)
    _storage_initialized: bool = field(default=False, repr=False)
    _ocr_initialized: bool = field(default=False, repr=False)
    _extraction_initialized: bool = field(default=False, repr=False)
    _initialized: bool = field(default=False, repr=False)

    def wire_repositories(
        self,
        *,
        document_repository: IDocumentRepository,
        document_page_repository: IDocumentPageRepository,
        ocr_result_repository: IOCRResultRepository,
        extracted_field_repository: IExtractedFieldRepository,
        processing_job_repository: IProcessingJobRepository,
        audit_log_repository: IAuditLogRepository,
    ) -> None:
        """Wire persistence adapters into the container."""
        self.document_repository = document_repository
        self.document_page_repository = document_page_repository
        self.ocr_result_repository = ocr_result_repository
        self.extracted_field_repository = extracted_field_repository
        self.processing_job_repository = processing_job_repository
        self.audit_log_repository = audit_log_repository
        self._repos_initialized = True

    def wire_storage(self, *, document_storage: IDocumentStorage) -> None:
        """Wire document storage adapter into the container."""
        self.document_storage = document_storage
        self._storage_initialized = True

    def wire_ocr(
        self,
        *,
        page_renderer: IPageRenderer,
        image_preprocessor: IImagePreprocessor,
        ocr_service: IOCRService,
    ) -> None:
        """Wire OCR pipeline adapters into the container."""
        self.page_renderer = page_renderer
        self.image_preprocessor = image_preprocessor
        self.ocr_service = ocr_service
        self._ocr_initialized = True

    def wire_extraction(
        self,
        *,
        layout_analyzer: ILayoutAnalyzer,
        field_extractor: IFieldExtractor,
    ) -> None:
        """Wire layout analysis and field extraction adapters into the container."""
        self.layout_analyzer = layout_analyzer
        self.field_extractor = field_extractor
        self._extraction_initialized = True

    def wire_services(
        self,
        *,
        layout_analyzer: ILayoutAnalyzer,
        field_extractor: IFieldExtractor,
        task_queue: ITaskQueue,
    ) -> None:
        """Wire downstream processing service adapters into the container."""
        self.wire_extraction(
            layout_analyzer=layout_analyzer,
            field_extractor=field_extractor,
        )
        self.task_queue = task_queue
        self._initialized = True

    def wire(
        self,
        *,
        document_repository: IDocumentRepository,
        document_page_repository: IDocumentPageRepository,
        ocr_result_repository: IOCRResultRepository,
        extracted_field_repository: IExtractedFieldRepository,
        processing_job_repository: IProcessingJobRepository,
        audit_log_repository: IAuditLogRepository,
        document_storage: IDocumentStorage,
        page_renderer: IPageRenderer,
        image_preprocessor: IImagePreprocessor,
        ocr_service: IOCRService,
        layout_analyzer: ILayoutAnalyzer,
        field_extractor: IFieldExtractor,
        task_queue: ITaskQueue,
    ) -> None:
        """Wire all infrastructure adapters into the container."""
        self.wire_repositories(
            document_repository=document_repository,
            document_page_repository=document_page_repository,
            ocr_result_repository=ocr_result_repository,
            extracted_field_repository=extracted_field_repository,
            processing_job_repository=processing_job_repository,
            audit_log_repository=audit_log_repository,
        )
        self.wire_storage(document_storage=document_storage)
        self.wire_ocr(
            page_renderer=page_renderer,
            image_preprocessor=image_preprocessor,
            ocr_service=ocr_service,
        )
        self.wire_services(
            layout_analyzer=layout_analyzer,
            field_extractor=field_extractor,
            task_queue=task_queue,
        )

    def require_repositories_initialized(self) -> None:
        """Ensure repository adapters have been wired."""
        if not self._repos_initialized:
            msg = "Repositories not initialized. Call wire_repositories() at startup."
            raise RuntimeError(msg)

    def require_storage_initialized(self) -> None:
        """Ensure document storage has been wired."""
        if not self._storage_initialized:
            msg = "Storage not initialized. Call wire_storage() at startup."
            raise RuntimeError(msg)

    def require_ocr_initialized(self) -> None:
        """Ensure OCR adapters have been wired."""
        if not self._storage_initialized:
            msg = "Storage not initialized. Call wire_storage() at startup."
            raise RuntimeError(msg)
        if not self._ocr_initialized:
            msg = "OCR not initialized. Call wire_ocr() at startup."
            raise RuntimeError(msg)

    def require_extraction_initialized(self) -> None:
        """Ensure layout and extraction adapters have been wired."""
        self.require_ocr_initialized()
        if not self._extraction_initialized:
            msg = "Extraction not initialized. Call wire_extraction() at startup."
            raise RuntimeError(msg)

    def require_initialized(self) -> None:
        """Ensure container has been fully wired before use."""
        self.require_extraction_initialized()
        if not self._initialized:
            msg = "Services not initialized. Call wire_services() at startup."
            raise RuntimeError(msg)

    @property
    def documents(self) -> IDocumentRepository:
        """Get document repository, raising if not wired."""
        self.require_repositories_initialized()
        assert self.document_repository is not None
        return self.document_repository

    @property
    def document_pages(self) -> IDocumentPageRepository:
        """Get document page repository, raising if not wired."""
        self.require_repositories_initialized()
        assert self.document_page_repository is not None
        return self.document_page_repository

    @property
    def audit_logs(self) -> IAuditLogRepository:
        """Get audit log repository, raising if not wired."""
        self.require_repositories_initialized()
        assert self.audit_log_repository is not None
        return self.audit_log_repository

    @property
    def document_storage_service(self) -> IDocumentStorage:
        """Get document storage service, raising if not wired."""
        self.require_storage_initialized()
        assert self.document_storage is not None
        return self.document_storage

    @property
    def ocr_results(self) -> IOCRResultRepository:
        """Get OCR result repository, raising if not wired."""
        self.require_repositories_initialized()
        assert self.ocr_result_repository is not None
        return self.ocr_result_repository

    @property
    def ocr_service_instance(self) -> IOCRService:
        """Get OCR service, raising if not wired."""
        self.require_ocr_initialized()
        assert self.ocr_service is not None
        return self.ocr_service

    @property
    def page_renderer_service(self) -> IPageRenderer:
        """Get page renderer, raising if not wired."""
        self.require_ocr_initialized()
        assert self.page_renderer is not None
        return self.page_renderer

    @property
    def extracted_fields(self) -> IExtractedFieldRepository:
        """Get extracted field repository, raising if not wired."""
        self.require_repositories_initialized()
        assert self.extracted_field_repository is not None
        return self.extracted_field_repository

    @property
    def layout_analyzer_service(self) -> ILayoutAnalyzer:
        """Get layout analyzer, raising if not wired."""
        self.require_extraction_initialized()
        assert self.layout_analyzer is not None
        return self.layout_analyzer

    @property
    def field_extractor_service(self) -> IFieldExtractor:
        """Get field extractor, raising if not wired."""
        self.require_extraction_initialized()
        assert self.field_extractor is not None
        return self.field_extractor

    @property
    def task_queue_service(self) -> ITaskQueue:
        """Get task queue service, raising if not wired."""
        self.require_initialized()
        assert self.task_queue is not None
        return self.task_queue
