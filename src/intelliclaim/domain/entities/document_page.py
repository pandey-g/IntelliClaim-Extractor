"""Document page domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from intelliclaim.domain.value_objects.document_id import DocumentId


@dataclass
class DocumentPage:
    """Represents a single page extracted from a multi-page document."""

    id: UUID
    document_id: DocumentId
    page_number: int
    storage_path: str
    width: int | None = None
    height: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        document_id: DocumentId,
        page_number: int,
        storage_path: str,
        *,
        width: int | None = None,
        height: int | None = None,
    ) -> "DocumentPage":
        """Factory method for creating document pages."""
        return cls(
            id=uuid4(),
            document_id=document_id,
            page_number=page_number,
            storage_path=storage_path,
            width=width,
            height=height,
        )
