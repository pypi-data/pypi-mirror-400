from __future__ import annotations

from datetime import timezone

from jarvis_composite_executor import utils


def test_now_returns_utc() -> None:
    timestamp = utils.now()
    assert timestamp.tzinfo is not None
    assert timestamp.tzinfo.utcoffset(timestamp) == timezone.utc.utcoffset(timestamp)


def test_normalize_base_url() -> None:
    assert utils.normalize_base_url("http://example.com/") == "http://example.com"
    assert utils.normalize_base_url("http://example.com/v1") == "http://example.com"
    assert utils.normalize_base_url("http://example.com/v1/") == "http://example.com"
