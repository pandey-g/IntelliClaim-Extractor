"""Health check response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(examples=["healthy"])
    version: str
    timestamp: datetime
    components: dict[str, str] = Field(default_factory=dict)
