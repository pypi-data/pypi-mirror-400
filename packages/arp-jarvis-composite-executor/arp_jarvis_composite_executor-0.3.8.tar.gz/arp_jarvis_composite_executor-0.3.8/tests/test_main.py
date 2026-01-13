from __future__ import annotations

import importlib
import runpy
import sys

from jarvis_composite_executor import __main__ as main_module


def test_main_reload(monkeypatch) -> None:
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fake_run(*args, **kwargs) -> None:
        calls.append((args, kwargs))

    monkeypatch.setattr(main_module.uvicorn, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["prog", "--reload", "--host", "0.0.0.0", "--port", "9000"])

    main_module.main()

    assert calls
    args, kwargs = calls[0]
    assert args[0] == "jarvis_composite_executor.app:app"
    assert kwargs["host"] == "0.0.0.0"
    assert kwargs["port"] == 9000
    assert kwargs["reload"] is True


def test_main_no_reload(monkeypatch) -> None:
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fake_run(*args, **kwargs) -> None:
        calls.append((args, kwargs))

    monkeypatch.setattr(main_module.uvicorn, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["prog", "--host", "127.0.0.1", "--port", "9001"])
    monkeypatch.setenv("JARVIS_SELECTION_URL", "http://selection.local")
    monkeypatch.setenv("JARVIS_NODE_REGISTRY_URL", "http://registry.local")
    monkeypatch.setenv("ARP_AUTH_CLIENT_ID", "id")
    monkeypatch.setenv("ARP_AUTH_CLIENT_SECRET", "secret")
    monkeypatch.setenv("ARP_AUTH_TOKEN_ENDPOINT", "http://auth.local/token")
    monkeypatch.setenv("ARP_AUTH_MODE", "disabled")
    monkeypatch.setenv("ARP_LLM_PROFILE", "openai")
    monkeypatch.setenv("ARP_LLM_CHAT_MODEL", "gpt-4.1-mini")
    monkeypatch.setenv("ARP_LLM_API_KEY", "test")

    import jarvis_composite_executor.app as app_module

    importlib.reload(app_module)
    monkeypatch.setattr(app_module, "create_app", lambda: "app")

    main_module.main()

    args, kwargs = calls[0]
    assert args[0] == "app"
    assert kwargs["host"] == "127.0.0.1"
    assert kwargs["port"] == 9001
    assert kwargs["reload"] is False


def test_main_module_guard(monkeypatch) -> None:
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fake_run(*args, **kwargs) -> None:
        calls.append((args, kwargs))

    monkeypatch.setattr(main_module.uvicorn, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["prog", "--reload"])

    runpy.run_module("jarvis_composite_executor.__main__", run_name="__main__")

    assert calls
