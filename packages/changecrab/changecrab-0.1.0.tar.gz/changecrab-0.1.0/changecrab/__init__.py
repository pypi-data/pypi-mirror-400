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

__version__ = "0.1.0"
__all__ = [
    "ChangeCrab",
    "ChangeCrabError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "Changelog",
    "Post",
    "Category",
]

