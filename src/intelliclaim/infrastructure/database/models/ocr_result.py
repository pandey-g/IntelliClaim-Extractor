"""OCR result ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intelliclaim.infrastructure.database.base import Base

if TYPE_CHECKING:
    from intelliclaim.infrastructure.database.models.document import DocumentModel
    from intelliclaim.infrastructure.database.models.document_page import DocumentPageModel


class OCRResultModel(Base):
    """Persisted OCR output for a document page."""

    __tablename__ = "ocr_results"
    __table_args__ = (
        Index("ix_ocr_results_document_id", "document_id"),
        Index("ix_ocr_results_document_page", "document_id", "page_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    page_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_pages.id", ondelete="SET NULL"),
        nullable=True,
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    words: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    average_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    document: Mapped[DocumentModel] = relationship(back_populates="ocr_results")
    page: Mapped[DocumentPageModel | None] = relationship(back_populates="ocr_results")
