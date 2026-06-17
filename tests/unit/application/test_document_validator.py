"""Unit tests for document validator."""

import pytest

from intelliclaim.application.services.document_validator import DocumentValidator
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.exceptions.document import InvalidDocumentError
from intelliclaim.infrastructure.config.settings import Settings

MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\nendobj\n"
MINIMAL_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
MINIMAL_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 16


@pytest.mark.unit
class TestDocumentValidator:
    @pytest.fixture
    def validator(self) -> DocumentValidator:
        settings = Settings(
            secret_key="test-secret-key-for-pytest-runs-32chars",
            max_upload_size_mb=1,
        )
        return DocumentValidator(settings)

    def test_valid_pdf(self, validator: DocumentValidator) -> None:
        result = validator.validate("claim.pdf", MINIMAL_PDF)
        assert result.document_type == DocumentType.PDF
        assert result.content_type == "application/pdf"

    def test_valid_png(self, validator: DocumentValidator) -> None:
        result = validator.validate("scan.png", MINIMAL_PNG)
        assert result.document_type == DocumentType.PNG

    def test_valid_jpeg(self, validator: DocumentValidator) -> None:
        result = validator.validate("photo.jpg", MINIMAL_JPEG)
        assert result.document_type == DocumentType.JPEG

    def test_rejects_empty_file(self, validator: DocumentValidator) -> None:
        with pytest.raises(InvalidDocumentError, match="empty"):
            validator.validate("empty.pdf", b"")

    def test_rejects_invalid_extension(self, validator: DocumentValidator) -> None:
        with pytest.raises(InvalidDocumentError, match="not allowed"):
            validator.validate("malware.exe", MINIMAL_PDF)

    def test_rejects_path_traversal_filename(self, validator: DocumentValidator) -> None:
        with pytest.raises(InvalidDocumentError, match="Invalid filename"):
            validator.validate("../../etc/passwd.pdf", MINIMAL_PDF)

    def test_rejects_magic_byte_mismatch(self, validator: DocumentValidator) -> None:
        with pytest.raises(InvalidDocumentError, match="does not match"):
            validator.validate("fake.pdf", b"NOT_A_PDF_FILE_CONTENT")

    def test_rejects_oversized_file(self, validator: DocumentValidator) -> None:
        oversized = MINIMAL_PDF + b"x" * (1024 * 1024)
        with pytest.raises(InvalidDocumentError, match="maximum size"):
            validator.validate("big.pdf", oversized)
