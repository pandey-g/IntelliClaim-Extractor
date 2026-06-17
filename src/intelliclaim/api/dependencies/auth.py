"""Authentication dependencies for API endpoints."""

from typing import Annotated

from fastapi import Header, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from intelliclaim.domain.exceptions.security import AuthenticationError
from intelliclaim.infrastructure.config.settings import Settings
from intelliclaim.infrastructure.security.jwt_handler import JWTHandler

bearer_scheme = HTTPBearer(auto_error=False)


def _get_request_settings(request: Request) -> Settings:
    settings = getattr(request.app.state, "settings", None)
    if settings is None:
        msg = "Application settings not configured"
        raise RuntimeError(msg)
    return settings


def _validate_api_key(api_key: str, settings: Settings) -> str:
    """Validate API key and return actor identifier."""
    if api_key not in settings.api_key_list:
        raise AuthenticationError("Invalid API key")
    return f"api-key:{api_key[:8]}"


def _validate_bearer_token(token: str, settings: Settings) -> str:
    """Validate JWT bearer token and return subject as actor."""
    handler = JWTHandler(settings)
    payload = handler.decode_token(token)
    subject = payload["sub"]
    if not isinstance(subject, str):
        raise AuthenticationError("Invalid token subject")
    return f"jwt:{subject}"


async def get_current_actor(
    request: Request,
    api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer_scheme),
    ] = None,
) -> str:
    """Authenticate request via API key or JWT bearer token."""
    settings = _get_request_settings(request)

    if api_key:
        return _validate_api_key(api_key, settings)

    if credentials and credentials.credentials:
        return _validate_bearer_token(credentials.credentials, settings)

    if settings.is_production:
        raise AuthenticationError("Authentication required")

    if settings.api_key_list:
        raise AuthenticationError("Authentication required")

    return "development-anonymous"
