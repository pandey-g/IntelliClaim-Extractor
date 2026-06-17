"""Unit tests for authentication dependencies."""

import pytest

from intelliclaim.api.dependencies.auth import get_current_actor
from intelliclaim.domain.exceptions.security import AuthenticationError
from intelliclaim.infrastructure.config.settings import Settings
from intelliclaim.infrastructure.security.jwt_handler import JWTHandler


@pytest.mark.unit
class TestAuthentication:
    @pytest.fixture
    def settings(self) -> Settings:
        return Settings(
            secret_key="test-secret-key-for-pytest-runs-32chars",
            api_keys="valid-key-12345",
        )

    @pytest.fixture
    def mock_request(self, settings: Settings):
        from unittest.mock import MagicMock

        request = MagicMock()
        request.app.state.settings = settings
        return request

    async def test_api_key_authentication(self, mock_request, settings: Settings) -> None:
        actor = await get_current_actor(request=mock_request, api_key="valid-key-12345")
        assert actor.startswith("api-key:")

    async def test_invalid_api_key_raises(self, mock_request, settings: Settings) -> None:
        with pytest.raises(AuthenticationError):
            await get_current_actor(request=mock_request, api_key="wrong-key")

    async def test_jwt_authentication(self, mock_request, settings: Settings) -> None:
        from fastapi.security import HTTPAuthorizationCredentials

        token = JWTHandler(settings).create_access_token("service-user")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        actor = await get_current_actor(request=mock_request, credentials=credentials)
        assert actor == "jwt:service-user"

    async def test_missing_credentials_raises_when_keys_configured(
        self,
        mock_request,
        settings: Settings,
    ) -> None:
        with pytest.raises(AuthenticationError):
            await get_current_actor(request=mock_request)
