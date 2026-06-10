"""Document page repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from intelliclaim.application.interfaces.repositories import IDocumentPageRepository
from intelliclaim.domain.entities.document_page import DocumentPage
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.database.mappers import (
    document_page_to_domain,
    document_page_to_model,
)
from intelliclaim.infrastructure.database.models.document_page import DocumentPageModel


class DocumentPageRepository(IDocumentPageRepository):
    """PostgreSQL-backed document page repository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, page: DocumentPage) -> DocumentPage:
        pages = await self.save_many([page])
        return pages[0]

    async def save_many(self, pages: list[DocumentPage]) -> list[DocumentPage]:
        if not pages:
            return []
        async with self._session_factory() as session:
            models = [document_page_to_model(page) for page in pages]
            session.add_all(models)
            await session.commit()
            for model in models:
                await session.refresh(model)
            return [document_page_to_domain(model) for model in models]

    async def get_by_document_id(self, document_id: DocumentId) -> list[DocumentPage]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(DocumentPageModel)
                .where(DocumentPageModel.document_id == document_id.value)
                .order_by(DocumentPageModel.page_number)
            )
            return [document_page_to_domain(model) for model in result.scalars().all()]
