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
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def reset_settings_cache() -> Generator[None, None, None]:
    """Reset settings cache between tests."""
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="session")
def postgres_database_url() -> str:
    """Async SQLAlchemy URL for repository integration tests."""
    env_url = os.environ.get("DATABASE_URL")
    if env_url:
        return env_url

    try:
        from testcontainers.postgres import PostgresContainer
    except ImportError as exc:
        pytest.skip(f"PostgreSQL unavailable: {exc}")

    try:
        with PostgresContainer("postgres:16-alpine") as postgres:
            sync_url = postgres.get_connection_url()
            async_url = sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
            async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")
            yield async_url
    except Exception as exc:
        pytest.skip(f"PostgreSQL testcontainer unavailable: {exc}")


@pytest.fixture
async def db_manager(postgres_database_url: str):
    """Database session manager with schema created for integration tests."""
    from intelliclaim.infrastructure.database.base import Base
    from intelliclaim.infrastructure.database.session import DatabaseSessionManager
    from intelliclaim.infrastructure.config.settings import Settings

    settings = Settings(
        secret_key="test-secret-key-for-pytest-runs-32chars",
        database_url=postgres_database_url,
    )
    manager = DatabaseSessionManager(settings)

    async with manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield manager

    async with manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await manager.close()


@pytest.fixture
def repositories(db_manager):
    """Wired repository bundle backed by test PostgreSQL."""
    from intelliclaim.infrastructure.bootstrap import create_repositories

    return create_repositories(db_manager)
