import pytest

from vestaboard.models import (
    CurrentMessage,
    CurrentMessageResponse,
    SendMessageResponse,
    coerce_layout,
)


def test_current_message_layout_as_list_parses_json_string() -> None:
    msg = CurrentMessage(layout="[[0, 1], [2, 3]]", id="m1")
    assert msg.layout_as_list() == [[0, 1], [2, 3]]


@pytest.mark.parametrize(
    "layout",
    [
        '"not a list"',
        "[1, 2, 3]",
        '[[0, "x"]]',
    ],
)
def test_current_message_layout_as_list_validates_shape(layout: str) -> None:
    msg = CurrentMessage(layout=layout, id="m1")
    with pytest.raises(ValueError):
        msg.layout_as_list()


def test_current_message_response_from_dict_validates_types() -> None:
    with pytest.raises(TypeError):
        CurrentMessageResponse.from_dict({"currentMessage": "nope"})

    with pytest.raises(TypeError):
        CurrentMessageResponse.from_dict({"currentMessage": {"layout": 123, "id": "x"}})

    with pytest.raises(TypeError):
        CurrentMessageResponse.from_dict(
            {"currentMessage": {"layout": "[[0]]", "id": 1}}
        )


def test_send_message_response_from_dict_validates_types() -> None:
    with pytest.raises(TypeError):
        SendMessageResponse.from_dict({"status": 1, "id": "x", "created": 1})
    with pytest.raises(TypeError):
        SendMessageResponse.from_dict({"status": "ok", "id": 1, "created": 1})
    with pytest.raises(TypeError):
        SendMessageResponse.from_dict({"status": "ok", "id": "x", "created": "nope"})


@pytest.mark.parametrize(
    "layout",
    [
        [],
        [[]],
        [[0], [0, 0]],
    ],
)
def test_coerce_layout_validates(layout: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        coerce_layout(layout)  # type: ignore[arg-type]
