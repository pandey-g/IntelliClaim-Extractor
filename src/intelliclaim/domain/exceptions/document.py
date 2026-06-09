"""Document-related domain exceptions."""

from intelliclaim.domain.exceptions.base import DomainError


class DocumentNotFoundError(DomainError):
    """Raised when a requested document does not exist."""

    def __init__(self, document_id: str) -> None:
        super().__init__(
            message=f"Document not found: {document_id}",
            code="DOCUMENT_NOT_FOUND",
        )
        self.document_id = document_id


class InvalidDocumentError(DomainError):
    """Raised when an uploaded document fails validation."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="INVALID_DOCUMENT")


class DocumentProcessingError(DomainError):
    """Raised when document processing fails."""

    def __init__(self, message: str, *, document_id: str | None = None) -> None:
        super().__init__(message=message, code="DOCUMENT_PROCESSING_ERROR")
        self.document_id = document_id
