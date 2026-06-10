"""Extracted field repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from intelliclaim.application.interfaces.repositories import IExtractedFieldRepository
from intelliclaim.domain.entities.extracted_field import ExtractedField
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.database.mappers import (
    extracted_field_to_domain,
    extracted_field_to_model,
)
from intelliclaim.infrastructure.database.models.extracted_field import ExtractedFieldModel


class ExtractedFieldRepository(IExtractedFieldRepository):
    """PostgreSQL-backed extracted field repository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save_many(self, fields: list[ExtractedField]) -> list[ExtractedField]:
        if not fields:
            return []
        async with self._session_factory() as session:
            models = [extracted_field_to_model(field) for field in fields]
            session.add_all(models)
            await session.commit()
            for model in models:
                await session.refresh(model)
            return [extracted_field_to_domain(model) for model in models]

    async def get_by_document_id(self, document_id: DocumentId) -> list[ExtractedField]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ExtractedFieldModel)
                .where(ExtractedFieldModel.document_id == document_id.value)
                .order_by(ExtractedFieldModel.field_name)
            )
            return [extracted_field_to_domain(model) for model in result.scalars().all()]
