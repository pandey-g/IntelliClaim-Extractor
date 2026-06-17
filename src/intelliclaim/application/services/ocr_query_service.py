"""OCR query application service."""

from intelliclaim.application.interfaces.repositories import IDocumentRepository, IOCRResultRepository
from intelliclaim.domain.exceptions.document import DocumentNotFoundError
from intelliclaim.domain.value_objects.document_id import DocumentId


class OCRQueryService:
    """Provides read access to OCR extraction results."""

    def __init__(
        self,
        document_repository: IDocumentRepository,
        ocr_result_repository: IOCRResultRepository,
    ) -> None:
        self._document_repository = document_repository
        self._ocr_result_repository = ocr_result_repository

    async def get_ocr_results(self, document_id: DocumentId) -> list[dict[str, object]]:
        """Retrieve OCR results for a document."""
        document = await self._document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(str(document_id))

        results = await self._ocr_result_repository.get_by_document_id(document_id)
        pages: list[dict[str, object]] = []
        for result in results:
            pages.append(
                {
                    "page_number": result.page_number,
                    "full_text": result.full_text,
                    "average_confidence": (
                        result.average_confidence.value if result.average_confidence else None
                    ),
                    "words": [
                        {
                            "text": word.text,
                            "confidence": word.confidence.value,
                            "x": word.bounding_box.x,
                            "y": word.bounding_box.y,
                            "width": word.bounding_box.width,
                            "height": word.bounding_box.height,
                        }
                        for word in result.words
                    ],
                }
            )
        return pages
