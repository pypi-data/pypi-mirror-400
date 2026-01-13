import asyncio

from arp_llm.providers.dev_mock import DevMockChatFixture, DevMockChatModel
from arp_standard_model import NodeKind, NodeType
from jarvis_composite_executor.engine.arggen import ArgGen


def test_arggen_strips_nulls_and_validates() -> None:
    fixture = DevMockChatFixture(text="arggen", parsed={"text": "hello", "extra": None})
    llm = DevMockChatModel(fixtures=[fixture])
    arggen = ArgGen(llm, max_retries=0)

    node_type = NodeType(
        node_type_id="jarvis.core.echo",
        version="0.3.7",
        kind=NodeKind.atomic,
        description="Echo text",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "extra": {"type": "string"},
            },
            "required": ["text"],
            "additionalProperties": False,
        },
    )

    result = asyncio.run(
        arggen.generate_inputs(
            subtask_goal="echo this",
            node_type=node_type,
            context={"root_goal": "echo this"},
        )
    )

    assert result.inputs == {"text": "hello"}
