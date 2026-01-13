from __future__ import annotations

import pytest
from typing import cast

from arp_standard_model import (
    Budgets,
    Candidate,
    CandidateSet,
    ConstraintEnvelope,
    Extensions,
    NodeRun,
    NodeRunState,
    NodeTypeRef,
    RunContext,
    Structural,
    Trace,
)
from arp_standard_server import ArpServerError

from jarvis_composite_executor.engine import driver


def test_infer_goal_prefers_goal_and_prompt() -> None:
    assert driver._infer_goal({"goal": "  hello "}) == "hello"
    assert driver._infer_goal({"prompt": "  hi "}) == "hi"
    with pytest.raises(ArpServerError):
        driver._infer_goal({})


def test_extract_helpers() -> None:
    assert driver._extract_context({"context": {"a": 1}}) == {"a": 1}
    assert driver._extract_context({"context": "nope"}) == {}
    assert driver._extract_int({"depth": "2"}, "depth") == 2
    assert driver._extract_int({"depth": 3}, "depth") == 3
    assert driver._extract_int({"depth": "x"}, "depth") is None


def test_resolve_limit_from_inputs_constraints_and_defaults() -> None:
    assert driver._resolve_limit(name="max_steps", explicit=3, constraint=9, default=1) == 3
    assert driver._resolve_limit(name="max_steps", explicit=None, constraint=4, default=1) == 4
    assert driver._resolve_limit(name="max_steps", explicit=None, constraint=None, default=2) == 2
    with pytest.raises(ArpServerError):
        driver._resolve_limit(name="max_steps", explicit=None, constraint=None, default=None)


def test_constraints_extractors() -> None:
    envelope = ConstraintEnvelope(
        budgets=Budgets(max_steps=5),
        structural=Structural(max_depth=2),
    )
    assert driver._constraint_max_steps(envelope) == 5
    assert driver._constraint_max_depth(envelope) == 2


def test_planner_context_run_context() -> None:
    run_context = RunContext(
        tenant_id="tenant",
        budgets={"max_steps": 1},
        policy={"mode": "test"},
        trace=Trace(trace_id="trace", span_id="span"),
    )
    payload = driver._planner_context({"foo": "bar"}, run_context)

    assert payload["foo"] == "bar"
    assert payload["run_context"]["tenant_id"] == "tenant"
    assert payload["run_context"]["policy"] == {"mode": "test"}
    assert payload["run_context"]["trace"]["trace_id"] == "trace"


def test_arggen_context_and_extensions_merge() -> None:
    candidate_set = CandidateSet(
        candidate_set_id="set-1",
        subtask_id="subtask-1",
        candidates=[Candidate(node_type_ref=NodeTypeRef(node_type_id="n", version="1"), score=1.0)],
    )
    merged = driver._merge_extensions(Extensions.model_validate({"foo": "bar"}), {"baz": "qux"})
    assert merged["foo"] == "bar"
    assert merged["baz"] == "qux"
    assert driver._merge_extensions(cast(Extensions, {"a": 1}), {"b": 2}) == {"a": 1, "b": 2}

    context = driver._arggen_context(
        root_goal="goal",
        root_context={"root": True},
        working_context=[{"step": 1}],
        run_context=RunContext(tenant_id="tenant"),
        candidate_set=candidate_set,
    )
    assert context["candidate_set_id"] == "set-1"
    assert context["prior_steps"] == [{"step": 1}]
    assert context["run_context"]["tenant_id"] == "tenant"


def test_composite_inputs_and_terminal_state() -> None:
    inputs: dict[str, object] = {}
    driver._ensure_composite_inputs(
        inputs=inputs,
        goal="goal",
        context={"k": "v"},
        depth=1,
        max_depth=2,
        max_steps=3,
    )
    assert inputs["goal"] == "goal"
    assert inputs["depth"] == 1
    assert inputs["max_depth"] == 2
    assert inputs["max_steps"] == 3

    failed_run = NodeRun(
        node_run_id="n1",
        node_type_ref=NodeTypeRef(node_type_id="node", version="1"),
        state=NodeRunState.failed,
        run_id="run",
    )
    assert driver._resolve_terminal_state([failed_run]).value == "failed"
    canceled_run = failed_run.model_copy(update={"state": NodeRunState.canceled})
    assert driver._resolve_terminal_state([canceled_run]).value == "canceled"


def test_summarize_and_bound_context() -> None:
    run = NodeRun(
        node_run_id="n2",
        node_type_ref=NodeTypeRef(node_type_id="node", version="1"),
        state=NodeRunState.succeeded,
        run_id="run",
        outputs={"ok": True},
    )
    summary = driver._summarize_node_run(run, subtask_id="s1")
    assert summary["subtask_id"] == "s1"
    assert summary["outputs"] == {"ok": True}

    bound = driver._bound_context([{"a": 1}, {"b": 2}, {"c": 3}], window=2)
    assert bound == [{"b": 2}, {"c": 3}]
    assert driver._bound_context([{"a": 1}], window=None) == [{"a": 1}]
