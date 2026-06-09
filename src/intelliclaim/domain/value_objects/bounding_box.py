"""Bounding box value object for OCR/layout results."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BoundingBox:
    """Axis-aligned bounding box with normalized or pixel coordinates."""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if self.width < 0 or self.height < 0:
            msg = "Bounding box dimensions must be non-negative"
            raise ValueError(msg)

    @property
    def area(self) -> int:
        """Calculate bounding box area."""
        return self.width * self.height

    def to_dict(self) -> dict[str, int]:
        """Serialize to dictionary representation."""
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}
