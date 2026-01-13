from __future__ import annotations

from arp_standard_model import Candidate, CandidateSet, NodeTypeRef

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
