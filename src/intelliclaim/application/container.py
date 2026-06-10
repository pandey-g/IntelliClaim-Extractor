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
    ILayoutAnalyzer,
    IOCRService,
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
    ocr_service: IOCRService | None = None
    layout_analyzer: ILayoutAnalyzer | None = None
    field_extractor: IFieldExtractor | None = None
    task_queue: ITaskQueue | None = None
    _repos_initialized: bool = field(default=False, repr=False)
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

    def wire_services(
        self,
        *,
        document_storage: IDocumentStorage,
        ocr_service: IOCRService,
        layout_analyzer: ILayoutAnalyzer,
        field_extractor: IFieldExtractor,
        task_queue: ITaskQueue,
    ) -> None:
        """Wire external service adapters into the container."""
        self.document_storage = document_storage
        self.ocr_service = ocr_service
        self.layout_analyzer = layout_analyzer
        self.field_extractor = field_extractor
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
        self.wire_services(
            document_storage=document_storage,
            ocr_service=ocr_service,
            layout_analyzer=layout_analyzer,
            field_extractor=field_extractor,
            task_queue=task_queue,
        )

    def require_repositories_initialized(self) -> None:
        """Ensure repository adapters have been wired."""
        if not self._repos_initialized:
            msg = "Repositories not initialized. Call wire_repositories() at startup."
            raise RuntimeError(msg)

    def require_initialized(self) -> None:
        """Ensure container has been fully wired before use."""
        self.require_repositories_initialized()
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
        self.require_initialized()
        assert self.document_storage is not None
        return self.document_storage

    @property
    def task_queue_service(self) -> ITaskQueue:
        """Get task queue service, raising if not wired."""
        self.require_initialized()
        assert self.task_queue is not None
        return self.task_queue
