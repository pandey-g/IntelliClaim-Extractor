"""FastAPI application factory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from intelliclaim import __version__
from intelliclaim.api.dependencies.container import set_container
from intelliclaim.api.middleware.exception_handler import register_exception_handlers
from intelliclaim.api.middleware.logging import LoggingMiddleware
from intelliclaim.api.middleware.request_id import RequestIdMiddleware
from intelliclaim.api.routers import health
from intelliclaim.application.container import Container
from intelliclaim.infrastructure.config.settings import Settings, get_settings
from intelliclaim.infrastructure.database.session import DatabaseSessionManager
from intelliclaim.infrastructure.logging.setup import configure_logging, get_logger
from intelliclaim.infrastructure.observability.telemetry import setup_telemetry

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown."""
    settings = get_settings()
    configure_logging(settings)

    db_manager = DatabaseSessionManager(settings)
    container = Container(settings=settings)
    set_container(container)

    app.state.db_manager = db_manager
    app.state.settings = settings

    logger.info(
        "application_starting",
        app_name=settings.app_name,
        environment=settings.app_env,
        version=__version__,
    )

    yield

    await db_manager.close()
    logger.info("application_shutdown_complete")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app_settings = settings or get_settings()

    app = FastAPI(
        title=app_settings.app_name,
        version=__version__,
        description="AI-powered document intelligence platform for insurance claim processing",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(LoggingMiddleware)

    register_exception_handlers(app)

    from intelliclaim.api.dependencies.rate_limit import limiter

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    app.include_router(health.router, tags=["Health"])

    setup_telemetry(app, app_settings)

    return app
