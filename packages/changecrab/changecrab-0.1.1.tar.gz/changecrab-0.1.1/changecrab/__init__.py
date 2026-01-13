"""
ChangeCrab Python SDK

A clean, professional Python client for the ChangeCrab API.
Manage changelogs and posts programmatically.
"""

from changecrab.client import ChangeCrab
from changecrab.exceptions import (
    AuthenticationError,
    ChangeCrabError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from changecrab.models import Category, Changelog, Post

# Convenience alias for API errors
ApiError = ChangeCrabError

__version__ = "0.1.1"
__all__ = [
    "ChangeCrab",
    "ChangeCrabError",
    "ApiError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "Changelog",
    "Post",
    "Category",
]

