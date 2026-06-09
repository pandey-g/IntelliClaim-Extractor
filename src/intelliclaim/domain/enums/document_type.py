"""Supported document MIME categories."""

from enum import StrEnum


class DocumentType(StrEnum):
    """Classification of uploaded document formats."""

    PDF = "pdf"
    PNG = "png"
    JPEG = "jpeg"
    TIFF = "tiff"

    @classmethod
    def from_extension(cls, extension: str) -> "DocumentType":
        """Resolve document type from file extension."""
        normalized = extension.lower().lstrip(".")
        mapping: dict[str, DocumentType] = {
            "pdf": cls.PDF,
            "png": cls.PNG,
            "jpg": cls.JPEG,
            "jpeg": cls.JPEG,
            "tif": cls.TIFF,
            "tiff": cls.TIFF,
        }
        if normalized not in mapping:
            msg = f"Unsupported file extension: {extension}"
            raise ValueError(msg)
        return mapping[normalized]
