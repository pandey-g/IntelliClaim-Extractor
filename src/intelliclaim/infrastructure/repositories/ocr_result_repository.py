"""OCR result repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from intelliclaim.application.interfaces.repositories import IOCRResultRepository
from intelliclaim.domain.entities.ocr_result import OCRResult
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.database.mappers import ocr_result_to_domain, ocr_result_to_model
from intelliclaim.infrastructure.database.models.ocr_result import OCRResultModel


class OCRResultRepository(IOCRResultRepository):
    """PostgreSQL-backed OCR result repository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, result: OCRResult) -> OCRResult:
        async with self._session_factory() as session:
            model = ocr_result_to_model(result)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return ocr_result_to_domain(model)

    async def get_by_document_id(self, document_id: DocumentId) -> list[OCRResult]:
        async with self._session_factory() as session:
            query = await session.execute(
                select(OCRResultModel)
                .where(OCRResultModel.document_id == document_id.value)
                .order_by(OCRResultModel.page_number)
            )
            return [ocr_result_to_domain(model) for model in query.scalars().all()]
