"""Integration tests for document upload API."""

import pytest
from httpx import ASGITransport, AsyncClient

from intelliclaim.api.app import create_app
from intelliclaim.infrastructure.config.settings import Settings

MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\nendobj\n"
API_KEY = "test-api-key-12345"


@pytest.mark.integration
class TestDocumentUploadAPI:
    @pytest.fixture
    async def document_client(self, postgres_database_url: str, tmp_path):
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

    async def test_upload_requires_authentication(self, document_client: AsyncClient) -> None:
        response = await document_client.post(
            "/documents",
            files={"file": ("claim.pdf", MINIMAL_PDF, "application/pdf")},
        )
        assert response.status_code == 401

    async def test_upload_pdf_success(self, document_client: AsyncClient) -> None:
        response = await document_client.post(
            "/documents",
            headers={"X-API-Key": API_KEY},
            files={"file": ("claim.pdf", MINIMAL_PDF, "application/pdf")},
        )
        assert response.status_code == 201
        data = response.json()
        assert "document_id" in data

        document_id = data["document_id"]

        get_response = await document_client.get(
            f"/documents/{document_id}",
            headers={"X-API-Key": API_KEY},
        )
        assert get_response.status_code == 200
        assert get_response.json()["filename"] == "claim.pdf"
        assert get_response.json()["status"] == "pending"

        status_response = await document_client.get(
            f"/documents/{document_id}/status",
            headers={"X-API-Key": API_KEY},
        )
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "pending"

    async def test_upload_rejects_invalid_file(self, document_client: AsyncClient) -> None:
        response = await document_client.post(
            "/documents",
            headers={"X-API-Key": API_KEY},
            files={"file": ("fake.pdf", b"not-a-pdf", "application/pdf")},
        )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_DOCUMENT"

    async def test_get_nonexistent_document_returns_404(
        self,
        document_client: AsyncClient,
    ) -> None:
        response = await document_client.get(
            "/documents/550e8400-e29b-41d4-a716-446655440000",
            headers={"X-API-Key": API_KEY},
        )
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"

    async def test_upload_with_jwt(self, document_client: AsyncClient) -> None:
        from intelliclaim.infrastructure.security.jwt_handler import JWTHandler

        handler = JWTHandler(
            Settings(secret_key="test-secret-key-for-pytest-runs-32chars"),
        )
        token = handler.create_access_token("integration-test")

        response = await document_client.post(
            "/documents",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("claim.pdf", MINIMAL_PDF, "application/pdf")},
        )
        assert response.status_code == 201
