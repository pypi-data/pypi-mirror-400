"""Exceptions for the Vestaboard Read/Write API client."""

from __future__ import annotations

from typing import Any, Optional


class ApiError(Exception):
    """Base exception for all API errors.

    Attributes:
        message: A human-readable error message.
        status_code: The HTTP status code, if available.
        response_data: Best-effort parsed response payload (JSON when possible),
            if available.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        response_data: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self) -> str:  # pragma: no cover
        if self.status_code is None:
            return self.message
        return f"{self.status_code}: {self.message}"


class AuthenticationError(ApiError):
    """Raised when authentication fails or the API key is missing."""


class ValidationError(ApiError):
    """Raised when request validation fails (client-side or HTTP 400)."""


class NotFoundError(ApiError):
    """Raised when a requested resource cannot be found (HTTP 404)."""


class RateLimitError(ApiError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""


class ServerError(ApiError):
    """Raised for server-side errors (HTTP 5xx)."""


class NetworkError(ApiError):
    """Raised when a network/transport error occurs before receiving a response."""
