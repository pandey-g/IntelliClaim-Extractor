"""JWT token creation and validation."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from intelliclaim.domain.exceptions.security import AuthenticationError
from intelliclaim.infrastructure.config.settings import Settings


class JWTHandler:
    """Handles JWT encoding and decoding."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_access_token(
        self,
        subject: str,
        *,
        expires_minutes: int | None = None,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """Create a signed JWT access token."""
        expire_delta = timedelta(minutes=expires_minutes or self._settings.jwt_expire_minutes)
        expire = datetime.now(UTC) + expire_delta
        payload: dict[str, Any] = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.now(UTC),
        }
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(
            payload,
            self._settings.secret_key,
            algorithm=self._settings.jwt_algorithm,
        )

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT access token."""
        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[self._settings.jwt_algorithm],
            )
        except JWTError as exc:
            raise AuthenticationError("Invalid or expired token") from exc

        subject = payload.get("sub")
        if not subject or not isinstance(subject, str):
            raise AuthenticationError("Token missing subject claim")
        return payload
