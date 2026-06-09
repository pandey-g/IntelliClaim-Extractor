"""Document domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from intelliclaim.domain.enums.document_status import DocumentStatus
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.value_objects.document_id import DocumentId


@dataclass
class Document:
    """Represents an uploaded insurance claim document."""

    id: DocumentId
    filename: str
    content_type: str
    document_type: DocumentType
    file_size_bytes: int
    storage_path: str
    status: DocumentStatus = DocumentStatus.PENDING
    page_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    error_message: str | None = None

    def mark_status(self, status: DocumentStatus, *, error: str | None = None) -> None:
        """Transition document to a new processing status."""
        self.status = status
        self.updated_at = datetime.now(UTC)
        if error is not None:
            self.error_message = error

    def is_terminal(self) -> bool:
        """Check if document has reached a terminal state."""
        return self.status in (DocumentStatus.COMPLETED, DocumentStatus.FAILED)
