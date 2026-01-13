import asyncio

from arp_llm.providers.dev_mock import DevMockChatFixture, DevMockChatModel
from jarvis_composite_executor.engine.planner import Planner


def test_planner_truncates_and_assigns_ids() -> None:
    fixture = DevMockChatFixture(
        text="planner",
        parsed={
            "subtasks": [
                {"subtask_id": "", "goal": "step one", "notes": None},
                {"subtask_id": "step-2", "goal": "step two", "notes": None},
            ],
            "summary": "two steps",
        },
    )
    planner = Planner(DevMockChatModel(fixtures=[fixture]))

    result = asyncio.run(
        planner.plan(
            goal="root goal",
            context={},
            max_steps=1,
            depth=0,
            max_depth=2,
            id_prefix="root",
        )
    )

    assert len(result.subtasks) == 1
    assert result.subtasks[0].subtask_id == "root.0"
