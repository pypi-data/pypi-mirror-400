from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from arp_llm.errors import LlmError
from arp_llm.types import ChatModel, Message
from arp_standard_server import ArpServerError

from ..llm_assets import PLANNER_RESPONSE_SCHEMA, PLANNER_SYSTEM_PROMPT
from ..schema_utils import find_openai_strict_schema_issues

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PlannedSubtask:
    subtask_id: str
    goal: str
    notes: str | None


@dataclass(frozen=True)
class PlannerResult:
    subtasks: list[PlannedSubtask]
    summary: str | None
    provider: str
    model: str
    latency_ms: int
    usage: dict[str, Any] | None


class Planner:
    def __init__(self, llm: ChatModel) -> None:
        self._llm = llm

    async def plan(
        self,
        *,
        goal: str,
        context: dict[str, Any],
        max_steps: int,
        depth: int,
        max_depth: int,
    ) -> PlannerResult:
        if max_steps < 1:
            raise ArpServerError(
                code="planner_invalid_max_steps",
                message="max_steps must be >= 1 for planning",
                status_code=400,
                details={"max_steps": max_steps},
            )
        if max_depth < 0:
            raise ArpServerError(
                code="planner_invalid_max_depth",
                message="max_depth must be >= 0 for planning",
                status_code=400,
                details={"max_depth": max_depth},
            )
        if depth >= max_depth:
            raise ArpServerError(
                code="planner_depth_exceeded",
                message="Composite depth exceeds max_depth",
                status_code=400,
                details={"depth": depth, "max_depth": max_depth},
            )

        context_payload: dict[str, Any] = dict(context)
        context_payload.pop("run_context", None)

        payload: dict[str, Any] = {
            "task": {
                "goal": goal,
                "context": context_payload,
            },
            "limits": {
                "max_steps": max_steps,
                "depth": depth,
                "max_depth": max_depth,
            },
        }
        messages = [
            Message.system(PLANNER_SYSTEM_PROMPT),
            Message.user(json.dumps(payload, sort_keys=True)),
        ]

        schema_issues = find_openai_strict_schema_issues(PLANNER_RESPONSE_SCHEMA, limit=5)
        if schema_issues:
            logger.warning("Planner response schema is not OpenAI-strict (issues=%s)", schema_issues)
        logger.info(
            "Planner LLM request (goal_len=%s, max_steps=%s, depth=%s/%s, schema_issues=%s)",
            len(goal),
            max_steps,
            depth,
            max_depth,
            len(schema_issues),
        )
        response = await self._llm.response(messages, response_schema=PLANNER_RESPONSE_SCHEMA)
        if response.parsed is None:
            raise LlmError(code="parse_error", message="Planner response missing parsed output")
        parsed = response.parsed

        raw_subtasks = parsed.get("subtasks")
        if not isinstance(raw_subtasks, list):
            raise ArpServerError(
                code="planner_invalid_output",
                message="Planner response missing subtasks array",
                status_code=502,
            )

        subtasks = self._normalize_subtasks(raw_subtasks, max_steps=max_steps)
        summary = parsed.get("summary")
        summary_value = summary if isinstance(summary, str) else None

        return PlannerResult(
            subtasks=subtasks,
            summary=summary_value,
            provider=response.provider,
            model=response.model,
            latency_ms=response.latency_ms,
            usage=response.usage,
        )

    def _normalize_subtasks(
        self, raw_subtasks: list[Any], *, max_steps: int
    ) -> list[PlannedSubtask]:
        normalized: list[PlannedSubtask] = []
        for index, item in enumerate(raw_subtasks):
            if len(normalized) >= max_steps:
                break
            if not isinstance(item, dict):
                raise ArpServerError(
                    code="planner_invalid_subtask",
                    message="Planner subtask must be an object",
                    status_code=502,
                    details={"index": index},
                )
            goal = item.get("goal")
            notes = item.get("notes")
            if not isinstance(goal, str) or not goal.strip():
                raise ArpServerError(
                    code="planner_invalid_subtask",
                    message="Planner subtask goal must be a non-empty string",
                    status_code=502,
                    details={"index": index},
                )
            subtask_id = f"S{len(normalized) + 1}"
            note_value = notes if isinstance(notes, str) else None
            normalized.append(PlannedSubtask(subtask_id=subtask_id, goal=goal, notes=note_value))

        return normalized
