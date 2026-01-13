from __future__ import annotations

import asyncio

import pytest
from arp_llm.types import ChatModel, Response
from arp_standard_server import ArpServerError

from jarvis_composite_executor.engine.planner import Planner


class FakeChatModel(ChatModel):
    def __init__(self, parsed) -> None:
        self._parsed = parsed

    async def response(self, messages, *, response_schema=None, temperature=None, timeout_seconds=None, metadata=None) -> Response:
        _ = messages, response_schema, temperature, timeout_seconds, metadata
        return Response(
            text="fake",
            parsed=self._parsed,
            usage=None,
            provider="fake",
            model="fake",
            request_id=None,
            latency_ms=1,
        )


def test_planner_invalid_limits() -> None:
    planner = Planner(FakeChatModel(parsed={"subtasks": [], "summary": None}))
    with pytest.raises(ArpServerError):
        asyncio.run(planner.plan(goal="g", context={}, max_steps=0, depth=0, max_depth=1))


def test_planner_depth_exceeded() -> None:
    planner = Planner(FakeChatModel(parsed={"subtasks": [], "summary": None}))
    with pytest.raises(ArpServerError):
        asyncio.run(planner.plan(goal="g", context={}, max_steps=1, depth=2, max_depth=2))


def test_planner_invalid_output() -> None:
    planner = Planner(FakeChatModel(parsed={"summary": None}))
    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(planner.plan(goal="g", context={}, max_steps=1, depth=0, max_depth=2))
    assert excinfo.value.code == "planner_invalid_output"


def test_planner_invalid_subtask() -> None:
    planner = Planner(FakeChatModel(parsed={"subtasks": [{"goal": ""}], "summary": None}))
    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(planner.plan(goal="g", context={}, max_steps=1, depth=0, max_depth=2))
    assert excinfo.value.code == "planner_invalid_subtask"


def test_planner_duplicate_subtask_id_is_ignored() -> None:
    planner = Planner(
        FakeChatModel(
            parsed={
                "subtasks": [
                    {"subtask_id": "dup", "goal": "a", "notes": None},
                    {"subtask_id": "dup", "goal": "b", "notes": None},
                ],
                "summary": None,
            }
        )
    )
    result = asyncio.run(planner.plan(goal="g", context={}, max_steps=5, depth=0, max_depth=2))
    assert [subtask.subtask_id for subtask in result.subtasks] == ["S1", "S2"]
