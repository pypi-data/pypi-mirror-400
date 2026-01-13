from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from arp_llm.errors import LlmError
from arp_llm.types import ChatModel, Message
from arp_standard_model import NodeType
from arp_standard_server import ArpServerError

from ..llm_assets import ARGGEN_SYSTEM_PROMPT
from ..schema_utils import normalize_schema_for_llm, validate_json_schema


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

        normalized_schema = normalize_schema_for_llm(node_type.input_schema)
        validation_error: dict[str, Any] | None = None
        last_error: Exception | None = None

        for attempt in range(self._max_retries + 1):
            payload = {
                "subtask_goal": subtask_goal,
                "node_type_id": node_type.node_type_id,
                "version": node_type.version,
                "description": node_type.description or "",
                "input_schema": node_type.input_schema,
                "context": context,
                "validation_error": validation_error,
            }
            messages = [
                Message.system(ARGGEN_SYSTEM_PROMPT),
                Message.user(json.dumps(payload, sort_keys=True)),
            ]
            response = await self._llm.response(messages, response_schema=normalized_schema)
            if response.parsed is None:
                raise LlmError(code="parse_error", message="Arg-gen response missing parsed output")
            parsed = response.parsed
            if not isinstance(parsed, dict):
                raise LlmError(
                    code="parse_error",
                    message="Arg-gen structured response must be a JSON object",
                )

            cleaned = {key: value for key, value in parsed.items() if value is not None}
            try:
                validate_json_schema(cleaned, node_type.input_schema)
            except Exception as exc:
                last_error = exc
                validation_error = {
                    "attempt": attempt + 1,
                    "error": str(exc),
                }
                continue

            return ArgGenResult(
                inputs=cleaned,
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
