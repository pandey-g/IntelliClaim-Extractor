"""Document upload validation logic."""

from dataclasses import dataclass
from pathlib import Path

from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.exceptions.document import InvalidDocumentError
from intelliclaim.infrastructure.config.settings import Settings

MAGIC_SIGNATURES: dict[DocumentType, list[bytes]] = {
    DocumentType.PDF: [b"%PDF"],
    DocumentType.PNG: [b"\x89PNG\r\n\x1a\n"],
    DocumentType.JPEG: [b"\xff\xd8\xff"],
    DocumentType.TIFF: [b"II*\x00", b"MM\x00*"],
}

CONTENT_TYPES: dict[DocumentType, str] = {
    DocumentType.PDF: "application/pdf",
    DocumentType.PNG: "image/png",
    DocumentType.JPEG: "image/jpeg",
    DocumentType.TIFF: "image/tiff",
}


@dataclass(frozen=True, slots=True)
class ValidatedUpload:
    """Result of successful upload validation."""

    filename: str
    document_type: DocumentType
    content_type: str
    file_size_bytes: int
    content: bytes


class DocumentValidator:
    """Validates uploaded document files before persistence."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._allowed_extensions = set(settings.allowed_extension_list)
        self._max_size_bytes = settings.max_upload_size_bytes

    def validate(self, filename: str, content: bytes) -> ValidatedUpload:
        """Validate filename, size, extension, and file content signatures."""
        if ".." in filename or "/" in filename or "\\" in filename:
            raise InvalidDocumentError("Invalid filename")

        safe_name = Path(filename).name
        if not safe_name or safe_name in {".", ".."}:
            raise InvalidDocumentError("Filename is required")

        if not content:
            raise InvalidDocumentError("Uploaded file is empty")

        if len(content) > self._max_size_bytes:
            raise InvalidDocumentError(
                f"File exceeds maximum size of {self._settings.max_upload_size_mb} MB"
            )

        extension = Path(safe_name).suffix.lstrip(".").lower()
        if extension not in self._allowed_extensions:
            raise InvalidDocumentError(f"File extension '.{extension}' is not allowed")

        try:
            document_type = DocumentType.from_extension(extension)
        except ValueError as exc:
            raise InvalidDocumentError(str(exc)) from exc

        self._validate_magic_bytes(content, document_type)

        return ValidatedUpload(
            filename=safe_name,
            document_type=document_type,
            content_type=CONTENT_TYPES[document_type],
            file_size_bytes=len(content),
            content=content,
        )

    def _validate_magic_bytes(self, content: bytes, document_type: DocumentType) -> None:
        """Verify file content matches expected magic byte signatures."""
        signatures = MAGIC_SIGNATURES[document_type]
        if not any(content.startswith(signature) for signature in signatures):
            raise InvalidDocumentError(
                f"File content does not match expected format for {document_type.value}"
            )
