"""Document identifier value object."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DocumentId:
    """Strongly-typed document identifier."""

    value: UUID

    @classmethod
    def generate(cls) -> "DocumentId":
        """Generate a new unique document identifier."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "DocumentId":
        """Parse a document identifier from string representation."""
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)
