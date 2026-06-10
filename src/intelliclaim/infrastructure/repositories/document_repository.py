"""Document repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from intelliclaim.application.interfaces.repositories import IDocumentRepository
from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.database.mappers import (
    document_to_domain,
    document_to_model,
    update_document_model,
)
from intelliclaim.infrastructure.database.models.document import DocumentModel


class DocumentRepository(IDocumentRepository):
    """PostgreSQL-backed document repository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, document: Document) -> Document:
        async with self._session_factory() as session:
            model = document_to_model(document)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return document_to_domain(model)

    async def get_by_id(self, document_id: DocumentId) -> Document | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(DocumentModel).where(DocumentModel.id == document_id.value)
            )
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return document_to_domain(model)

    async def update(self, document: Document) -> Document:
        async with self._session_factory() as session:
            result = await session.execute(
                select(DocumentModel).where(DocumentModel.id == document.id.value)
            )
            model = result.scalar_one_or_none()
            if model is None:
                msg = f"Document not found for update: {document.id}"
                raise ValueError(msg)
            update_document_model(model, document)
            await session.commit()
            await session.refresh(model)
            return document_to_domain(model)
