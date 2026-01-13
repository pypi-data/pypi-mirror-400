import pytest
import requests
import responses

from vestaboard.base_client import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF_SECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    MAX_RETRIES_ENV_VAR,
    READ_WRITE_API_KEY_ENV_VAR,
    RETRY_BACKOFF_ENV_VAR,
    TIMEOUT_ENV_VAR,
    BaseClient,
)
from vestaboard.exceptions import (
    ApiError,
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


def test_api_key_from_param(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(READ_WRITE_API_KEY_ENV_VAR, raising=False)
    client = BaseClient(api_key="abc", base_url="https://example.com")
    assert client.session.headers["X-Vestaboard-Read-Write-Key"] == "abc"


def test_api_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(READ_WRITE_API_KEY_ENV_VAR, "env-key")
    client = BaseClient(base_url="https://example.com")
    assert client.session.headers["X-Vestaboard-Read-Write-Key"] == "env-key"


def test_missing_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(READ_WRITE_API_KEY_ENV_VAR, raising=False)
    with pytest.raises(AuthenticationError):
        BaseClient(base_url="https://example.com")


def test_env_overrides_timeout_and_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(READ_WRITE_API_KEY_ENV_VAR, "env-key")
    monkeypatch.setenv(TIMEOUT_ENV_VAR, "1.5")
    monkeypatch.setenv(MAX_RETRIES_ENV_VAR, "2")
    monkeypatch.setenv(RETRY_BACKOFF_ENV_VAR, "0.25")

    client = BaseClient(base_url="https://example.com")
    assert client.timeout_seconds == 1.5
    assert client.max_retries == 2
    assert client.retry_backoff_seconds == 0.25


def test_invalid_env_values_fall_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(READ_WRITE_API_KEY_ENV_VAR, "env-key")
    monkeypatch.setenv(TIMEOUT_ENV_VAR, "nope")
    monkeypatch.setenv(MAX_RETRIES_ENV_VAR, "nope")
    monkeypatch.setenv(RETRY_BACKOFF_ENV_VAR, "nope")

    client = BaseClient(base_url="https://example.com")
    assert client.timeout_seconds == DEFAULT_TIMEOUT_SECONDS
    assert client.max_retries == DEFAULT_MAX_RETRIES
    assert client.retry_backoff_seconds == DEFAULT_RETRY_BACKOFF_SECONDS


def test_negative_config_values_are_clamped() -> None:
    client = BaseClient(
        api_key="k",
        base_url="https://example.com/api",
        max_retries=-1,
        timeout_seconds=0.0,
        retry_backoff_seconds=-1.0,
    )
    assert client.max_retries == 0
    assert client.timeout_seconds == DEFAULT_TIMEOUT_SECONDS
    assert client.retry_backoff_seconds == 0.0


def test_context_manager_closes_session() -> None:
    with BaseClient(api_key="k", base_url="https://example.com/api") as client:
        assert client.api_key == "k"


@responses.activate
def test_url_joining_leading_slash() -> None:
    client = BaseClient(api_key="k", base_url="https://example.com/api")
    responses.add(
        responses.GET,
        "https://example.com/api/test",
        json={"ok": True},
        status=200,
    )
    assert client.get("/test") == {"ok": True}


@responses.activate
def test_204_no_content_returns_empty_object() -> None:
    client = BaseClient(api_key="k", base_url="https://example.com/api")
    responses.add(responses.GET, "https://example.com/api/empty", status=204)
    assert client.get("empty") == {}


@responses.activate
def test_invalid_json_falls_back_to_text() -> None:
    client = BaseClient(api_key="k", base_url="https://example.com/api")
    responses.add(
        responses.GET,
        "https://example.com/api/text",
        body="not-json",
        status=200,
        content_type="text/plain",
    )
    assert client.get("text") == "not-json"


@responses.activate
def test_error_message_from_plain_text_body() -> None:
    client = BaseClient(api_key="k", base_url="https://example.com/api", max_retries=0)
    responses.add(
        responses.GET,
        "https://example.com/api/text-error",
        body="plain error message",
        status=418,
        content_type="text/plain",
    )

    with pytest.raises(ApiError) as exc:
        client.get("text-error")
    assert "plain error message" in str(exc.value)


@responses.activate
def test_error_message_from_error_field() -> None:
    client = BaseClient(api_key="k", base_url="https://example.com/api", max_retries=0)
    responses.add(
        responses.GET,
        "https://example.com/api/error-field",
        json={"error": "nope"},
        status=418,
    )

    with pytest.raises(ApiError) as exc:
        client.get("error-field")
    assert "nope" in str(exc.value)


@responses.activate
def test_error_message_defaults_when_no_message_fields() -> None:
    client = BaseClient(api_key="k", base_url="https://example.com/api", max_retries=0)
    responses.add(
        responses.GET,
        "https://example.com/api/no-message",
        json={"foo": "bar"},
        status=418,
    )

    with pytest.raises(ApiError) as exc:
        client.get("no-message")
    assert "Request failed" in str(exc.value)


@responses.activate
def test_error_message_defaults_when_text_body_is_blank() -> None:
    client = BaseClient(api_key="k", base_url="https://example.com/api", max_retries=0)
    responses.add(
        responses.GET,
        "https://example.com/api/blank-text",
        body="   ",
        status=418,
        content_type="text/plain",
    )

    with pytest.raises(ApiError) as exc:
        client.get("blank-text")
    assert "Request failed" in str(exc.value)


@pytest.mark.parametrize(
    ("status", "exc_type"),
    [
        (400, ValidationError),
        (401, AuthenticationError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, ServerError),
        (418, ApiError),
    ],
)
@responses.activate
def test_error_mapping(status: int, exc_type: type[Exception]) -> None:
    client = BaseClient(api_key="k", base_url="https://example.com/api", max_retries=0)
    responses.add(
        responses.GET,
        "https://example.com/api/bad",
        json={"message": "nope"},
        status=status,
    )
    with pytest.raises(exc_type):
        client.get("bad")


@responses.activate
def test_put_patch_delete_wrappers() -> None:
    client = BaseClient(api_key="k", base_url="https://example.com/api", max_retries=0)

    responses.add(
        responses.PUT,
        "https://example.com/api/item",
        json={"ok": "put"},
        status=200,
    )
    responses.add(
        responses.PATCH,
        "https://example.com/api/item",
        json={"ok": "patch"},
        status=200,
    )
    responses.add(
        responses.DELETE,
        "https://example.com/api/item",
        json={"ok": "delete"},
        status=200,
    )

    assert client.put("item", json_data={"a": 1}) == {"ok": "put"}
    assert client.patch("item", json_data={"b": 2}) == {"ok": "patch"}
    assert client.delete("item") == {"ok": "delete"}


@responses.activate
def test_retries_on_retryable_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    client = BaseClient(
        api_key="k",
        base_url="https://example.com/api",
        max_retries=1,
        retry_backoff_seconds=0.0,
    )
    responses.add(
        responses.GET,
        "https://example.com/api/retry",
        json={"error": "server"},
        status=500,
    )
    responses.add(
        responses.GET,
        "https://example.com/api/retry",
        json={"ok": True},
        status=200,
    )

    assert client.get("retry") == {"ok": True}
    assert len(responses.calls) == 2


def test_retries_on_request_exception_then_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    client = BaseClient(
        api_key="k",
        base_url="https://example.com/api",
        max_retries=1,
        retry_backoff_seconds=0.0,
    )

    resp = requests.Response()
    resp.status_code = 200
    resp._content = b'{"ok": true}'  # type: ignore[attr-defined]

    calls = {"n": 0}

    def flaky_request(*args: object, **kwargs: object) -> requests.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            raise requests.exceptions.RequestException("boom")
        return resp

    monkeypatch.setattr(client.session, "request", flaky_request)
    assert client.get("x") == {"ok": True}
    assert calls["n"] == 2


def test_network_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    client = BaseClient(
        api_key="k",
        base_url="https://example.com/api",
        max_retries=0,
    )

    def boom(*args: object, **kwargs: object) -> object:
        raise requests.exceptions.RequestException("boom")

    monkeypatch.setattr(client.session, "request", boom)
    with pytest.raises(NetworkError):
        client.get("x")


def test_multipart_request_does_not_force_json_content_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = BaseClient(api_key="k", base_url="https://example.com/api", max_retries=0)

    resp = requests.Response()
    resp.status_code = 200
    resp._content = b'{"ok": true}'  # type: ignore[attr-defined]

    def fake_request(**kwargs: object) -> requests.Response:
        headers = kwargs.get("headers")
        assert isinstance(headers, dict)
        assert "Content-Type" not in headers
        assert kwargs.get("files") is not None
        return resp

    monkeypatch.setattr(client.session, "request", fake_request)

    result = client.post(
        "upload",
        data={"a": "1"},
        files={"file": ("name.txt", b"hello")},
    )
    assert result == {"ok": True}


@responses.activate
def test_retry_exhaustion_raises_server_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    client = BaseClient(
        api_key="k",
        base_url="https://example.com/api",
        max_retries=1,
        retry_backoff_seconds=0.0,
    )
    responses.add(
        responses.GET,
        "https://example.com/api/always500",
        json={"error": "server"},
        status=500,
    )
    responses.add(
        responses.GET,
        "https://example.com/api/always500",
        json={"error": "server"},
        status=500,
    )

    with pytest.raises(ServerError):
        client.get("always500")
    assert len(responses.calls) == 2


# End of file
