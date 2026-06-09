"""Confidence score value object."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConfidenceScore:
    """Normalized confidence score in range [0.0, 1.0]."""

    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            msg = f"Confidence score must be between 0.0 and 1.0, got {self.value}"
            raise ValueError(msg)

    @classmethod
    def from_percentage(cls, percentage: float) -> "ConfidenceScore":
        """Create confidence score from percentage value (0-100)."""
        return cls(value=percentage / 100.0)
