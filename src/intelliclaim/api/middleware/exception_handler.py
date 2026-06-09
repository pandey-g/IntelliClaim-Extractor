"""Global exception handlers for standardized error responses."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from intelliclaim.api.schemas.errors import ErrorDetail, ErrorResponse
from intelliclaim.domain.exceptions.base import DomainError
from intelliclaim.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)

DOMAIN_ERROR_STATUS_MAP: dict[str, int] = {
    "DOCUMENT_NOT_FOUND": 404,
    "INVALID_DOCUMENT": 400,
    "AUTHENTICATION_ERROR": 401,
    "AUTHORIZATION_ERROR": 403,
    "VALIDATION_ERROR": 422,
    "EXTRACTION_ERROR": 422,
    "DOCUMENT_PROCESSING_ERROR": 500,
}


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers."""

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        status_code = DOMAIN_ERROR_STATUS_MAP.get(exc.code, 400)
        request_id = getattr(request.state, "request_id", None)

        logger.warning(
            "domain_error",
            error_code=exc.code,
            message=exc.message,
            request_id=request_id,
        )

        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(
                error=ErrorDetail(code=exc.code, message=exc.message),
                request_id=request_id,
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        errors = exc.errors()

        logger.warning(
            "validation_error",
            errors=errors,
            request_id=request_id,
        )

        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="VALIDATION_ERROR",
                    message="Request validation failed",
                    details=errors,
                ),
                request_id=request_id,
            ).model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="HTTP_ERROR",
                    message=str(exc.detail),
                ),
                request_id=request_id,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)

        logger.exception(
            "unhandled_exception",
            error=str(exc),
            request_id=request_id,
        )

        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="An unexpected error occurred",
                ),
                request_id=request_id,
            ).model_dump(),
        )
