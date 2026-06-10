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
    ILayoutAnalyzer,
    IOCRService,
    ITaskQueue,
)

__all__ = [
    "IAuditLogRepository",
    "IDocumentPageRepository",
    "IDocumentRepository",
    "IDocumentStorage",
    "IExtractedFieldRepository",
    "IFieldExtractor",
    "ILayoutAnalyzer",
    "IOCRResultRepository",
    "IOCRService",
    "IProcessingJobRepository",
    "ITaskQueue",
]
