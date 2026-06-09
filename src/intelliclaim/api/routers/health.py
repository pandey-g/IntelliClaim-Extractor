"""Health check endpoints."""

from fastapi import APIRouter, Request

from intelliclaim.api.schemas.health import HealthResponse
from intelliclaim.application.services.health_service import HealthService

router = APIRouter()
health_service = HealthService()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """Return application health status including component checks."""
    components: dict[str, str] = {"api": "healthy"}

    db_manager = getattr(request.app.state, "db_manager", None)
    if db_manager is not None:
        db_healthy = await db_manager.health_check()
        components["database"] = "healthy" if db_healthy else "unhealthy"

    status = health_service.check(component_statuses=components)

    return HealthResponse(
        status=status.status,
        version=status.version,
        timestamp=status.timestamp,
        components=status.components,
    )
