"""Shared pytest fixtures."""

import os
from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-runs-32chars")
os.environ.setdefault("OTEL_ENABLED", "false")
os.environ.setdefault("PROMETHEUS_ENABLED", "false")

from intelliclaim.api.app import create_app  # noqa: E402
from intelliclaim.infrastructure.config.settings import Settings, get_settings  # noqa: E402


@pytest.fixture
def test_settings() -> Settings:
    """Provide test application settings."""
    get_settings.cache_clear()
    return Settings(
        secret_key="test-secret-key-for-pytest-runs-32chars",
        app_env="development",
        otel_enabled=False,
        prometheus_enabled=False,
        database_url="postgresql+asyncpg://test:test@localhost:5432/test",
    )


@pytest.fixture
def app(test_settings: Settings):
    """Create FastAPI test application."""
    get_settings.cache_clear()
    application = create_app(settings=test_settings)
    yield application
    get_settings.cache_clear()


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Provide async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def reset_settings_cache() -> Generator[None, None, None]:
    """Reset settings cache between tests."""
    yield
    get_settings.cache_clear()
