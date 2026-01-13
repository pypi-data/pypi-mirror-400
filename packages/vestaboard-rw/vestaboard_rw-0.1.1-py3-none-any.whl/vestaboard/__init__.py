"""Vestaboard Read/Write API client library."""

from __future__ import annotations

from vestaboard.client import VestaboardClient
from vestaboard.exceptions import (
    ApiError,
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from vestaboard.models import (
    CurrentMessage,
    CurrentMessageResponse,
    SendMessageResponse,
)
from vestaboard.read_write import ReadWriteClient

__version__ = "0.1.1"

__all__ = [
    "ApiError",
    "AuthenticationError",
    "CurrentMessage",
    "CurrentMessageResponse",
    "NetworkError",
    "NotFoundError",
    "RateLimitError",
    "ReadWriteClient",
    "SendMessageResponse",
    "ServerError",
    "ValidationError",
    "VestaboardClient",
]
