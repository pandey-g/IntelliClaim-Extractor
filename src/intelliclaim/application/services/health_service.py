"""Health check application service."""

from dataclasses import dataclass
from datetime import UTC, datetime

from intelliclaim import __version__


@dataclass(frozen=True, slots=True)
class HealthStatus:
    """Health check result."""

    status: str
    version: str
    timestamp: datetime
    components: dict[str, str]


class HealthService:
    """Provides application health status."""

    def check(self, *, component_statuses: dict[str, str] | None = None) -> HealthStatus:
        """Perform health check aggregating component statuses."""
        components = component_statuses or {}
        overall = "healthy" if all(s == "healthy" for s in components.values()) else "degraded"
        if not components:
            overall = "healthy"

        return HealthStatus(
            status=overall,
            version=__version__,
            timestamp=datetime.now(UTC),
            components=components,
        )
