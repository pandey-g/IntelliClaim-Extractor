"""Unit tests for document page renderer."""

import io

import pytest

fitz = pytest.importorskip("fitz")
from PIL import Image

from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.value_objects.document_id import DocumentId
from intelliclaim.infrastructure.ocr.page_renderer import DocumentPageRenderer

MINIMAL_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/MediaBox[0 0 200 200]/Parent 2 0 R"
    b"/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n"
    b"4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
    b"5 0 obj<</Length 44>>stream\nBT /F1 12 Tf 50 100 Td (CLAIM) Tj ET\nendstream\nendobj\n"
    b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n"
    b"0000000115 00000 n \n0000000240 00000 n \n0000000310 00000 n \n"
    b"trailer<</Size 6/Root 1 0 R>>\nstartxref\n403\n%%EOF"
)


@pytest.mark.unit
class TestDocumentPageRenderer:
    @pytest.fixture
    def renderer(self) -> DocumentPageRenderer:
        return DocumentPageRenderer()

    @pytest.fixture
    def pdf_document(self) -> Document:
        return Document(
            id=DocumentId.generate(),
            filename="claim.pdf",
            content_type="application/pdf",
            document_type=DocumentType.PDF,
            file_size_bytes=len(MINIMAL_PDF),
            storage_path="/tmp/claim.pdf",
        )

    async def test_render_pdf_pages(self, renderer: DocumentPageRenderer, tmp_path) -> None:
        document = Document(
            id=DocumentId.generate(),
            filename="claim.pdf",
            content_type="application/pdf",
            document_type=DocumentType.PDF,
            file_size_bytes=len(MINIMAL_PDF),
            storage_path="/tmp/claim.pdf",
        )
        pages = await renderer.render_pages(
            document,
            MINIMAL_PDF,
            output_dir=tmp_path,
        )
        assert len(pages) == 1
        assert pages[0].exists()

    async def test_render_png_page(self, renderer: DocumentPageRenderer, tmp_path) -> None:
        image = Image.new("RGB", (50, 50), color="white")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        document = Document(
            id=DocumentId.generate(),
            filename="scan.png",
            content_type="image/png",
            document_type=DocumentType.PNG,
            file_size_bytes=len(png_bytes),
            storage_path="/tmp/scan.png",
        )
        pages = await renderer.render_pages(document, png_bytes, output_dir=tmp_path)
        assert len(pages) == 1
        assert pages[0].name == "page_1.png"
