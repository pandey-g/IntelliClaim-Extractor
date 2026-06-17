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
from intelliclaim.api.routers import documents, health
from intelliclaim.application.container import Container
from intelliclaim.infrastructure.bootstrap import (
    create_document_storage,
    create_extraction_pipeline,
    create_ocr_pipeline,
    create_repositories,
)
from intelliclaim.infrastructure.config.settings import Settings, get_settings
from intelliclaim.infrastructure.database.session import DatabaseSessionManager
from intelliclaim.infrastructure.logging.setup import configure_logging, get_logger
from intelliclaim.infrastructure.observability.telemetry import setup_telemetry

logger = get_logger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Application lifespan manager for startup and shutdown."""
        active_settings: Settings = app.state.settings
        configure_logging(active_settings)

        db_manager = DatabaseSessionManager(active_settings)
        container = Container(settings=active_settings)
        repositories = create_repositories(db_manager)
        container.wire_repositories(
            document_repository=repositories.document_repository,
            document_page_repository=repositories.document_page_repository,
            ocr_result_repository=repositories.ocr_result_repository,
            extracted_field_repository=repositories.extracted_field_repository,
            processing_job_repository=repositories.processing_job_repository,
            audit_log_repository=repositories.audit_log_repository,
        )
        container.wire_storage(document_storage=create_document_storage(active_settings))
        ocr_pipeline = create_ocr_pipeline(active_settings)
        container.wire_ocr(
            page_renderer=ocr_pipeline.page_renderer,
            image_preprocessor=ocr_pipeline.image_preprocessor,
            ocr_service=ocr_pipeline.ocr_service,
        )
        extraction_pipeline = create_extraction_pipeline(active_settings)
        container.wire_extraction(
            layout_analyzer=extraction_pipeline.layout_analyzer,
            field_extractor=extraction_pipeline.field_extractor,
        )
        set_container(container)

        app.state.db_manager = db_manager

        logger.info(
            "application_starting",
            app_name=active_settings.app_name,
            environment=active_settings.app_env,
            version=__version__,
        )

        yield

        await db_manager.close()
        logger.info("application_shutdown_complete")

    app = FastAPI(
        title=app_settings.app_name,
        version=__version__,
        description="AI-powered document intelligence platform for insurance claim processing",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    app.state.settings = app_settings

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(LoggingMiddleware)

    register_exception_handlers(app)

    from intelliclaim.api.dependencies.rate_limit import limiter

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    app.include_router(health.router, tags=["Health"])
    app.include_router(documents.router)

    setup_telemetry(app, app_settings)

    return app
