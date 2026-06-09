"""Domain exceptions."""

from intelliclaim.domain.exceptions.base import DomainError
from intelliclaim.domain.exceptions.document import (
    DocumentNotFoundError,
    DocumentProcessingError,
    InvalidDocumentError,
)
from intelliclaim.domain.exceptions.extraction import ExtractionError, ValidationError
from intelliclaim.domain.exceptions.security import AuthenticationError, AuthorizationError

__all__ = [
    "AuthenticationError",
    "AuthorizationError",
    "DocumentNotFoundError",
    "DocumentProcessingError",
    "DomainError",
    "ExtractionError",
    "InvalidDocumentError",
    "ValidationError",
]
