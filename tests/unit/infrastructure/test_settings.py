"""Unit tests for application settings."""

import pytest

from intelliclaim.infrastructure.config.settings import Settings


@pytest.mark.unit
class TestSettings:
    def test_api_key_list_parsing(self) -> None:
        settings = Settings(
            secret_key="test-secret-key-for-pytest-runs-32chars",
            api_keys="key1, key2 , key3",
        )
        assert settings.api_key_list == ["key1", "key2", "key3"]

    def test_allowed_extension_list(self) -> None:
        settings = Settings(
            secret_key="test-secret-key-for-pytest-runs-32chars",
            allowed_extensions="pdf,png,jpg",
        )
        assert settings.allowed_extension_list == ["pdf", "png", "jpg"]

    def test_max_upload_size_bytes(self) -> None:
        settings = Settings(
            secret_key="test-secret-key-for-pytest-runs-32chars",
            max_upload_size_mb=25,
        )
        assert settings.max_upload_size_bytes == 25 * 1024 * 1024

    def test_is_production(self) -> None:
        settings = Settings(
            secret_key="test-secret-key-for-pytest-runs-32chars",
            app_env="production",
        )
        assert settings.is_production is True
