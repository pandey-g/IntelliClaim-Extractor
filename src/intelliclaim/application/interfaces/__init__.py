"""Port interfaces for infrastructure adapters."""

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

__all__ = [
    "IAuditLogRepository",
    "IDocumentPageRepository",
    "IDocumentRepository",
    "IDocumentStorage",
    "IExtractedFieldRepository",
    "IFieldExtractor",
    "IImagePreprocessor",
    "ILayoutAnalyzer",
    "IOCRResultRepository",
    "IOCRService",
    "IPageRenderer",
    "IProcessingJobRepository",
    "ITaskQueue",
]
