"""Unit tests for domain exceptions."""

import pytest

from intelliclaim.domain.exceptions.base import DomainError
from intelliclaim.domain.exceptions.document import (
    DocumentNotFoundError,
    DocumentProcessingError,
    InvalidDocumentError,
)
from intelliclaim.domain.exceptions.extraction import ExtractionError, ValidationError
from intelliclaim.domain.exceptions.security import AuthenticationError, AuthorizationError


@pytest.mark.unit
class TestDomainExceptions:
    def test_base_domain_error(self) -> None:
        exc = DomainError("test error", code="TEST_CODE")
        assert exc.message == "test error"
        assert exc.code == "TEST_CODE"

    def test_document_not_found(self) -> None:
        exc = DocumentNotFoundError("doc-123")
        assert exc.code == "DOCUMENT_NOT_FOUND"
        assert exc.document_id == "doc-123"

    def test_invalid_document(self) -> None:
        exc = InvalidDocumentError("bad file")
        assert exc.code == "INVALID_DOCUMENT"

    def test_document_processing_error(self) -> None:
        exc = DocumentProcessingError("failed", document_id="doc-1")
        assert exc.document_id == "doc-1"

    def test_extraction_error(self) -> None:
        exc = ExtractionError("extraction failed")
        assert exc.code == "EXTRACTION_ERROR"

    def test_validation_error_with_field(self) -> None:
        exc = ValidationError("invalid amount", field="claim_amount")
        assert exc.field == "claim_amount"

    def test_authentication_error(self) -> None:
        exc = AuthenticationError()
        assert exc.code == "AUTHENTICATION_ERROR"

    def test_authorization_error(self) -> None:
        exc = AuthorizationError("denied")
        assert exc.message == "denied"
