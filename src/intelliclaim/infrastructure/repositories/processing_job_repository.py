"""Processing job repository implementation."""

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from intelliclaim.application.interfaces.repositories import IProcessingJobRepository
from intelliclaim.domain.entities.processing_job import ProcessingJob
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.database.mappers import (
    processing_job_to_domain,
    processing_job_to_model,
    update_processing_job_model,
)
from intelliclaim.infrastructure.database.models.processing_job import ProcessingJobModel


class ProcessingJobRepository(IProcessingJobRepository):
    """PostgreSQL-backed processing job repository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, job: ProcessingJob) -> ProcessingJob:
        async with self._session_factory() as session:
            model = processing_job_to_model(job)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return processing_job_to_domain(model)

    async def get_by_id(self, job_id: UUID) -> ProcessingJob | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProcessingJobModel).where(ProcessingJobModel.id == job_id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return processing_job_to_domain(model)

    async def get_by_document_id(self, document_id: DocumentId) -> ProcessingJob | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProcessingJobModel)
                .where(ProcessingJobModel.document_id == document_id.value)
                .order_by(desc(ProcessingJobModel.created_at))
                .limit(1)
            )
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return processing_job_to_domain(model)

    async def update(self, job: ProcessingJob) -> ProcessingJob:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProcessingJobModel).where(ProcessingJobModel.id == job.id)
            )
            model = result.scalar_one_or_none()
            if model is None:
                msg = f"Processing job not found for update: {job.id}"
                raise ValueError(msg)
            update_processing_job_model(model, job)
            await session.commit()
            await session.refresh(model)
            return processing_job_to_domain(model)
