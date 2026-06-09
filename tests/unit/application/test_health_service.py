"""Unit tests for health service."""

import pytest

from intelliclaim.application.services.health_service import HealthService


@pytest.mark.unit
class TestHealthService:
    def test_healthy_when_all_components_healthy(self) -> None:
        service = HealthService()
        result = service.check(
            component_statuses={"api": "healthy", "database": "healthy"},
        )
        assert result.status == "healthy"
        assert result.version == "0.1.0"

    def test_degraded_when_component_unhealthy(self) -> None:
        service = HealthService()
        result = service.check(
            component_statuses={"api": "healthy", "database": "unhealthy"},
        )
        assert result.status == "degraded"

    def test_healthy_with_no_components(self) -> None:
        service = HealthService()
        result = service.check()
        assert result.status == "healthy"
