"""Read/Write API client for Vestaboard."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

from vestaboard.base_client import BaseClient, DEFAULT_BASE_URL
from vestaboard.exceptions import ApiError, ValidationError
from vestaboard.models import CurrentMessageResponse, SendMessageResponse, coerce_layout

_FLAGSHIP_DIMS = (6, 22)
_NOTE_DIMS = (3, 15)


class ReadWriteClient(BaseClient):
    """Client for the Vestaboard Read/Write API (`rw.vestaboard.com`).

    This client implements only the Read/Write API endpoints:
    - GET `/` to read the current message
    - POST `/` to send a new message (text or a layout array)

    Authentication is via the `X-Vestaboard-Read-Write-Key` request header as
    documented by Vestaboard:
    - `https://docs.vestaboard.com/docs/read-write-api/authentication`

    Args:
        api_key: Vestaboard Read/Write API key. If not provided, the client will
            attempt to read it from the `VESTABOARD_READ_WRITE_API_KEY`
            environment variable.
        base_url: Base URL for the Read/Write API. Defaults to
            `https://rw.vestaboard.com`.
        timeout_seconds: Default request timeout in seconds.
        max_retries: Number of retries for transient failures.
        retry_backoff_seconds: Base seconds for exponential backoff.
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
        super().__init__(
            api_key=api_key,
            base_url=base_url or DEFAULT_BASE_URL,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff_seconds,
        )

    def get_current_message(self) -> CurrentMessageResponse:
        """Read the current message from the Vestaboard.

        This corresponds to:
        - GET `https://rw.vestaboard.com/`

        Returns:
            The current message response, including the message layout string and id.

        Raises:
            ApiError: If the API returns a non-success response or unexpected payload.
        """
        payload = self.get("")
        if not isinstance(payload, Mapping):
            raise ApiError(
                "Unexpected response payload type for current message.",
                status_code=None,
                response_data=None,
            )
        return CurrentMessageResponse.from_dict(payload)

    def send_message(
        self,
        *,
        text: Optional[str] = None,
        layout: Optional[Sequence[Sequence[int]]] = None,
    ) -> SendMessageResponse:
        """Send a new message to the Vestaboard.

        Vestaboard supports sending either:
        - a JSON object: `{"text": "Hello World"}`
        - or a raw JSON array-of-arrays representing a layout (character codes)

        This corresponds to:
        - POST `https://rw.vestaboard.com/`

        Notes:
            Vestaboard may drop messages if more than one message is sent every 15
            seconds (rate limiting behavior).

        Args:
            text: Text to display.
            layout: Explicit layout as a nested array of character codes.

        Returns:
            The send message response containing status, message id, and created
            timestamp.

        Raises:
            ValidationError: If inputs are invalid (blank text, both inputs, invalid
                layout).
            ApiError: If the API returns a non-success response or unexpected payload.
        """
        if (text is None and layout is None) or (
            text is not None and layout is not None
        ):
            raise ValidationError(
                "Provide exactly one of `text` or `layout`.",
                status_code=400,
                response_data=None,
            )

        json_body: Any
        if text is not None:
            if not text.strip():
                raise ValidationError(
                    "Text messages must not be blank.",
                    status_code=400,
                    response_data=None,
                )
            json_body = {"text": text}
        else:
            assert layout is not None
            try:
                layout_list = coerce_layout(layout)
            except (TypeError, ValueError) as exc:
                raise ValidationError(
                    str(exc),
                    status_code=400,
                    response_data=None,
                ) from exc
            rows = len(layout_list)
            cols = len(layout_list[0])
            if (rows, cols) not in {_FLAGSHIP_DIMS, _NOTE_DIMS}:
                raise ValidationError(
                    (
                        f"Layout must be {_FLAGSHIP_DIMS} (Flagship) or "
                        f"{_NOTE_DIMS} (Note). Got ({rows}, {cols})."
                    ),
                    status_code=400,
                    response_data=None,
                )
            json_body = layout_list

        payload = self.post("", json_data=json_body)
        if not isinstance(payload, Mapping):
            raise ApiError(
                "Unexpected response payload type for send message.",
                status_code=None,
                response_data=None,
            )
        return SendMessageResponse.from_dict(payload)
