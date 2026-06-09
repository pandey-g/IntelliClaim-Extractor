"""Standardized error response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Structured error detail."""

    code: str
    message: str
    details: list[dict[str, Any]] | dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Standard API error envelope."""

    error: ErrorDetail
    request_id: str | None = Field(default=None)
