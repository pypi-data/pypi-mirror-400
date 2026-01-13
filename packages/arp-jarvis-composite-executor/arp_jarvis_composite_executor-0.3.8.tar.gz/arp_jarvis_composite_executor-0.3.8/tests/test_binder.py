from __future__ import annotations

from arp_standard_model import Candidate, CandidateSet, Extensions, NodeTypeRef

from jarvis_composite_executor.engine.binder import choose_candidate


def test_choose_candidate_returns_first() -> None:
    candidate = Candidate(node_type_ref=NodeTypeRef(node_type_id="node", version="1"), score=1.0)
    candidate_set = CandidateSet(
        candidate_set_id="set-1",
        subtask_id="subtask",
        candidates=[candidate],
    )

    assert choose_candidate(candidate_set) == candidate


def test_choose_candidate_empty() -> None:
    candidate_set = CandidateSet(candidate_set_id="set-1", subtask_id="subtask", candidates=[])

    assert choose_candidate(candidate_set) is None


def test_choose_candidate_prefers_planner_when_flagged() -> None:
    planner = Candidate(node_type_ref=NodeTypeRef(node_type_id="jarvis.composite.planner.general", version="0.3.7"), score=1.0)
    atomic = Candidate(node_type_ref=NodeTypeRef(node_type_id="jarvis.core.echo", version="0.3.7"), score=1.0)
    candidate_set = CandidateSet(
        candidate_set_id="set-1",
        subtask_id="subtask",
        candidates=[atomic, planner],
        extensions=Extensions.model_validate(
            {
                "jarvis.selection.needs_planner": True,
                "jarvis.selection.planner_node_type_ref": {
                    "node_type_id": "jarvis.composite.planner.general",
                    "version": "0.3.7",
                },
            }
        ),
    )

    assert choose_candidate(candidate_set) == planner
