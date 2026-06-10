"""Unit tests for application entry point."""

import pytest

from intelliclaim import main


@pytest.mark.unit
class TestMain:
    def test_app_is_created(self) -> None:
        assert main.app is not None
        assert main.app.title == "IntelliClaim Extractor"
