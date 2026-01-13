from __future__ import annotations

from typing import Any

PLANNER_SYSTEM_PROMPT = (
    "You are a task planner. You decompose a goal into a small list of ordered subtasks. "
    "You will be given a JSON input with fields: task.goal, task.context, limits.max_steps, limits.depth, limits.max_depth. "
    "Your job is to output up to limits.max_steps subtasks that, when executed in order, fully achieve task.goal. "
    "Do NOT omit required work. If the goal needs more than max_steps actions at this level, create coarser subtasks that bundle work. "
    "Use depth/max_depth: if limits.depth < limits.max_depth - 1, subtasks may be higher-level bundles that will be decomposed later; "
    "When the goal contains multiple independent items, prefer subtasks that each handle one item end-to-end to minimize cross-subtask dependencies. "
    "Minimize dependencies between subtasks when feasible. If a later subtask must reuse an earlier result, say exactly what to reuse. "
    "Make subtasks explicit and self-contained (include key parameters like specific URLs or items; avoid vague references like 'the above'). "
    "Avoid duplicates and ensure coverage. "
    "Return only JSON that matches the response schema. "
)

ARGGEN_SYSTEM_PROMPT = (
    "You generate inputs for a selected action. "
    "You will be given JSON with: subtask.goal, selected_action (node_type_id, version, description), and context (including previous_steps outputs). "
    "Return ONLY a JSON object that matches the provided schema exactly. "
    "When reusing values from context.previous_steps, copy them exactly."
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
                    "subtask_id": {"type": ["string", "null"]},
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
