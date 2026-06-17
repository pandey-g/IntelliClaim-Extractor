"""Document page rendering for PDF and image inputs."""

import asyncio
from pathlib import Path

import fitz
from PIL import Image

from intelliclaim.application.interfaces.services import IPageRenderer
from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.exceptions.document import DocumentProcessingError


class DocumentPageRenderer(IPageRenderer):
    """Renders PDF and image documents into per-page PNG files."""

    PDF_RENDER_DPI = 300

    async def render_pages(
        self,
        document: Document,
        file_content: bytes,
        *,
        output_dir: Path,
    ) -> list[Path]:
        """Render document pages to PNG images on disk."""
        output_dir.mkdir(parents=True, exist_ok=True)

        if document.document_type == DocumentType.PDF:
            return await asyncio.to_thread(
                self._render_pdf,
                file_content,
                output_dir,
            )
        return await asyncio.to_thread(
            self._render_image,
            file_content,
            document.document_type,
            output_dir,
        )

    def _render_pdf(self, content: bytes, output_dir: Path) -> list[Path]:
        paths: list[Path] = []
        try:
            pdf = fitz.open(stream=content, filetype="pdf")
        except Exception as exc:
            raise DocumentProcessingError(
                f"Failed to open PDF: {exc}",
            ) from exc

        try:
            if pdf.page_count == 0:
                raise DocumentProcessingError("PDF contains no pages")

            zoom = self.PDF_RENDER_DPI / 72.0
            matrix = fitz.Matrix(zoom, zoom)

            for page_index in range(pdf.page_count):
                page = pdf.load_page(page_index)
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                page_path = output_dir / f"page_{page_index + 1}.png"
                pixmap.save(str(page_path))
                paths.append(page_path)
        finally:
            pdf.close()

        return paths

    def _render_image(
        self,
        content: bytes,
        document_type: DocumentType,
        output_dir: Path,
    ) -> list[Path]:
        from io import BytesIO

        try:
            image = Image.open(BytesIO(content))
            image = image.convert("RGB")
        except Exception as exc:
            raise DocumentProcessingError(
                f"Failed to open image: {exc}",
            ) from exc

        page_path = output_dir / "page_1.png"
        image.save(page_path, format="PNG")
        return [page_path]
