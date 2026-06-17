"""Document OCR and extraction processing application service."""

import asyncio
from pathlib import Path

import structlog

from intelliclaim.application.interfaces.repositories import (
    IAuditLogRepository,
    IDocumentPageRepository,
    IDocumentRepository,
    IExtractedFieldRepository,
    IOCRResultRepository,
)
from intelliclaim.application.interfaces.services import (
    IDocumentStorage,
    IFieldExtractor,
    ILayoutAnalyzer,
    IOCRService,
    IPageRenderer,
)
from intelliclaim.application.services.extraction_validator import ExtractionValidator
from intelliclaim.domain.entities.audit_log import AuditLog
from intelliclaim.domain.entities.document_page import DocumentPage
from intelliclaim.domain.enums.document_status import DocumentStatus
from intelliclaim.domain.exceptions.document import DocumentNotFoundError, DocumentProcessingError
from intelliclaim.domain.value_objects.document_id import DocumentId

logger = structlog.get_logger(__name__)


class DocumentProcessingService:
    """Orchestrates document preprocessing, OCR, layout analysis, and extraction."""

    def __init__(
        self,
        document_repository: IDocumentRepository,
        document_page_repository: IDocumentPageRepository,
        ocr_result_repository: IOCRResultRepository,
        extracted_field_repository: IExtractedFieldRepository,
        audit_log_repository: IAuditLogRepository,
        document_storage: IDocumentStorage,
        page_renderer: IPageRenderer,
        ocr_service: IOCRService,
        layout_analyzer: ILayoutAnalyzer,
        field_extractor: IFieldExtractor,
        extraction_validator: ExtractionValidator | None = None,
    ) -> None:
        self._document_repository = document_repository
        self._document_page_repository = document_page_repository
        self._ocr_result_repository = ocr_result_repository
        self._extracted_field_repository = extracted_field_repository
        self._audit_log_repository = audit_log_repository
        self._document_storage = document_storage
        self._page_renderer = page_renderer
        self._ocr_service = ocr_service
        self._layout_analyzer = layout_analyzer
        self._field_extractor = field_extractor
        self._extraction_validator = extraction_validator or ExtractionValidator()

    async def process_document(
        self,
        document_id: DocumentId,
        *,
        actor: str = "system",
    ) -> dict[str, object]:
        """Run preprocessing, OCR, layout analysis, and field extraction."""
        document = await self._document_repository.get_by_id(document_id)
        if document is None:
            raise DocumentNotFoundError(str(document_id))

        if document.is_terminal():
            raise DocumentProcessingError(
                f"Document is in terminal state: {document.status.value}",
                document_id=str(document_id),
            )

        document.mark_status(DocumentStatus.PREPROCESSING)
        await self._document_repository.update(document)

        try:
            file_content = await self._document_storage.retrieve(document.storage_path)
            working_dir = self._document_storage.get_working_directory(document_id)
            rendered_pages = await self._page_renderer.render_pages(
                document,
                file_content,
                output_dir=working_dir / "rendered",
            )

            document_pages: list[DocumentPage] = []
            for index, page_path in enumerate(rendered_pages, start=1):
                page_bytes = page_path.read_bytes()
                storage_path = await self._document_storage.store_page_image(
                    document_id=document_id,
                    page_number=index,
                    image_bytes=page_bytes,
                )
                width, height = await asyncio.to_thread(self._read_image_dimensions, page_path)
                document_pages.append(
                    DocumentPage.create(
                        document_id=document_id,
                        page_number=index,
                        storage_path=storage_path,
                        width=width,
                        height=height,
                    )
                )

            await self._document_page_repository.save_many(document_pages)
            document.page_count = len(document_pages)
            document.mark_status(DocumentStatus.OCR_IN_PROGRESS)
            await self._document_repository.update(document)

            ocr_results = []
            for page in document_pages:
                page_image_path = Path(page.storage_path)
                ocr_result = await self._ocr_service.extract_text(
                    document_id=document_id,
                    image_path=page_image_path,
                    page_number=page.page_number,
                )
                saved = await self._ocr_result_repository.save(ocr_result)
                ocr_results.append(saved)

            document.mark_status(DocumentStatus.LAYOUT_ANALYSIS)
            await self._document_repository.update(document)

            layout_pages: list[dict[str, object]] = []
            for page, ocr_result in zip(document_pages, ocr_results, strict=True):
                layout_result = await self._layout_analyzer.analyze(
                    document_id=document_id,
                    image_path=Path(page.storage_path),
                    ocr_result=ocr_result,
                )
                layout_pages.append(layout_result)

            document.mark_status(DocumentStatus.EXTRACTION)
            await self._document_repository.update(document)

            extracted_fields = await self._field_extractor.extract(
                document_id=document_id,
                layout_data={"pages": layout_pages},
                ocr_results=ocr_results,
            )

            document.mark_status(DocumentStatus.VALIDATION)
            await self._document_repository.update(document)

            validated_fields = self._extraction_validator.validate(extracted_fields)
            saved_fields = await self._extracted_field_repository.save_many(validated_fields)

            document.mark_status(DocumentStatus.COMPLETED)
            await self._document_repository.update(document)

            await self._audit_log_repository.save(
                AuditLog.create(
                    action="document.processing_completed",
                    actor=actor,
                    document_id=document_id,
                    details={
                        "page_count": document.page_count,
                        "ocr_results": len(ocr_results),
                        "extracted_fields": len(saved_fields),
                    },
                )
            )

            logger.info(
                "document_processing_completed",
                document_id=str(document_id),
                page_count=document.page_count,
                ocr_results=len(ocr_results),
                extracted_fields=len(saved_fields),
            )

            return {
                "document_id": document_id.value,
                "status": document.status.value,
                "page_count": document.page_count,
                "ocr_results_count": len(ocr_results),
                "extracted_fields_count": len(saved_fields),
            }

        except DocumentProcessingError as exc:
            document.mark_status(DocumentStatus.FAILED, error=exc.message)
            await self._document_repository.update(document)
            raise
        except Exception as exc:
            document.mark_status(DocumentStatus.FAILED, error=str(exc))
            await self._document_repository.update(document)
            raise DocumentProcessingError(
                f"Document processing failed: {exc}",
                document_id=str(document_id),
            ) from exc

    @staticmethod
    def _read_image_dimensions(image_path: Path) -> tuple[int | None, int | None]:
        import cv2

        image = cv2.imread(str(image_path))
        if image is None:
            return None, None
        height, width = image.shape[:2]
        return width, height
