from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from arp_llm.errors import LlmError
from arp_llm.types import ChatModel, Message
from arp_standard_model import NodeType
from arp_standard_server import ArpServerError

from ..llm_assets import ARGGEN_SYSTEM_PROMPT
from ..schema_utils import find_openai_strict_schema_issues, validate_json_schema

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ArgGenResult:
    inputs: dict[str, Any]
    provider: str
    model: str
    latency_ms: int
    usage: dict[str, Any] | None


class ArgGen:
    def __init__(self, llm: ChatModel, *, max_retries: int) -> None:
        self._llm = llm
        self._max_retries = max_retries

    async def generate_inputs(
        self,
        *,
        subtask_goal: str,
        node_type: NodeType,
        context: dict[str, Any],
    ) -> ArgGenResult:
        if node_type.input_schema is None:
            raise ArpServerError(
                code="arggen_schema_missing",
                message="NodeType is missing input_schema required for arg-gen",
                status_code=422,
                details={"node_type_id": node_type.node_type_id, "version": node_type.version},
            )
        if not isinstance(node_type.input_schema, dict):
            raise ArpServerError(
                code="arggen_schema_invalid",
                message="NodeType input_schema must be an object",
                status_code=422,
                details={"node_type_id": node_type.node_type_id, "version": node_type.version},
            )

        schema_issues = find_openai_strict_schema_issues(node_type.input_schema, limit=10)
        if schema_issues:
            logger.warning(
                "ArgGen NodeType input_schema is not OpenAI-strict (node_type_id=%s, version=%s, issues=%s)",
                node_type.node_type_id,
                node_type.version,
                schema_issues,
            )

        validation_error: dict[str, Any] | None = None
        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            logger.info(
                "ArgGen LLM request (attempt=%s/%s, node_type_id=%s, version=%s, goal_len=%s, has_validation_error=%s, schema_issues=%s)",
                attempt + 1,
                self._max_retries + 1,
                node_type.node_type_id,
                node_type.version,
                len(subtask_goal),
                validation_error is not None,
                len(schema_issues),
            )
            action_description = (node_type.description or "").strip() or node_type.node_type_id
            payload: dict[str, Any] = {
                "subtask": {"goal": subtask_goal},
                "selected_action": {
                    "node_type_id": node_type.node_type_id,
                    "version": node_type.version,
                    "description": action_description,
                },
                "context": context,
            }
            if validation_error is not None:
                payload["previous_validation_error"] = validation_error
            messages = [
                Message.system(ARGGEN_SYSTEM_PROMPT),
                Message.user(json.dumps(payload, sort_keys=True)),
            ]
            response = await self._llm.response(messages, response_schema=node_type.input_schema)
            if response.parsed is None:
                raise LlmError(code="parse_error", message="Arg-gen response missing parsed output")
            if not isinstance(response.parsed, dict):
                raise LlmError(code="parse_error", message="Arg-gen structured response must be a JSON object")

            parsed = response.parsed
            try:
                # Validate the raw structured output against the declared input schema.
                # (NodeType schemas are expected to be "strict" schemas where optional fields
                # are represented as nullable types rather than omitted keys.)
                validate_json_schema(parsed, node_type.input_schema)
            except Exception as exc:
                last_error = exc
                validation_error = {
                    "attempt": attempt + 1,
                    "error": str(exc),
                }
                continue

            return ArgGenResult(
                inputs=parsed,
                provider=response.provider,
                model=response.model,
                latency_ms=response.latency_ms,
                usage=response.usage,
            )

        raise ArpServerError(
            code="arggen_validation_failed",
            message="Arg-gen failed to produce valid inputs for the node schema",
            status_code=502,
            details={"error": str(last_error) if last_error else None},
        )
