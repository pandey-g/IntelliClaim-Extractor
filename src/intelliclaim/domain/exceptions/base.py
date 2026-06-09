"""Base domain exception hierarchy."""


class DomainError(Exception):
    """Base class for all domain-level errors."""

    def __init__(self, message: str, *, code: str = "DOMAIN_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code
