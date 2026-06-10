"""Unit tests for logging setup."""

import pytest

from intelliclaim.infrastructure.config.settings import Settings
from intelliclaim.infrastructure.logging.setup import configure_logging, get_logger


@pytest.mark.unit
class TestLogging:
    def test_configure_json_logging(self) -> None:
        settings = Settings(
            secret_key="test-secret-key-for-pytest-runs-32chars",
            log_format="json",
            log_level="DEBUG",
        )
        configure_logging(settings)
        logger = get_logger("test")
        assert logger is not None

    def test_configure_console_logging(self) -> None:
        settings = Settings(
            secret_key="test-secret-key-for-pytest-runs-32chars",
            log_format="console",
        )
        configure_logging(settings)
        logger = get_logger("test", component="api")
        assert logger is not None
