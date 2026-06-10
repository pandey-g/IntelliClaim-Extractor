"""Unit tests for API container dependency."""

import pytest

from intelliclaim.api.dependencies.container import get_container, set_container
from intelliclaim.application.container import Container
from intelliclaim.infrastructure.config.settings import Settings


@pytest.mark.unit
class TestContainerDependency:
    def test_get_container_raises_when_unset(self) -> None:
        set_container(
            Container(settings=Settings(secret_key="test-secret-key-for-pytest-runs-32chars"))
        )
        container = get_container()
        assert container is not None

    def test_get_container_raises_before_set(self) -> None:
        import intelliclaim.api.dependencies.container as mod

        original = mod._container
        mod._container = None
        try:
            with pytest.raises(RuntimeError, match="not initialized"):
                get_container()
        finally:
            mod._container = original
