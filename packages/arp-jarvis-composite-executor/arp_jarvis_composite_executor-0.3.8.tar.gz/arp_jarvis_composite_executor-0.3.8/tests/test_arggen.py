import asyncio

from arp_llm.providers.dev_mock import DevMockChatFixture, DevMockChatModel
from arp_standard_model import NodeKind, NodeType
from jarvis_composite_executor.engine.arggen import ArgGen


def test_arggen_keeps_nulls_and_validates() -> None:
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
            "additionalProperties": False,
            "properties": {
                "text": {"type": "string"},
                "extra": {"type": ["string", "null"]},
            },
            "required": ["text", "extra"],
        },
    )

    result = asyncio.run(
        arggen.generate_inputs(
            subtask_goal="echo this",
            node_type=node_type,
            context={"root_goal": "echo this"},
        )
    )

    assert result.inputs == {"text": "hello", "extra": None}


def test_arggen_accepts_structured_object_output() -> None:
    fixture = DevMockChatFixture(text="arggen", parsed={"uuid4": "1950631f-c549-4cfd-916c-750d4584783b"})
    llm = DevMockChatModel(fixtures=[fixture])
    arggen = ArgGen(llm, max_retries=0)

    node_type = NodeType(
        node_type_id="jarvis.core.echo",
        version="0.3.7",
        kind=NodeKind.atomic,
        description="Echo inputs",
        input_schema={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "uuid4": {"type": "string"},
            },
            "required": ["uuid4"],
        },
    )

    result = asyncio.run(
        arggen.generate_inputs(
            subtask_goal="Return the generated UUID",
            node_type=node_type,
            context={
                "root_goal": "Generate a UUID, then return it.",
                "previous_steps": [{"outputs": {"uuid4": "1950631f-c549-4cfd-916c-750d4584783b"}}],
            },
        )
    )

    assert result.inputs == {"uuid4": "1950631f-c549-4cfd-916c-750d4584783b"}
