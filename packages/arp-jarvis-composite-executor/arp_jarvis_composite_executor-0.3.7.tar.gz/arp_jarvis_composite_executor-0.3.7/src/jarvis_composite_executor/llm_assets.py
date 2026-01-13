from __future__ import annotations

from typing import Any

PLANNER_SYSTEM_PROMPT = (
    "You are a planner that decomposes a composite task into bounded subtasks. "
    "Return a list of subtasks only. Do not select node types or tools. "
    "Prefer fewer steps and keep goals concise."
)

ARGGEN_SYSTEM_PROMPT = (
    "You are an input generator. Return ONLY a JSON object that matches the provided schema. "
    "No prose. Follow the schema strictly."
)

PLANNER_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "subtasks": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "subtask_id": {"type": "string"},
                    "goal": {"type": "string"},
                    "notes": {"type": ["string", "null"]},
                },
                "required": ["subtask_id", "goal", "notes"],
            },
        },
        "summary": {"type": ["string", "null"]},
    },
    "required": ["subtasks", "summary"],
}
