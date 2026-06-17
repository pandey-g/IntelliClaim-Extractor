"""Unit tests for JWT handler."""

import pytest

from intelliclaim.domain.exceptions.security import AuthenticationError
from intelliclaim.infrastructure.config.settings import Settings
from intelliclaim.infrastructure.security.jwt_handler import JWTHandler


@pytest.mark.unit
class TestJWTHandler:
    @pytest.fixture
    def handler(self) -> JWTHandler:
        settings = Settings(secret_key="test-secret-key-for-pytest-runs-32chars")
        return JWTHandler(settings)

    def test_create_and_decode_token(self, handler: JWTHandler) -> None:
        token = handler.create_access_token("service-account")
        payload = handler.decode_token(token)
        assert payload["sub"] == "service-account"

    def test_rejects_invalid_token(self, handler: JWTHandler) -> None:
        with pytest.raises(AuthenticationError):
            handler.decode_token("invalid.token.value")
