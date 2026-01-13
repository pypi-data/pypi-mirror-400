from __future__ import annotations

import pytest
from arp_standard_model import NodeTypeRef

from jarvis_composite_executor import schema_utils


def test_normalize_schema_requires_all_properties() -> None:
    schema = {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "limit": {"type": "integer"},
        },
        "required": ["text"],
        "additionalProperties": False,
    }

    normalized = schema_utils.normalize_schema_for_llm(schema)

    assert sorted(normalized["required"]) == ["limit", "text"]
    assert normalized["properties"]["limit"]["type"] == ["integer", "null"]
    assert normalized["properties"]["text"]["type"] == "string"


def test_normalize_schema_handles_anyof() -> None:
    schema = {
        "anyOf": [
            {"type": "string"},
            {
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
            },
        ]
    }

    normalized = schema_utils.normalize_schema_for_llm(schema)

    assert isinstance(normalized["anyOf"], list)
    assert normalized["anyOf"][1]["properties"]["value"]["type"] == "string"


def test_optional_anyof_allows_null() -> None:
    schema = {
        "type": "object",
        "properties": {
            "maybe": {"anyOf": [{"type": "string"}]},
        },
        "required": [],
    }

    normalized = schema_utils.normalize_schema_for_llm(schema)

    any_of = normalized["properties"]["maybe"]["anyOf"]
    assert {"type": "null"} in any_of


def test_normalize_schema_handles_oneof_and_arrays() -> None:
    schema = {
        "oneOf": [
            {"type": "string"},
            {"type": "array", "items": {"type": "integer"}},
        ]
    }

    normalized = schema_utils.normalize_schema_for_llm(schema)

    assert normalized["oneOf"][1]["items"]["type"] == "integer"


def test_optional_type_list_allows_null() -> None:
    schema = {
        "type": "object",
        "properties": {"maybe": {"type": ["string", "number"]}},
        "required": [],
    }

    normalized = schema_utils.normalize_schema_for_llm(schema)

    assert "null" in normalized["properties"]["maybe"]["type"]


def test_optional_empty_schema_adds_anyof_null() -> None:
    schema = {
        "type": "object",
        "properties": {"maybe": {}},
        "required": [],
    }

    normalized = schema_utils.normalize_schema_for_llm(schema)

    assert normalized["properties"]["maybe"]["anyOf"][1] == {"type": "null"}


def test_validate_json_schema() -> None:
    schema = {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
    schema_utils.validate_json_schema({"text": "ok"}, schema)
    with pytest.raises(Exception):
        schema_utils.validate_json_schema({"text": 123}, schema)


def test_as_dict_model_dump() -> None:
    ref = NodeTypeRef(node_type_id="node", version="1")
    assert schema_utils._as_dict(ref) == {"node_type_id": "node", "version": "1"}
