from __future__ import annotations

import copy
from typing import Any, Mapping


def normalize_schema_for_llm(schema: Mapping[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(dict(schema))
    return _normalize_schema(normalized)


def validate_json_schema(instance: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    import jsonschema

    jsonschema.validate(instance=instance, schema=dict(schema))


def _normalize_schema(schema: dict[str, Any]) -> dict[str, Any]:
    if "anyOf" in schema and isinstance(schema["anyOf"], list):
        schema["anyOf"] = [_normalize_schema(_as_dict(item)) for item in schema["anyOf"]]
        return schema
    if "oneOf" in schema and isinstance(schema["oneOf"], list):
        schema["oneOf"] = [_normalize_schema(_as_dict(item)) for item in schema["oneOf"]]
        return schema

    schema_type = schema.get("type")
    if schema_type == "object":
        properties = schema.get("properties")
        if isinstance(properties, dict):
            original_required = set(schema.get("required") or [])
            required = list(properties.keys())
            schema["required"] = required
            for key, prop_schema in list(properties.items()):
                normalized = _normalize_schema(_as_dict(prop_schema))
                if key not in original_required:
                    normalized = _allow_null(normalized)
                properties[key] = normalized
        return schema

    if schema_type == "array":
        items = schema.get("items")
        if isinstance(items, dict):
            schema["items"] = _normalize_schema(items)
        return schema

    return schema


def _allow_null(schema: dict[str, Any]) -> dict[str, Any]:
    if "type" in schema:
        schema_type = schema["type"]
        if isinstance(schema_type, list):
            if "null" not in schema_type:
                schema["type"] = list(schema_type) + ["null"]
        elif isinstance(schema_type, str):
            if schema_type != "null":
                schema["type"] = [schema_type, "null"]
        return schema

    any_of = schema.get("anyOf")
    if isinstance(any_of, list):
        normalized = [_as_dict(item) for item in any_of]
        if not any(_allows_null(item) for item in normalized):
            normalized.append({"type": "null"})
        schema["anyOf"] = normalized
        return schema

    schema["anyOf"] = [schema, {"type": "null"}]
    return schema


def _allows_null(schema: dict[str, Any]) -> bool:
    schema_type = schema.get("type")
    if schema_type == "null":
        return True
    if isinstance(schema_type, list) and "null" in schema_type:
        return True
    if "anyOf" in schema and isinstance(schema["anyOf"], list):
        return any(_allows_null(_as_dict(item)) for item in schema["anyOf"])
    if "oneOf" in schema and isinstance(schema["oneOf"], list):
        return any(_allows_null(_as_dict(item)) for item in schema["oneOf"])
    return False


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return dict(value.model_dump(exclude_none=True))
    return dict(value)
