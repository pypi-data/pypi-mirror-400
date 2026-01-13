from __future__ import annotations

import copy
from typing import Any, Mapping


def normalize_schema_for_llm(schema: Mapping[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(dict(schema))
    return _normalize_schema(normalized)


def find_openai_strict_schema_issues(schema: Mapping[str, Any], *, limit: int = 25) -> list[dict[str, Any]]:
    """
    Best-effort validator for OpenAI "strict" structured output schemas.

    OpenAI requires every object schema to explicitly set `"additionalProperties": false`, and
    for `"required"` to contain all keys in `"properties"` (nullable types are used to represent
    optionality).

    Returns a bounded list of issues suitable for logging.
    """

    issues: list[dict[str, Any]] = []

    def visit(value: Any, path: list[Any]) -> None:
        if len(issues) >= limit:
            return
        if isinstance(value, dict):
            schema_type = value.get("type")
            is_object = schema_type == "object" or (isinstance(schema_type, list) and "object" in schema_type)

            if is_object:
                ap = value.get("additionalProperties", None)
                if ap is not False:
                    issues.append(
                        {
                            "path": _format_schema_path(path),
                            "issue": "additionalProperties_must_be_false",
                            "value": ap,
                        }
                    )
                    if len(issues) >= limit:
                        return

                props = value.get("properties")
                if props is None or not isinstance(props, dict):
                    issues.append(
                        {
                            "path": _format_schema_path(path + ["properties"]),
                            "issue": "properties_must_be_object",
                            "value": None if props is None else type(props).__name__,
                        }
                    )
                    if len(issues) >= limit:
                        return
                    props = {}

                req = value.get("required")
                if req is None or not isinstance(req, list):
                    issues.append(
                        {
                            "path": _format_schema_path(path + ["required"]),
                            "issue": "required_must_be_array",
                            "value": None if req is None else type(req).__name__,
                        }
                    )
                    if len(issues) >= limit:
                        return
                    req = []

                missing = [key for key in props.keys() if key not in req]
                if missing:
                    issues.append(
                        {
                            "path": _format_schema_path(path + ["required"]),
                            "issue": "required_must_include_all_properties",
                            "value": missing,
                        }
                    )
                    if len(issues) >= limit:
                        return

            for key, item in value.items():
                if key in ("$defs", "definitions") and isinstance(item, dict):
                    for def_name, def_schema in item.items():
                        visit(def_schema, path + [key, def_name])
                    continue
                if key in ("anyOf", "oneOf", "allOf") and isinstance(item, list):
                    for idx, branch in enumerate(item):
                        visit(branch, path + [key, idx])
                    continue
                if key == "properties" and isinstance(item, dict):
                    for prop_name, prop_schema in item.items():
                        visit(prop_schema, path + [key, prop_name])
                    continue
                if key == "items":
                    visit(item, path + [key])
                    continue
        elif isinstance(value, list):
            for idx, item in enumerate(value):
                visit(item, path + [idx])

    visit(dict(schema), [])
    return issues


def _format_schema_path(path: list[Any]) -> str:
    if not path:
        return "$"
    parts: list[str] = ["$"]
    for item in path:
        if isinstance(item, int):
            parts.append(f"[{item}]")
        else:
            parts.append(f".{item}")
    return "".join(parts)


def validate_json_schema(instance: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    import jsonschema

    jsonschema.validate(instance=instance, schema=dict(schema))


def _normalize_schema(schema: dict[str, Any]) -> dict[str, Any]:
    if "anyOf" in schema and isinstance(schema["anyOf"], list):
        schema["anyOf"] = [_normalize_schema(_as_dict(item)) for item in schema["anyOf"]]
    if "oneOf" in schema and isinstance(schema["oneOf"], list):
        schema["oneOf"] = [_normalize_schema(_as_dict(item)) for item in schema["oneOf"]]

    schema_type = schema.get("type")
    if schema_type == "object":
        properties = schema.get("properties")
        if not isinstance(properties, dict):
            schema["properties"] = {}
            schema["required"] = []
            schema["additionalProperties"] = False
            return schema

        original_required = set(schema.get("required") or [])
        required = list(properties.keys())
        schema["required"] = required
        schema["additionalProperties"] = False
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
