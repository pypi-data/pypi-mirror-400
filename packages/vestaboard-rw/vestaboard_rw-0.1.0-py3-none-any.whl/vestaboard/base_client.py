"""HTTP transport and shared behavior for the Vestaboard Read/Write API client."""

from __future__ import annotations

import json
import os
import time
from typing import Any, Mapping, MutableMapping, Optional

import requests

from vestaboard.exceptions import (
    ApiError,
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)

DEFAULT_BASE_URL = "https://rw.vestaboard.com"
DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_SECONDS = 0.5

READ_WRITE_API_KEY_ENV_VAR = "VESTABOARD_READ_WRITE_API_KEY"

ENV_PREFIX = "VESTABOARD"
TIMEOUT_ENV_VAR = f"{ENV_PREFIX}_TIMEOUT_SECONDS"
MAX_RETRIES_ENV_VAR = f"{ENV_PREFIX}_MAX_RETRIES"
RETRY_BACKOFF_ENV_VAR = f"{ENV_PREFIX}_RETRY_BACKOFF_SECONDS"

API_KEY_HEADER_NAME = "X-Vestaboard-Read-Write-Key"

_RETRYABLE_STATUS_CODES = {500, 502, 503, 504}


def _read_env_str(name: str) -> Optional[str]:
    """Read an environment variable as a string.

    Args:
        name: Environment variable name.

    Returns:
        The environment variable value if set and non-empty; otherwise None.
    """
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _read_env_int(name: str) -> Optional[int]:
    """Read an environment variable as an integer.

    Args:
        name: Environment variable name.

    Returns:
        The parsed integer value, or None if unset or invalid.
    """
    raw = _read_env_str(name)
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _read_env_float(name: str) -> Optional[float]:
    """Read an environment variable as a float.

    Args:
        name: Environment variable name.

    Returns:
        The parsed float value, or None if unset or invalid.
    """
    raw = _read_env_str(name)
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


class BaseClient:
    """Base HTTP client for Vestaboard Read/Write API requests.

    This class owns the `requests.Session` and implements:
    - API key sourcing and default headers
    - Request timeouts and retries with exponential backoff
    - Consistent error mapping (HTTP status -> exception type)

    Args:
        api_key: Vestaboard Read/Write API key. If not provided, the client will
            attempt to read it from the `VESTABOARD_READ_WRITE_API_KEY`
            environment variable.
        base_url: API base URL. Defaults to `https://rw.vestaboard.com`.
        timeout_seconds: Default request timeout in seconds. If not provided, the
            client will use `VESTABOARD_TIMEOUT_SECONDS` if set, otherwise a
            library default.
        max_retries: Number of retries for transient failures. If not provided,
            the client will use `VESTABOARD_MAX_RETRIES` if set, otherwise a
            library default.
        retry_backoff_seconds: Base backoff in seconds for exponential backoff.
            If not provided, the client will use `VESTABOARD_RETRY_BACKOFF_SECONDS`
            if set, otherwise a library default.

    Raises:
        AuthenticationError: If the API key cannot be resolved.
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_backoff_seconds: Optional[float] = None,
    ) -> None:
        resolved_key = api_key or _read_env_str(READ_WRITE_API_KEY_ENV_VAR)
        if not resolved_key:
            raise AuthenticationError(
                f"Missing Vestaboard Read/Write API key. Provide `api_key=` or set "
                f"{READ_WRITE_API_KEY_ENV_VAR}.",
                status_code=401,
            )

        self.api_key: str = resolved_key
        self.base_url: str = (base_url or DEFAULT_BASE_URL).rstrip("/")

        self.timeout_seconds: float = (
            timeout_seconds
            if timeout_seconds is not None
            else _read_env_float(TIMEOUT_ENV_VAR) or DEFAULT_TIMEOUT_SECONDS
        )
        self.max_retries: int = (
            max_retries
            if max_retries is not None
            else _read_env_int(MAX_RETRIES_ENV_VAR) or DEFAULT_MAX_RETRIES
        )
        self.retry_backoff_seconds: float = (
            retry_backoff_seconds
            if retry_backoff_seconds is not None
            else _read_env_float(RETRY_BACKOFF_ENV_VAR) or DEFAULT_RETRY_BACKOFF_SECONDS
        )

        if self.max_retries < 0:
            self.max_retries = 0
        if self.timeout_seconds <= 0:
            self.timeout_seconds = DEFAULT_TIMEOUT_SECONDS
        if self.retry_backoff_seconds < 0:
            self.retry_backoff_seconds = 0.0

        self.session = requests.Session()
        self.session.headers.update(
            {
                API_KEY_HEADER_NAME: self.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def __enter__(self) -> BaseClient:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def get(
        self,
        endpoint: str,
        params: Optional[Mapping[str, Any]] = None,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Send a GET request.

        Args:
            endpoint: API endpoint path (with or without leading slash).
            params: Optional query parameters.
            timeout_seconds: Overrides the client's default timeout for this call.

        Returns:
            Parsed JSON (dict/list/primitive) when possible; otherwise raw text.
        """
        return self._request(
            "GET", endpoint, params=params, timeout_seconds=timeout_seconds
        )

    def post(
        self,
        endpoint: str,
        json_data: Optional[Any] = None,
        data: Optional[Mapping[str, Any]] = None,
        files: Optional[Mapping[str, Any]] = None,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Send a POST request.

        Args:
            endpoint: API endpoint path (with or without leading slash).
            json_data: JSON-serializable payload to send via `json=...`.
            data: Form data (used with `files` uploads).
            files: Multipart files payload for uploads.
            timeout_seconds: Overrides the client's default timeout for this call.

        Returns:
            Parsed JSON (dict/list/primitive) when possible; otherwise raw text.
        """
        return self._request(
            "POST",
            endpoint,
            json_data=json_data,
            data=data,
            files=files,
            timeout_seconds=timeout_seconds,
        )

    def put(
        self,
        endpoint: str,
        json_data: Optional[Any] = None,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Send a PUT request."""
        return self._request(
            "PUT", endpoint, json_data=json_data, timeout_seconds=timeout_seconds
        )

    def patch(
        self,
        endpoint: str,
        json_data: Optional[Any] = None,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Send a PATCH request."""
        return self._request(
            "PATCH", endpoint, json_data=json_data, timeout_seconds=timeout_seconds
        )

    def delete(
        self,
        endpoint: str,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Send a DELETE request."""
        return self._request("DELETE", endpoint, timeout_seconds=timeout_seconds)

    def _build_url(self, endpoint: str) -> str:
        """Build a full URL for an endpoint."""
        endpoint_clean = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint_clean}"

    def _parse_response_data(self, response: requests.Response) -> Any:
        """Decode a response payload.

        Args:
            response: The HTTP response.

        Returns:
            Parsed JSON payload if possible, otherwise raw response text.
        """
        if response.status_code == 204:
            return {}
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text

    def _raise_mapped_error(self, response: requests.Response) -> None:
        """Raise an exception mapped from the response status code.

        Args:
            response: The HTTP response.

        Raises:
            ApiError: A mapped error subclass.
        """
        data = self._parse_response_data(response)
        message = "Request failed"

        if isinstance(data, Mapping):
            if "message" in data and isinstance(data["message"], str):
                message = data["message"]
            elif "error" in data and isinstance(data["error"], str):
                message = data["error"]
        elif isinstance(data, str) and data.strip():
            message = data.strip()

        status = response.status_code
        if status == 400:
            raise ValidationError(message, status_code=status, response_data=data)
        if status == 401:
            raise AuthenticationError(message, status_code=status, response_data=data)
        if status == 404:
            raise NotFoundError(message, status_code=status, response_data=data)
        if status == 429:
            raise RateLimitError(message, status_code=status, response_data=data)
        if 500 <= status <= 599:
            raise ServerError(message, status_code=status, response_data=data)
        raise ApiError(message, status_code=status, response_data=data)

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json_data: Optional[Any] = None,
        data: Optional[Mapping[str, Any]] = None,
        files: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """Send an HTTP request with retries and error mapping.

        Args:
            method: HTTP method (GET/POST/PUT/PATCH/DELETE).
            endpoint: Endpoint path (with or without leading slash).
            json_data: JSON-serializable payload.
            data: Form data payload (used with files).
            files: Files payload for multipart requests.
            params: Query parameters.
            timeout_seconds: Override timeout for this call.

        Returns:
            Parsed JSON payload if possible, otherwise raw response text.

        Raises:
            NetworkError: On request transport errors after retries.
            ApiError: On non-2xx responses after applying retries and mapping.
        """
        url = self._build_url(endpoint)
        timeout = (
            timeout_seconds if timeout_seconds is not None else self.timeout_seconds
        )

        for attempt in range(self.max_retries + 1):
            try:
                if files is not None:
                    # For multipart requests, allow requests to set the boundary and
                    # Content-Type.
                    headers: MutableMapping[str, str] = {
                        str(k): str(v) for k, v in self.session.headers.items()
                    }
                    headers.pop("Content-Type", None)
                    response = self.session.request(
                        method=method,
                        url=url,
                        params=params,
                        data=data,
                        files=files,
                        timeout=timeout,
                        headers=headers,
                    )
                else:
                    response = self.session.request(
                        method=method,
                        url=url,
                        params=params,
                        json=json_data,
                        timeout=timeout,
                    )
            except requests.exceptions.RequestException as exc:
                if attempt < self.max_retries:
                    backoff = self.retry_backoff_seconds * (2**attempt)
                    time.sleep(backoff)
                    continue
                raise NetworkError(
                    str(exc),
                    status_code=None,
                    response_data=None,
                ) from exc

            if (
                response.status_code in _RETRYABLE_STATUS_CODES
                and attempt < self.max_retries
            ):
                backoff = self.retry_backoff_seconds * (2**attempt)
                time.sleep(backoff)
                continue

            if response.status_code >= 400:
                self._raise_mapped_error(response)

            return self._parse_response_data(response)

        # Defensive: loop should have returned or raised.
        raise ApiError(
            "Request failed unexpectedly",
            status_code=None,
            response_data=None,
        )  # pragma: no cover
