"""Extraction and validation domain exceptions."""

from intelliclaim.domain.exceptions.base import DomainError


class ExtractionError(DomainError):
    """Raised when field extraction fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="EXTRACTION_ERROR")


class ValidationError(DomainError):
    """Raised when extracted data fails business validation."""

    def __init__(self, message: str, *, field: str | None = None) -> None:
        super().__init__(message=message, code="VALIDATION_ERROR")
        self.field = field
