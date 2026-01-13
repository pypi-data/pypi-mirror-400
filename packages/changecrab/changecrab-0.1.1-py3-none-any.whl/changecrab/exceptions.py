"""Custom exceptions for the ChangeCrab SDK."""

import json
from typing import Any, Dict, Optional


def _truncate_response_body(response_data: Optional[Dict[str, Any]], max_length: int = 500) -> str:
    """Truncate response body for safe display in error messages."""
    if not response_data:
        return ""
    try:
        body_str = json.dumps(response_data, indent=2)
        if len(body_str) <= max_length:
            return body_str
        return body_str[:max_length] + f"\n... (truncated, {len(body_str)} chars total)"
    except (TypeError, ValueError):
        return str(response_data)[:max_length]


class ChangeCrabError(Exception):
    """Base exception for all ChangeCrab SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_id = request_id

    def __str__(self) -> str:
        parts = []
        if self.status_code:
            parts.append(f"[{self.status_code}]")
        parts.append(self.message)
        if self.request_id:
            parts.append(f"(Request ID: {self.request_id})")
        if self.response_data:
            truncated_body = _truncate_response_body(self.response_data)
            if truncated_body:
                parts.append(f"\nResponse: {truncated_body}")
        return " ".join(parts)


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
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, status_code, response_data, request_id)
        self.errors = errors or {}

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.errors:
            error_details = "; ".join(
                f"{field}: {', '.join(msgs)}" for field, msgs in self.errors.items()
            )
            return f"{base_str} - Field errors: {error_details}"
        return base_str


class RateLimitError(ChangeCrabError):
    """Raised when the API rate limit has been exceeded."""

    pass


class ServerError(ChangeCrabError):
    """Raised when the API returns a server error (5xx status codes)."""

    pass

