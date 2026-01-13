import json
from typing import Any

import pytest
import requests
import responses

from vestaboard.exceptions import ApiError, ValidationError
from vestaboard.read_write import ReadWriteClient


@responses.activate
def test_get_current_message() -> None:
    client = ReadWriteClient(api_key="k", base_url="https://example.com")
    responses.add(
        responses.GET,
        "https://example.com/",
        json={"currentMessage": {"layout": "[[0]]", "id": "msg-1"}},
        status=200,
    )
    resp = client.get_current_message()
    assert resp.current_message.id == "msg-1"
    assert resp.current_message.layout == "[[0]]"


@responses.activate
def test_get_current_message_unexpected_payload_raises() -> None:
    client = ReadWriteClient(api_key="k", base_url="https://example.com")
    responses.add(
        responses.GET,
        "https://example.com/",
        body="not-json",
        status=200,
        content_type="text/plain",
    )
    with pytest.raises(ApiError):
        client.get_current_message()


@responses.activate
def test_send_message_text() -> None:
    client = ReadWriteClient(api_key="k", base_url="https://example.com")

    def callback(request: requests.PreparedRequest) -> tuple[int, dict[str, str], str]:
        body_raw = request.body
        if isinstance(body_raw, bytes):
            body = json.loads(body_raw.decode("utf-8"))
        else:
            body = json.loads(body_raw or "{}")
        assert body == {"text": "Hello World"}
        return (
            200,
            {"Content-Type": "application/json"},
            json.dumps({"status": "ok", "id": "id-1", "created": 123}),
        )

    responses.add_callback(
        responses.POST,
        "https://example.com/",
        callback=callback,
        content_type="application/json",
    )

    resp = client.send_message(text="Hello World")
    assert resp.status == "ok"
    assert resp.id == "id-1"
    assert resp.created == 123


@responses.activate
def test_send_message_layout_flagship() -> None:
    client = ReadWriteClient(api_key="k", base_url="https://example.com")
    layout = [[0 for _ in range(22)] for _ in range(6)]

    def callback(request: requests.PreparedRequest) -> tuple[int, dict[str, str], str]:
        body_raw = request.body
        if isinstance(body_raw, bytes):
            parsed: Any = json.loads(body_raw.decode("utf-8"))
        else:
            parsed = json.loads(body_raw or "[]")

        assert isinstance(parsed, list)
        assert len(parsed) == 6
        assert all(isinstance(row, list) and len(row) == 22 for row in parsed)
        return (
            200,
            {"Content-Type": "application/json"},
            json.dumps({"status": "ok", "id": "id-2", "created": 456}),
        )

    responses.add_callback(
        responses.POST,
        "https://example.com/",
        callback=callback,
        content_type="application/json",
    )

    resp = client.send_message(layout=layout)
    assert resp.id == "id-2"


def test_send_message_requires_exactly_one_input() -> None:
    client = ReadWriteClient(api_key="k", base_url="https://example.com")
    with pytest.raises(ValidationError):
        client.send_message()
    with pytest.raises(ValidationError):
        layout = [[0 for _ in range(22)] for _ in range(6)]
        client.send_message(text="hi", layout=layout)


def test_send_message_rejects_blank_text() -> None:
    client = ReadWriteClient(api_key="k", base_url="https://example.com")
    with pytest.raises(ValidationError):
        client.send_message(text="   ")


def test_send_message_rejects_invalid_layout_dimensions() -> None:
    client = ReadWriteClient(api_key="k", base_url="https://example.com")
    with pytest.raises(ValidationError):
        client.send_message(layout=[[0]])


def test_send_message_rejects_non_int_layout_values() -> None:
    client = ReadWriteClient(api_key="k", base_url="https://example.com")
    layout: list[list[Any]] = [[0 for _ in range(22)] for _ in range(6)]
    layout[0][0] = "x"
    with pytest.raises(ValidationError):
        client.send_message(layout=layout)


@responses.activate
def test_send_message_unexpected_payload_raises() -> None:
    client = ReadWriteClient(api_key="k", base_url="https://example.com")
    responses.add(
        responses.POST,
        "https://example.com/",
        body="not-json",
        status=200,
        content_type="text/plain",
    )
    with pytest.raises(ApiError):
        client.send_message(text="Hello")
