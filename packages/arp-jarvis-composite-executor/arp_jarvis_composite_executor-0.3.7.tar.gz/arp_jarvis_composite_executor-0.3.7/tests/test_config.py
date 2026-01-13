import pytest

from jarvis_composite_executor.config import load_composite_config_from_env


def test_load_composite_config_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JARVIS_COMPOSITE_MAX_STEPS", raising=False)
    monkeypatch.delenv("JARVIS_COMPOSITE_MAX_DEPTH", raising=False)
    monkeypatch.delenv("JARVIS_COMPOSITE_POLL_TIMEOUT_SEC", raising=False)
    monkeypatch.delenv("JARVIS_COMPOSITE_POLL_INTERVAL_SEC", raising=False)
    monkeypatch.delenv("JARVIS_COMPOSITE_ARGGEN_MAX_RETRIES", raising=False)
    monkeypatch.delenv("JARVIS_COMPOSITE_CONTEXT_WINDOW", raising=False)
    monkeypatch.delenv("JARVIS_MAX_CONCURRENCY", raising=False)

    config = load_composite_config_from_env()

    assert config.poll_timeout_sec == 30.0
    assert config.poll_interval_sec == 1.0
    assert config.arggen_max_retries == 1
    assert config.max_steps_default is None
    assert config.max_depth_default is None


def test_load_composite_config_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JARVIS_COMPOSITE_MAX_STEPS", "6")
    monkeypatch.setenv("JARVIS_COMPOSITE_MAX_DEPTH", "3")
    monkeypatch.setenv("JARVIS_COMPOSITE_POLL_TIMEOUT_SEC", "12.5")
    monkeypatch.setenv("JARVIS_COMPOSITE_POLL_INTERVAL_SEC", "0.2")
    monkeypatch.setenv("JARVIS_COMPOSITE_ARGGEN_MAX_RETRIES", "2")
    monkeypatch.setenv("JARVIS_COMPOSITE_CONTEXT_WINDOW", "5")
    monkeypatch.setenv("JARVIS_MAX_CONCURRENCY", "10")

    config = load_composite_config_from_env()

    assert config.max_steps_default == 6
    assert config.max_depth_default == 3
    assert config.poll_timeout_sec == 12.5
    assert config.poll_interval_sec == 0.2
    assert config.arggen_max_retries == 2
    assert config.context_window == 5
    assert config.max_concurrency == 10


def test_load_composite_config_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JARVIS_COMPOSITE_POLL_TIMEOUT_SEC", "oops")
    with pytest.raises(RuntimeError):
        load_composite_config_from_env()


def test_load_composite_config_invalid_ints(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JARVIS_COMPOSITE_ARGGEN_MAX_RETRIES", "nope")
    with pytest.raises(RuntimeError):
        load_composite_config_from_env()

    monkeypatch.setenv("JARVIS_COMPOSITE_MAX_STEPS", "bad")
    with pytest.raises(RuntimeError):
        load_composite_config_from_env()
