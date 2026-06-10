"""Audit log repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from intelliclaim.application.interfaces.repositories import IAuditLogRepository
from intelliclaim.domain.entities.audit_log import AuditLog
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.database.mappers import audit_log_to_domain, audit_log_to_model
from intelliclaim.infrastructure.database.models.audit_log import AuditLogModel


class AuditLogRepository(IAuditLogRepository):
    """PostgreSQL-backed audit log repository."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, audit_log: AuditLog) -> AuditLog:
        async with self._session_factory() as session:
            model = audit_log_to_model(audit_log)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return audit_log_to_domain(model)

    async def get_by_document_id(self, document_id: DocumentId) -> list[AuditLog]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(AuditLogModel)
                .where(AuditLogModel.document_id == document_id.value)
                .order_by(AuditLogModel.created_at)
            )
            return [audit_log_to_domain(model) for model in result.scalars().all()]
