import builtins
import sys
import types

import pytest

from vestaboard.client import VestaboardClient
from vestaboard.read_write import ReadWriteClient


def test_facade_lazy_loads_and_caches_subclient() -> None:
    client = VestaboardClient(api_key="k", base_url="https://example.com")
    assert client._read_write is None

    rw1 = client.read_write
    assert isinstance(rw1, ReadWriteClient)
    assert client._read_write is rw1

    rw2 = client.read_write
    assert rw2 is rw1


def test_facade_propagates_config_to_subclient() -> None:
    client = VestaboardClient(
        api_key="k",
        base_url="https://example.com",
        timeout_seconds=3.0,
        max_retries=1,
        retry_backoff_seconds=0.0,
    )
    rw = client.read_write
    assert rw.base_url == "https://example.com"
    assert rw.timeout_seconds == 3.0
    assert rw.max_retries == 1
    assert rw.retry_backoff_seconds == 0.0


def test_rw_alias_returns_same_subclient() -> None:
    client = VestaboardClient(api_key="k", base_url="https://example.com")
    assert client.rw is client.read_write


def test_load_dotenv_raises_helpful_error_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def fake_import(
        name: str,
        globals: object = None,
        locals: object = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> object:
        if name == "dotenv":
            raise ImportError("nope")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ImportError) as exc:
        VestaboardClient(load_dotenv=True)
    assert "python-dotenv" in str(exc.value)


def test_load_dotenv_calls_load_function(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[bool] = []
    dummy = types.ModuleType("dotenv")

    def _load() -> None:
        called.append(True)

    dummy.load_dotenv = _load  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "dotenv", dummy)

    VestaboardClient(load_dotenv=True)
    assert called == [True]
