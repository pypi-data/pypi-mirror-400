from __future__ import annotations

import asyncio

import pytest
from arp_llm.errors import LlmError
from arp_llm.types import ChatModel, Response
from arp_standard_model import NodeKind, NodeType
from arp_standard_server import ArpServerError

from jarvis_composite_executor.engine.arggen import ArgGen


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


def test_arggen_missing_schema() -> None:
    arggen = ArgGen(FakeChatModel(parsed={"text": "ok"}), max_retries=0)
    node_type = NodeType(
        node_type_id="node",
        version="1",
        kind=NodeKind.atomic,
        description=None,
        input_schema=None,
    )
    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(arggen.generate_inputs(subtask_goal="goal", node_type=node_type, context={}))
    assert excinfo.value.code == "arggen_schema_missing"


def test_arggen_invalid_schema_type() -> None:
    arggen = ArgGen(FakeChatModel(parsed={"text": "ok"}), max_retries=0)
    node_type = NodeType.model_construct(
        node_type_id="node",
        version="1",
        kind=NodeKind.atomic,
        input_schema=["not", "a", "dict"],
    )
    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(arggen.generate_inputs(subtask_goal="goal", node_type=node_type, context={}))
    assert excinfo.value.code == "arggen_schema_invalid"


def test_arggen_missing_parsed() -> None:
    arggen = ArgGen(FakeChatModel(parsed=None), max_retries=0)
    node_type = NodeType(
        node_type_id="node",
        version="1",
        kind=NodeKind.atomic,
        description=None,
        input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
    )
    with pytest.raises(LlmError):
        asyncio.run(arggen.generate_inputs(subtask_goal="goal", node_type=node_type, context={}))


def test_arggen_parsed_not_object() -> None:
    arggen = ArgGen(FakeChatModel(parsed=["not", "object"]), max_retries=0)
    node_type = NodeType(
        node_type_id="node",
        version="1",
        kind=NodeKind.atomic,
        description=None,
        input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
    )
    with pytest.raises(LlmError):
        asyncio.run(arggen.generate_inputs(subtask_goal="goal", node_type=node_type, context={}))


def test_arggen_validation_failure() -> None:
    arggen = ArgGen(FakeChatModel(parsed={"text": 123}), max_retries=0)
    node_type = NodeType(
        node_type_id="node",
        version="1",
        kind=NodeKind.atomic,
        description=None,
        input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
    )
    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(arggen.generate_inputs(subtask_goal="goal", node_type=node_type, context={}))
    assert excinfo.value.code == "arggen_validation_failed"
