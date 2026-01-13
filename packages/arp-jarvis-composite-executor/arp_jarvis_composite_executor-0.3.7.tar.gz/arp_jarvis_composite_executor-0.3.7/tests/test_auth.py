import asyncio
import os
from typing import cast

import pytest
from arp_auth import AuthClient, AuthError
from arp_standard_server import ArpServerError

from jarvis_composite_executor import auth


class FakeToken:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token


class FakeAuthClient:
    def __init__(self, token: str = "token") -> None:
        self._token = token

    def client_credentials(self, *, audience: str | None = None, scope: str | None = None) -> FakeToken:
        _ = audience, scope
        return FakeToken(self._token)


class FakeAuthClientError(FakeAuthClient):
    def client_credentials(self, *, audience: str | None = None, scope: str | None = None) -> FakeToken:
        raise RuntimeError("boom")


def _clear_auth_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in list(os.environ):
        if key.startswith("ARP_AUTH_"):
            monkeypatch.delenv(key, raising=False)


def test_auth_settings_default(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_auth_env(monkeypatch)

    settings = auth.auth_settings_from_env_or_dev_secure()

    assert settings.mode == "required"
    assert settings.issuer == auth.DEFAULT_DEV_KEYCLOAK_ISSUER


def test_auth_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = object()

    monkeypatch.setenv("ARP_AUTH_MODE", "required")
    monkeypatch.setattr(auth.AuthSettings, "from_env", classmethod(lambda cls: sentinel))

    assert auth.auth_settings_from_env_or_dev_secure() is sentinel


def test_auth_client_optional_none(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_auth_env(monkeypatch)
    assert auth.auth_client_from_env_optional() is None


def test_auth_client_optional_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_AUTH_CLIENT_ID", "id")
    monkeypatch.delenv("ARP_AUTH_CLIENT_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        auth.auth_client_from_env_optional()


def test_auth_client_optional_success(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = object()
    monkeypatch.setenv("ARP_AUTH_CLIENT_ID", "id")
    monkeypatch.setenv("ARP_AUTH_CLIENT_SECRET", "secret")
    monkeypatch.setattr(auth.AuthClient, "from_env", classmethod(lambda cls: sentinel))

    client = auth.auth_client_from_env_optional()

    assert client is sentinel


def test_auth_client_optional_auth_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARP_AUTH_CLIENT_ID", "id")
    monkeypatch.setenv("ARP_AUTH_CLIENT_SECRET", "secret")

    def raise_auth_error(cls):
        raise AuthError("bad")

    monkeypatch.setattr(auth.AuthClient, "from_env", classmethod(raise_auth_error))

    with pytest.raises(RuntimeError):
        auth.auth_client_from_env_optional()


def test_client_credentials_token_success() -> None:
    client = FakeAuthClient(token="ok")

    result = asyncio.run(
        auth.client_credentials_token(
            auth_client=cast(AuthClient, client),
            audience=None,
            scope=None,
            service_label="svc",
        )
    )

    assert result == "ok"


def test_client_credentials_token_error() -> None:
    client = FakeAuthClientError()

    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(
            auth.client_credentials_token(
                auth_client=cast(AuthClient, client),
                audience=None,
                scope=None,
                service_label="svc",
            )
        )

    assert excinfo.value.code == "token_request_failed"
