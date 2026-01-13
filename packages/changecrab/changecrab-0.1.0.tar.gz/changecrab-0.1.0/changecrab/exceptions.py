"""Custom exceptions for the ChangeCrab SDK."""

from typing import Any, Dict, Optional


class ChangeCrabError(Exception):
    """Base exception for all ChangeCrab SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(ChangeCrabError):
    """Raised when API authentication fails."""

    pass


class NotFoundError(ChangeCrabError):
    """Raised when a requested resource is not found."""

    pass


class ValidationError(ChangeCrabError):
    """Raised when request data fails validation."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        errors: Optional[Dict[str, list]] = None,
    ) -> None:
        super().__init__(message, status_code, response_data)
        self.errors = errors or {}

    def __str__(self) -> str:
        if self.errors:
            error_details = "; ".join(
                f"{field}: {', '.join(msgs)}" for field, msgs in self.errors.items()
            )
            return f"{self.message} - {error_details}"
        return super().__str__()


class RateLimitError(ChangeCrabError):
    """Raised when the API rate limit has been exceeded."""

    pass


class ServerError(ChangeCrabError):
    """Raised when the API returns a server error (5xx status codes)."""

    pass

