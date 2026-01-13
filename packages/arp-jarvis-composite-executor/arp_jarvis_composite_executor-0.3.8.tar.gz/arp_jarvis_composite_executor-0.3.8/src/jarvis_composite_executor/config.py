from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class CompositeConfig:
    max_steps_default: int | None
    max_depth_default: int | None
    poll_timeout_sec: float
    poll_interval_sec: float
    arggen_max_retries: int
    context_window: int | None
    max_concurrency: int | None


def load_composite_config_from_env() -> CompositeConfig:
    return CompositeConfig(
        max_steps_default=_env_int_optional("JARVIS_COMPOSITE_MAX_STEPS"),
        max_depth_default=_env_int_optional("JARVIS_COMPOSITE_MAX_DEPTH"),
        poll_timeout_sec=_env_float("JARVIS_COMPOSITE_POLL_TIMEOUT_SEC", default=30.0),
        poll_interval_sec=_env_float("JARVIS_COMPOSITE_POLL_INTERVAL_SEC", default=1.0),
        arggen_max_retries=_env_int("JARVIS_COMPOSITE_ARGGEN_MAX_RETRIES", default=1),
        context_window=_env_int_optional("JARVIS_COMPOSITE_CONTEXT_WINDOW"),
        max_concurrency=_env_int_optional("JARVIS_MAX_CONCURRENCY"),
    )


def _env_float(name: str, *, default: float) -> float:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a number") from exc


def _env_int(name: str, *, default: int) -> int:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


def _env_int_optional(name: str) -> int | None:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
