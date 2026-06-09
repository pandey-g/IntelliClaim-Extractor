"""Security-related domain exceptions."""

from intelliclaim.domain.exceptions.base import DomainError


class AuthenticationError(DomainError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message=message, code="AUTHENTICATION_ERROR")


class AuthorizationError(DomainError):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message=message, code="AUTHORIZATION_ERROR")
