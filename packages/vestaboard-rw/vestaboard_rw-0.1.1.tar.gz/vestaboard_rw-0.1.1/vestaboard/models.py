"""Typed models for the Vestaboard Read/Write API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence


@dataclass(frozen=True)
class CurrentMessage:
    """The current message displayed on a Vestaboard.

    Attributes:
        layout: A JSON-encoded string representing the board layout as a nested
            array of character codes.
        id: The message identifier.
    """

    layout: str
    id: str

    def layout_as_list(self) -> list[list[int]]:
        """Parse the JSON layout string into a nested list of character codes.

        Returns:
            The layout as `List[List[int]]`.

        Raises:
            ValueError: If the layout cannot be parsed as the expected structure.
        """
        parsed = json.loads(self.layout)
        if not isinstance(parsed, list):
            raise ValueError("Layout JSON must be a list of rows.")

        rows: list[list[int]] = []
        for row in parsed:
            if not isinstance(row, list):
                raise ValueError("Each layout row must be a list.")
            int_row: list[int] = []
            for value in row:
                if not isinstance(value, int):
                    raise ValueError("Each layout cell must be an int character code.")
                int_row.append(value)
            rows.append(int_row)
        return rows


@dataclass(frozen=True)
class CurrentMessageResponse:
    """Response model for the 'Read Current Message' endpoint."""

    current_message: CurrentMessage

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> CurrentMessageResponse:
        """Create an instance from the API response payload.

        Args:
            data: The decoded JSON response payload.

        Returns:
            A parsed `CurrentMessageResponse`.

        Raises:
            KeyError: If required keys are missing.
            TypeError: If payload types are unexpected.
        """
        current = data["currentMessage"]
        if not isinstance(current, Mapping):
            raise TypeError("currentMessage must be an object.")

        layout = current["layout"]
        message_id = current["id"]
        if not isinstance(layout, str):
            raise TypeError("currentMessage.layout must be a string.")
        if not isinstance(message_id, str):
            raise TypeError("currentMessage.id must be a string.")

        return cls(current_message=CurrentMessage(layout=layout, id=message_id))


@dataclass(frozen=True)
class SendMessageResponse:
    """Response model for the 'Send Message' endpoint."""

    status: str
    id: str
    created: int

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> SendMessageResponse:
        """Create an instance from the API response payload.

        Args:
            data: The decoded JSON response payload.

        Returns:
            A parsed `SendMessageResponse`.

        Raises:
            KeyError: If required keys are missing.
            TypeError: If payload types are unexpected.
        """
        status = data["status"]
        message_id = data["id"]
        created = data["created"]

        if not isinstance(status, str):
            raise TypeError("status must be a string.")
        if not isinstance(message_id, str):
            raise TypeError("id must be a string.")
        if not isinstance(created, int):
            raise TypeError("created must be an int (epoch milliseconds).")

        return cls(status=status, id=message_id, created=created)


def coerce_layout(layout: Sequence[Sequence[int]]) -> list[list[int]]:
    """Coerce a layout into a JSON-serializable nested list of ints.

    Args:
        layout: A nested sequence of integer character codes.

    Returns:
        A nested list of ints.

    Raises:
        TypeError: If the layout contains non-int values.
        ValueError: If the layout is empty or not rectangular.
    """
    rows: list[list[int]] = []
    expected_cols: Optional[int] = None

    for row in layout:
        int_row: list[int] = []
        for value in row:
            if not isinstance(value, int):
                raise TypeError("Layout values must be integers.")
            int_row.append(value)
        if expected_cols is None:
            expected_cols = len(int_row)
            if expected_cols == 0:
                raise ValueError("Layout rows must not be empty.")
        elif len(int_row) != expected_cols:
            raise ValueError("Layout must be rectangular (all rows same length).")
        rows.append(int_row)

    if not rows:
        raise ValueError("Layout must contain at least one row.")
    return rows
