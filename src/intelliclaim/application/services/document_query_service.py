"""Document query application service."""

from intelliclaim.application.dto.document import DocumentResponseDTO, DocumentStatusDTO
from intelliclaim.application.interfaces.repositories import IDocumentRepository
from intelliclaim.domain.exceptions.document import DocumentNotFoundError
from intelliclaim.domain.value_objects.document_id import DocumentId


class DocumentQueryService:
    """Provides read access to document metadata and status."""

    def __init__(self, document_repository: IDocumentRepository) -> None:
        self._document_repository = document_repository

    async def get_document(self, document_id: DocumentId) -> DocumentResponseDTO:
        """Retrieve full document metadata."""
        document = await self._document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(str(document_id))

        return DocumentResponseDTO(
            document_id=document.id.value,
            filename=document.filename,
            content_type=document.content_type,
            document_type=document.document_type.value,
            file_size_bytes=document.file_size_bytes,
            status=document.status,
            page_count=document.page_count,
            created_at=document.created_at,
            updated_at=document.updated_at,
            error_message=document.error_message,
        )

    async def get_status(self, document_id: DocumentId) -> DocumentStatusDTO:
        """Retrieve document processing status."""
        document = await self._document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(str(document_id))

        return DocumentStatusDTO(
            document_id=document.id.value,
            status=document.status,
            updated_at=document.updated_at,
            error_message=document.error_message,
        )
