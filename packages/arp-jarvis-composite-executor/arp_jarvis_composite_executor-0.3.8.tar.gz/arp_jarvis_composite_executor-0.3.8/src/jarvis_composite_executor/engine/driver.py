from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from arp_standard_model import (
    BindingDecision,
    CandidateSet,
    CandidateSetRequest,
    ConstraintEnvelope,
    Error,
    EvaluationResult,
    EvaluationStatus,
    Extensions,
    NodeKind,
    NodeRun,
    NodeRunCompleteRequest,
    NodeRunEvaluationReportRequest,
    NodeRunState,
    NodeRunTerminalState,
    NodeRunsCreateRequest,
    NodeRunCreateSpec,
    NodeType,
    SubtaskSpec,
)
from arp_standard_server import ArpServerError

from ..config import CompositeConfig
from ..utils import now
from .arggen import ArgGen
from .binder import choose_candidate
from .planner import Planner
from ..clients import NodeRegistryClientLike, RunCoordinatorClientLike, SelectionClientLike

logger = logging.getLogger(__name__)


class CompositeAssignmentDriver:
    def __init__(
        self,
        *,
        run_coordinator: RunCoordinatorClientLike,
        selection: SelectionClientLike,
        node_registry: NodeRegistryClientLike,
        planner: Planner,
        arggen: ArgGen,
        config: CompositeConfig,
        canceled: set[str],
    ) -> None:
        self._run_coordinator = run_coordinator
        self._selection = selection
        self._node_registry = node_registry
        self._planner = planner
        self._arggen = arggen
        self._config = config
        self._canceled = canceled

    async def run(self, request) -> None:
        node_run_id = request.node_run_id
        if node_run_id in self._canceled:
            await self._complete_canceled(node_run_id)
            return

        goal = _infer_goal(request.inputs)
        context = _extract_context(request.inputs)
        depth = _extract_int(request.inputs, "depth") or 0
        max_steps = _resolve_limit(
            name="max_steps",
            explicit=_extract_int(request.inputs, "max_steps"),
            constraint=_constraint_max_steps(request.constraints),
            default=self._config.max_steps_default,
        )
        max_depth = _resolve_limit(
            name="max_depth",
            explicit=_extract_int(request.inputs, "max_depth"),
            constraint=_constraint_max_depth(request.constraints),
            default=self._config.max_depth_default,
        )

        planner_result = await self._planner.plan(
            goal=goal,
            context=_planner_context(context, request.run_context),
            max_steps=max_steps,
            depth=depth,
            max_depth=max_depth,
        )

        if not planner_result.subtasks:
            await self._finalize_composite(
                node_run_id=node_run_id,
                results=[],
                planner_summary=planner_result.summary,
            )
            return

        working_context: list[dict[str, Any]] = []
        results: list[NodeRun] = []

        for subtask in planner_result.subtasks:
            if node_run_id in self._canceled:
                await self._complete_canceled(node_run_id)
                return

            candidate_set = await self._generate_candidate_set(
                request,
                subtask=subtask,
                goal=goal,
                working_context=working_context,
            )
            if (candidate := choose_candidate(candidate_set)) is None:
                raise ArpServerError(
                    code="composite_no_candidates",
                    message="Selection produced no candidates for subtask",
                    status_code=422,
                    details={"subtask_id": subtask.subtask_id},
                )

            node_type = await self._node_registry.get_node_type(
                candidate.node_type_ref.node_type_id,
                candidate.node_type_ref.version,
            )
            inputs = await self._resolve_inputs(
                request=request,
                node_type=node_type,
                candidate_set=candidate_set,
                subtask_goal=subtask.goal,
                working_context=working_context,
                depth=depth,
                max_depth=max_depth,
                max_steps=max_steps,
            )

            binding_decision = BindingDecision(
                subtask_id=subtask.subtask_id,
                candidate_set_id=candidate_set.candidate_set_id,
                chosen_node_type_ref=candidate.node_type_ref,
                rationale=candidate.rationale,
            )
            spec = _node_run_spec(
                inputs=inputs,
                candidate_set=candidate_set,
                binding_decision=binding_decision,
                constraints=request.constraints,
            )
            response = await self._run_coordinator.create_node_runs(
                NodeRunsCreateRequest(
                    run_id=request.run_id,
                    parent_node_run_id=node_run_id,
                    node_runs=[spec],
                )
            )
            if not response.node_runs:
                raise ArpServerError(
                    code="composite_no_child_runs",
                    message="Run Coordinator returned no child NodeRuns",
                    status_code=502,
                )

            child_run = response.node_runs[0]
            result = await self._wait_for_terminal(child_run.node_run_id)
            if result is None:
                if node_run_id in self._canceled:
                    await self._complete_canceled(node_run_id)
                    return
                raise ArpServerError(
                    code="composite_child_timeout",
                    message="Timed out waiting for child NodeRun completion",
                    status_code=504,
                    details={"node_run_id": child_run.node_run_id},
                )

            results.append(result)
            working_context.append(_context_step_entry(result))
            working_context = _bound_context(working_context, window=self._config.context_window)

            if result.state != NodeRunState.succeeded:
                break

        await self._finalize_composite(
            node_run_id=node_run_id,
            results=results,
            planner_summary=planner_result.summary,
        )

    async def _generate_candidate_set(
        self,
        request,
        *,
        subtask,
        goal: str,
        working_context: list[dict[str, Any]],
    ) -> CandidateSet:
        subtask_extensions_dict = _merge_extensions(
            request.extensions,
            {
                "jarvis.subtask.notes": subtask.notes,
                "jarvis.root_goal": goal,
            },
        )
        subtask_extensions = Extensions.model_validate(subtask_extensions_dict) if subtask_extensions_dict else None
        subtask_spec = SubtaskSpec(
            subtask_id=subtask.subtask_id,
            goal=subtask.goal,
            extensions=subtask_extensions,
        )
        request_extensions_dict = _merge_extensions(
            request.extensions,
            {
                "jarvis.prior_steps": working_context if working_context else None,
            },
        )
        request_extensions = Extensions.model_validate(request_extensions_dict) if request_extensions_dict else None
        return await self._selection.generate_candidate_set(
            CandidateSetRequest(
                subtask_spec=subtask_spec,
                constraints=request.constraints,
                extensions=request_extensions,
                run_context=request.run_context,
            )
        )

    async def _resolve_inputs(
        self,
        *,
        request,
        node_type: NodeType,
        candidate_set: CandidateSet,
        subtask_goal: str,
        working_context: list[dict[str, Any]],
        depth: int,
        max_depth: int,
        max_steps: int,
    ) -> dict[str, Any]:
        arg_context = _arggen_context(
            root_goal=_infer_goal(request.inputs),
            root_context=_extract_context(request.inputs),
            working_context=working_context,
            run_context=request.run_context,
            candidate_set=candidate_set,
        )
        result = await self._arggen.generate_inputs(
            subtask_goal=subtask_goal,
            node_type=node_type,
            context=arg_context,
        )
        inputs = dict(result.inputs)

        if node_type.kind == NodeKind.composite:
            _ensure_composite_inputs(
                inputs=inputs,
                goal=subtask_goal,
                context=_extract_context(request.inputs),
                depth=depth + 1,
                max_depth=max_depth,
                max_steps=max_steps,
            )

        return inputs

    async def _wait_for_terminal(self, node_run_id: str) -> NodeRun | None:
        timeout_sec = self._config.poll_timeout_sec
        interval_sec = self._config.poll_interval_sec
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() <= deadline:
            if node_run_id in self._canceled:
                return None
            try:
                node_run = await self._run_coordinator.get_node_run(node_run_id)
            except Exception as exc:
                logger.warning("Failed to poll node run %s: %s", node_run_id, exc)
                await asyncio.sleep(interval_sec)
                continue
            if node_run.state in {NodeRunState.succeeded, NodeRunState.failed, NodeRunState.canceled}:
                return node_run
            await asyncio.sleep(interval_sec)
        return None

    async def _finalize_composite(
        self,
        *,
        node_run_id: str,
        results: list[NodeRun],
        planner_summary: str | None,
    ) -> None:
        evaluation_status = (
            EvaluationStatus.success
            if results and all(run.state == NodeRunState.succeeded for run in results)
            else EvaluationStatus.fail
        )
        if not results:
            evaluation_status = EvaluationStatus.success

        await self._run_coordinator.report_node_run_evaluation(
            node_run_id,
            NodeRunEvaluationReportRequest(
                evaluation_result=EvaluationResult(
                    status=evaluation_status,
                    reason_code="composite_evaluation",
                )
            ),
        )

        terminal_state = _resolve_terminal_state(results)
        error = None
        if terminal_state != NodeRunTerminalState.succeeded:
            error = Error(code="child_failed", message="One or more child NodeRuns failed")

        outputs = {
            "planner_summary": planner_summary,
            "child_node_runs": [_summarize_node_run(run) for run in results],
        }
        await self._run_coordinator.complete_node_run(
            node_run_id,
            NodeRunCompleteRequest(
                state=terminal_state,
                outputs=outputs,
                error=error,
            ),
        )

    async def _complete_canceled(self, node_run_id: str) -> None:
        await self._run_coordinator.complete_node_run(
            node_run_id,
            NodeRunCompleteRequest(state=NodeRunTerminalState.canceled),
        )


def _infer_goal(inputs: dict[str, Any]) -> str:
    if isinstance(inputs.get("goal"), str) and inputs["goal"].strip():
        return str(inputs["goal"]).strip()
    if isinstance(inputs.get("prompt"), str) and inputs["prompt"].strip():
        return str(inputs["prompt"]).strip()
    raise ArpServerError(
        code="composite_goal_missing",
        message="Composite inputs must include a goal or prompt",
        status_code=400,
    )


def _extract_context(inputs: dict[str, Any]) -> dict[str, Any]:
    context = inputs.get("context")
    if isinstance(context, dict):
        return context
    return {}


def _extract_int(inputs: dict[str, Any], name: str) -> int | None:
    value = inputs.get(name)
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _resolve_limit(
    *,
    name: str,
    explicit: int | None,
    constraint: int | None,
    default: int | None,
) -> int:
    if explicit is not None:
        value = explicit
    elif constraint is not None:
        value = constraint
    else:
        value = default
    if value is None:
        raise ArpServerError(
            code="composite_limit_missing",
            message=f"{name} must be provided via inputs, constraints, or env defaults",
            status_code=400,
            details={"limit": name},
        )
    return value


def _constraint_max_steps(constraints: ConstraintEnvelope | None) -> int | None:
    if constraints and constraints.budgets:
        return constraints.budgets.max_steps
    return None


def _constraint_max_depth(constraints: ConstraintEnvelope | None) -> int | None:
    if constraints and constraints.structural:
        return constraints.structural.max_depth
    return None


def _planner_context(context: dict[str, Any], run_context) -> dict[str, Any]:
    # Keep LLM prompts focused; avoid leaking internal IDs/trace data.
    return dict(context)


def _arggen_context(
    *,
    root_goal: str,
    root_context: dict[str, Any],
    working_context: list[dict[str, Any]],
    run_context,
    candidate_set: CandidateSet,
) -> dict[str, Any]:
    return {
        "root_goal": root_goal,
        "root_context": root_context,
        "previous_steps": working_context,
    }


def _merge_extensions(base: Extensions | None, additions: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    if base is not None:
        if hasattr(base, "model_dump"):
            payload.update(base.model_dump(exclude_none=True))
        else:
            payload.update(dict(base))
    payload.update({key: value for key, value in additions.items() if value is not None})
    return payload


def _node_run_spec(
    *,
    inputs: dict[str, Any],
    candidate_set: CandidateSet,
    binding_decision: BindingDecision,
    constraints: ConstraintEnvelope | None,
):
    return NodeRunCreateSpec(
        node_type_ref=binding_decision.chosen_node_type_ref,
        inputs=inputs,
        constraints=constraints,
        candidate_set_id=candidate_set.candidate_set_id,
        binding_decision=binding_decision,
    )


def _ensure_composite_inputs(
    *,
    inputs: dict[str, Any],
    goal: str,
    context: dict[str, Any],
    depth: int,
    max_depth: int,
    max_steps: int,
) -> None:
    inputs.setdefault("goal", goal)
    inputs.setdefault("context", context)
    inputs.setdefault("depth", depth)
    inputs.setdefault("max_depth", max_depth)
    inputs.setdefault("max_steps", max_steps)


def _resolve_terminal_state(results: list[NodeRun]) -> NodeRunTerminalState:
    if any(run.state == NodeRunState.canceled for run in results):
        return NodeRunTerminalState.canceled
    if any(run.state == NodeRunState.failed for run in results):
        return NodeRunTerminalState.failed
    return NodeRunTerminalState.succeeded


def _summarize_node_run(run: NodeRun, *, subtask_id: str | None = None) -> dict[str, Any]:
    state = run.state.value if hasattr(run.state, "value") else run.state
    summary: dict[str, Any] = {
        "node_run_id": run.node_run_id,
        "node_type_ref": run.node_type_ref.model_dump(exclude_none=True),
        "state": state,
        "outputs": run.outputs,
        "output_artifacts": run.output_artifacts,
    }
    if subtask_id:
        summary["subtask_id"] = subtask_id
    return summary


def _context_step_entry(run: NodeRun) -> dict[str, Any]:
    outputs = run.outputs if run.outputs is not None else {}
    return {
        "action": run.node_type_ref.node_type_id,
        "outputs": outputs,
    }


def _bound_context(entries: list[dict[str, Any]], *, window: int | None) -> list[dict[str, Any]]:
    if window is None or window <= 0:
        return entries
    return entries[-window:]
