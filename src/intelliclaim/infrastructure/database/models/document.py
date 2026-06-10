"""Document ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intelliclaim.infrastructure.database.base import Base

if TYPE_CHECKING:
    from intelliclaim.infrastructure.database.models.audit_log import AuditLogModel
    from intelliclaim.infrastructure.database.models.document_page import DocumentPageModel
    from intelliclaim.infrastructure.database.models.extracted_field import ExtractedFieldModel
    from intelliclaim.infrastructure.database.models.ocr_result import OCRResultModel
    from intelliclaim.infrastructure.database.models.processing_job import ProcessingJobModel


class DocumentModel(Base):
    """Persisted insurance claim document metadata."""

    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_status", "status"),
        Index("ix_documents_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    document_type: Mapped[str] = mapped_column(String(32), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    page_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    pages: Mapped[list[DocumentPageModel]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    ocr_results: Mapped[list[OCRResultModel]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    extracted_fields: Mapped[list[ExtractedFieldModel]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    processing_jobs: Mapped[list[ProcessingJobModel]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[list[AuditLogModel]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
