"""Unit tests for domain enumerations."""

import pytest

from intelliclaim.domain.enums.document_type import DocumentType


@pytest.mark.unit
class TestDocumentType:
    @pytest.mark.parametrize(
        ("extension", "expected"),
        [
            ("pdf", DocumentType.PDF),
            (".PDF", DocumentType.PDF),
            ("png", DocumentType.PNG),
            ("jpg", DocumentType.JPEG),
            ("jpeg", DocumentType.JPEG),
            ("tiff", DocumentType.TIFF),
            ("tif", DocumentType.TIFF),
        ],
    )
    def test_from_extension(self, extension: str, expected: DocumentType) -> None:
        assert DocumentType.from_extension(extension) == expected

    def test_unsupported_extension_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported"):
            DocumentType.from_extension("docx")
