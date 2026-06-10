"""Integration tests for exception handling."""

import pytest
from fastapi import APIRouter, FastAPI
from httpx import ASGITransport, AsyncClient

from intelliclaim.api.middleware.exception_handler import register_exception_handlers
from intelliclaim.domain.exceptions.document import DocumentNotFoundError, InvalidDocumentError


@pytest.mark.integration
class TestExceptionHandlers:
    @pytest.fixture
    def error_app(self) -> FastAPI:
        app = FastAPI()
        register_exception_handlers(app)
        router = APIRouter()

        @router.get("/not-found")
        async def raise_not_found() -> None:
            raise DocumentNotFoundError("missing-doc")

        @router.get("/invalid")
        async def raise_invalid() -> None:
            raise InvalidDocumentError("unsupported format")

        @router.get("/crash")
        async def raise_unhandled() -> None:
            raise RuntimeError("unexpected")

        app.include_router(router)
        return app

    @staticmethod
    def _transport(app: FastAPI) -> ASGITransport:
        return ASGITransport(app=app, raise_app_exceptions=False)

    async def test_domain_error_returns_structured_response(self, error_app: FastAPI) -> None:
        async with AsyncClient(
            transport=self._transport(error_app), base_url="http://test"
        ) as client:
            response = await client.get("/not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["error"]["code"] == "DOCUMENT_NOT_FOUND"

    async def test_invalid_document_returns_400(self, error_app: FastAPI) -> None:
        async with AsyncClient(
            transport=self._transport(error_app), base_url="http://test"
        ) as client:
            response = await client.get("/invalid")
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_DOCUMENT"

    async def test_unhandled_exception_returns_500(self, error_app: FastAPI) -> None:
        async with AsyncClient(
            transport=self._transport(error_app), base_url="http://test"
        ) as client:
            response = await client.get("/crash")
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
