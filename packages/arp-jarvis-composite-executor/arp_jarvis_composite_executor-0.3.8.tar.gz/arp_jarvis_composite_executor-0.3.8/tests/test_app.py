from __future__ import annotations

import importlib

import pytest


def _load_app_module(monkeypatch: pytest.MonkeyPatch):
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

    return importlib.reload(app_module)


def test_require_url_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    app_module = _load_app_module(monkeypatch)
    monkeypatch.delenv("JARVIS_SELECTION_URL", raising=False)
    with pytest.raises(RuntimeError):
        app_module._require_url("JARVIS_SELECTION_URL")


def test_require_url_fallback_and_normalization(monkeypatch: pytest.MonkeyPatch) -> None:
    app_module = _load_app_module(monkeypatch)
    monkeypatch.delenv("JARVIS_SELECTION_URL", raising=False)
    monkeypatch.setenv("ARP_SELECTION_URL", "http://selection.local/v1/")

    value = app_module._require_url("JARVIS_SELECTION_URL", fallback="ARP_SELECTION_URL")

    assert value == "http://selection.local"


def test_audience_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    app_module = _load_app_module(monkeypatch)
    monkeypatch.delenv("JARVIS_SELECTION_AUDIENCE", raising=False)
    assert app_module._audience_from_env("JARVIS_SELECTION_AUDIENCE") is None

    monkeypatch.setenv("JARVIS_SELECTION_AUDIENCE", "audience")
    assert app_module._audience_from_env("JARVIS_SELECTION_AUDIENCE") == "audience"


def test_create_app_wires_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    app_module = _load_app_module(monkeypatch)
    monkeypatch.setenv("JARVIS_SELECTION_URL", "http://selection.local/v1")
    monkeypatch.setenv("JARVIS_NODE_REGISTRY_URL", "http://registry.local/v1/")

    sentinel_auth = object()
    sentinel_llm = object()
    sentinel_settings = object()
    recorded: dict[str, object] = {}

    monkeypatch.setattr(app_module, "auth_client_from_env_optional", lambda: sentinel_auth)
    monkeypatch.setattr(app_module, "load_chat_model_from_env", lambda: sentinel_llm)
    monkeypatch.setattr(app_module, "auth_settings_from_env_or_dev_secure", lambda: sentinel_settings)

    def fake_selection(*, base_url: str, auth_client: object, audience: str | None) -> object:
        recorded["selection"] = (base_url, auth_client, audience)
        return object()

    def fake_registry(*, base_url: str, auth_client: object, audience: str | None) -> object:
        recorded["registry"] = (base_url, auth_client, audience)
        return object()

    def fake_create_app(self, *, title: str, auth_settings: object) -> str:
        recorded["title"] = title
        recorded["auth_settings"] = auth_settings
        return "app"

    monkeypatch.setattr(app_module, "SelectionGatewayClient", fake_selection)
    monkeypatch.setattr(app_module, "NodeRegistryGatewayClient", fake_registry)
    monkeypatch.setattr(app_module.CompositeExecutor, "create_app", fake_create_app)

    app = app_module.create_app()

    assert app == "app"
    assert recorded["selection"] == ("http://selection.local", sentinel_auth, None)
    assert recorded["registry"] == ("http://registry.local", sentinel_auth, None)
    assert recorded["title"] == "JARVIS Composite Executor"
    assert recorded["auth_settings"] is sentinel_settings


def test_create_app_requires_auth_client(monkeypatch: pytest.MonkeyPatch) -> None:
    app_module = _load_app_module(monkeypatch)
    monkeypatch.setattr(app_module, "auth_client_from_env_optional", lambda: None)

    with pytest.raises(RuntimeError):
        app_module.create_app()
