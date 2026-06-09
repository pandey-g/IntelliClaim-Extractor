"""Integration tests for health endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestHealthEndpoint:
    async def test_health_returns_200(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_response_schema(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert data["version"] == "0.1.0"
        assert "timestamp" in data
        assert "components" in data
        assert data["components"]["api"] == "healthy"

    async def test_health_includes_request_id_header(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert "X-Request-ID" in response.headers

    async def test_health_propagates_request_id(self, client: AsyncClient) -> None:
        custom_id = "test-request-id-12345"
        response = await client.get("/health", headers={"X-Request-ID": custom_id})
        assert response.headers["X-Request-ID"] == custom_id
