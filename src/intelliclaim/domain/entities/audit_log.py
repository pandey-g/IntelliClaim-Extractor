"""Audit log domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from intelliclaim.domain.value_objects.document_id import DocumentId


@dataclass
class AuditLog:
    """Immutable audit trail entry for compliance and debugging."""

    id: UUID
    action: str
    actor: str
    document_id: DocumentId | None = None
    details: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        action: str,
        actor: str,
        *,
        document_id: DocumentId | None = None,
        details: dict[str, Any] | None = None,
    ) -> "AuditLog":
        """Factory method for creating audit log entries."""
        return cls(
            id=uuid4(),
            action=action,
            actor=actor,
            document_id=document_id,
            details=details or {},
        )
