"""Integration tests for OCR processing pipeline."""

import io

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image, ImageDraw

from intelliclaim.api.app import create_app
from intelliclaim.infrastructure.config.settings import Settings

API_KEY = "test-api-key-12345"


def _make_text_png(text: str = "Claim ID: CLM-12345") -> bytes:
    image = Image.new("RGB", (400, 120), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((20, 40), text, fill="black")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.mark.integration
class TestOCRPipelineAPI:
    @pytest.fixture
    async def ocr_client(self, postgres_database_url: str, tmp_path):
        from intelliclaim.infrastructure.config.settings import get_settings
        from intelliclaim.infrastructure.database.base import Base
        from intelliclaim.infrastructure.database.session import DatabaseSessionManager

        get_settings.cache_clear()

        settings = Settings(
            secret_key="test-secret-key-for-pytest-runs-32chars",
            database_url=postgres_database_url,
            document_storage_path=str(tmp_path / "uploads"),
            api_keys=API_KEY,
            otel_enabled=False,
            prometheus_enabled=False,
        )

        db_manager = DatabaseSessionManager(settings)
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        await db_manager.close()

        application = create_app(settings=settings)
        async with application.router.lifespan_context(application):
            transport = ASGITransport(app=application, raise_app_exceptions=False)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                yield client

        get_settings.cache_clear()

    @pytest.mark.skipif(
        not __import__("shutil").which("tesseract"),
        reason="Tesseract not installed",
    )
    async def test_upload_process_and_get_ocr_results(self, ocr_client: AsyncClient) -> None:
        png_bytes = _make_text_png("Claim ID: CLM-12345")

        upload_response = await ocr_client.post(
            "/documents",
            headers={"X-API-Key": API_KEY},
            files={"file": ("claim.png", png_bytes, "image/png")},
        )
        assert upload_response.status_code == 201
        document_id = upload_response.json()["document_id"]

        process_response = await ocr_client.post(
            f"/documents/{document_id}/process",
            headers={"X-API-Key": API_KEY},
        )
        assert process_response.status_code == 200
        process_data = process_response.json()
        assert process_data["page_count"] == 1
        assert process_data["ocr_results_count"] == 1
        assert process_data["status"] == "completed"
        assert process_data["extracted_fields_count"] >= 0

        extraction_response = await ocr_client.get(
            f"/documents/{document_id}/extractions",
            headers={"X-API-Key": API_KEY},
        )
        assert extraction_response.status_code == 200
        extraction_data = extraction_response.json()
        assert extraction_data["document_id"] == document_id

        ocr_response = await ocr_client.get(
            f"/documents/{document_id}/ocr",
            headers={"X-API-Key": API_KEY},
        )
        assert ocr_response.status_code == 200
        ocr_data = ocr_response.json()
        assert len(ocr_data["pages"]) == 1
        assert ocr_data["pages"][0]["page_number"] == 1

    async def test_process_unknown_document_returns_404(self, ocr_client: AsyncClient) -> None:
        response = await ocr_client.post(
            "/documents/550e8400-e29b-41d4-a716-446655440000/process",
            headers={"X-API-Key": API_KEY},
        )
        assert response.status_code == 404
