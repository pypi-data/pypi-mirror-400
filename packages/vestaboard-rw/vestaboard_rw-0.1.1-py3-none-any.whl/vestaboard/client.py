"""Facade client for the Vestaboard Read/Write API."""

from __future__ import annotations

from typing import Optional

from vestaboard.read_write import ReadWriteClient


class VestaboardClient:
    """Top-level client that exposes the Vestaboard Read/Write API.

    This library intentionally focuses on the Read/Write API only:
    - `https://docs.vestaboard.com/docs/read-write-api/introduction`

    Args:
        api_key: Vestaboard Read/Write API key. If not provided, sub-clients will
            read from `VESTABOARD_READ_WRITE_API_KEY`.
        base_url: Override for the Read/Write base URL. Defaults to
            `https://rw.vestaboard.com`.
        timeout_seconds: Default request timeout in seconds for sub-clients.
        max_retries: Number of retries for transient failures for sub-clients.
        retry_backoff_seconds: Base seconds for exponential backoff for sub-clients.
        load_dotenv: If True, attempts to load environment variables from a `.env`
            file using `python-dotenv` (must be installed via the `dotenv` extra).
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_backoff_seconds: Optional[float] = None,
        load_dotenv: bool = False,
    ) -> None:
        if load_dotenv:
            try:
                from dotenv import load_dotenv as _load_dotenv
            except ImportError as exc:  # pragma: no cover
                raise ImportError(
                    "python-dotenv is not installed. Install with: "
                    "pip install 'vestaboard-rw[dotenv]'"
                ) from exc
            _load_dotenv()

        self._api_key = api_key
        self._base_url = base_url
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._retry_backoff_seconds = retry_backoff_seconds

        self._read_write: Optional[ReadWriteClient] = None

    @property
    def read_write(self) -> ReadWriteClient:
        """Access the Read/Write API client (lazy-loaded)."""
        if self._read_write is None:
            self._read_write = ReadWriteClient(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout_seconds=self._timeout_seconds,
                max_retries=self._max_retries,
                retry_backoff_seconds=self._retry_backoff_seconds,
            )
        return self._read_write

    @property
    def rw(self) -> ReadWriteClient:
        """Alias for `read_write`."""
        return self.read_write
