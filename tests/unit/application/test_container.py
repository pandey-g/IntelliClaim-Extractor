"""Unit tests for dependency injection container."""

import pytest

from intelliclaim.application.container import Container
from intelliclaim.infrastructure.config.settings import Settings


@pytest.mark.unit
class TestContainer:
    @pytest.fixture
    def container(self) -> Container:
        return Container(
            settings=Settings(secret_key="test-secret-key-for-pytest-runs-32chars"),
        )

    def test_require_repositories_raises_when_not_wired(self, container: Container) -> None:
        with pytest.raises(RuntimeError, match="Repositories not initialized"):
            container.require_repositories_initialized()

    def test_documents_raises_when_not_wired(self, container: Container) -> None:
        with pytest.raises(RuntimeError, match="Repositories not initialized"):
            _ = container.documents
