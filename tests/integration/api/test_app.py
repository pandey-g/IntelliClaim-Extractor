"""Integration tests for application setup."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestApplicationSetup:
    async def test_openapi_docs_available(self, client: AsyncClient) -> None:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        assert "IntelliClaim Extractor" in response.json()["info"]["title"]

    async def test_unknown_route_returns_structured_error(self, client: AsyncClient) -> None:
        response = await client.get("/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "HTTP_ERROR"
