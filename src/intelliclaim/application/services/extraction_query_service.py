"""Extraction query application service."""

from intelliclaim.application.dto.document import ExtractionResponseDTO, ExtractedFieldDTO
from intelliclaim.application.interfaces.repositories import (
    IDocumentRepository,
    IExtractedFieldRepository,
)
from intelliclaim.domain.exceptions.document import DocumentNotFoundError
from intelliclaim.domain.value_objects.document_id import DocumentId


class ExtractionQueryService:
    """Provides read access to structured extraction results."""

    def __init__(
        self,
        document_repository: IDocumentRepository,
        extracted_field_repository: IExtractedFieldRepository,
    ) -> None:
        self._document_repository = document_repository
        self._extracted_field_repository = extracted_field_repository

    async def get_extractions(self, document_id: DocumentId) -> ExtractionResponseDTO:
        """Retrieve extracted fields for a document."""
        document = await self._document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(str(document_id))

        fields = await self._extracted_field_repository.get_by_document_id(document_id)
        field_dtos = [
            ExtractedFieldDTO(
                field_name=field.field_name.value,
                field_value=field.field_value,
                confidence=field.confidence.value,
                page_number=field.page_number,
            )
            for field in fields
        ]

        confidence_score = 0.0
        if field_dtos:
            confidence_score = sum(dto.confidence for dto in field_dtos) / len(field_dtos)

        return ExtractionResponseDTO(
            document_id=document_id.value,
            fields=field_dtos,
            confidence_score=confidence_score,
        )
