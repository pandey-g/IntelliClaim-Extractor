"""Port interfaces for infrastructure adapters."""

from intelliclaim.application.interfaces.repositories import (
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
