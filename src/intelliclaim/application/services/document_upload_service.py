"""Document upload application service."""

import structlog

from intelliclaim.application.dto.document import DocumentUploadDTO
from intelliclaim.application.interfaces.repositories import IAuditLogRepository, IDocumentRepository
from intelliclaim.application.interfaces.services import IDocumentStorage
from intelliclaim.application.services.document_validator import DocumentValidator
from intelliclaim.domain.entities.audit_log import AuditLog
from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.value_objects.document_id import DocumentId

logger = structlog.get_logger(__name__)


class DocumentUploadService:
    """Orchestrates document upload, storage, and persistence."""

    def __init__(
        self,
        document_repository: IDocumentRepository,
        audit_log_repository: IAuditLogRepository,
        document_storage: IDocumentStorage,
        validator: DocumentValidator,
    ) -> None:
        self._document_repository = document_repository
        self._audit_log_repository = audit_log_repository
        self._document_storage = document_storage
        self._validator = validator

    async def upload(self, filename: str, content: bytes, *, actor: str) -> DocumentUploadDTO:
        """Validate, store, and persist an uploaded document."""
        validated = self._validator.validate(filename, content)
        document_id = DocumentId.generate()

        storage_path = await self._document_storage.store(
            document_id=document_id,
            filename=validated.filename,
            content=validated.content,
        )

        document = Document(
            id=document_id,
            filename=validated.filename,
            content_type=validated.content_type,
            document_type=validated.document_type,
            file_size_bytes=validated.file_size_bytes,
            storage_path=storage_path,
        )
        await self._document_repository.save(document)

        await self._audit_log_repository.save(
            AuditLog.create(
                action="document.uploaded",
                actor=actor,
                document_id=document_id,
                details={
                    "filename": validated.filename,
                    "document_type": validated.document_type.value,
                    "file_size_bytes": validated.file_size_bytes,
                },
            )
        )

        logger.info(
            "document_uploaded",
            document_id=str(document_id),
            filename=validated.filename,
            actor=actor,
        )

        return DocumentUploadDTO(document_id=document_id.value)
