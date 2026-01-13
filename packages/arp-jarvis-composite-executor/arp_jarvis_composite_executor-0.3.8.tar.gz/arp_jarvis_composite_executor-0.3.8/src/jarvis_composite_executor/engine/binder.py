from __future__ import annotations

from typing import Any

from arp_standard_model import Candidate, CandidateSet, NodeTypeRef


def choose_candidate(candidate_set: CandidateSet) -> Candidate | None:
    if not candidate_set.candidates:
        return None

    selection = _extensions_dict(candidate_set.extensions)
    if selection.get("jarvis.selection.needs_planner") is True:
        if (planner_ref := _planner_ref(selection)) is not None:
            for candidate in candidate_set.candidates:
                if candidate.node_type_ref == planner_ref:
                    return candidate
            return None

        for candidate in candidate_set.candidates:
            if candidate.node_type_ref.node_type_id.startswith("jarvis.composite.planner"):
                return candidate
        return None

    return candidate_set.candidates[0]


def _extensions_dict(extensions: Any) -> dict[str, Any]:
    if extensions is None:
        return {}
    if hasattr(extensions, "model_dump"):
        return extensions.model_dump(exclude_none=True)
    if isinstance(extensions, dict):
        return dict(extensions)
    return {}


def _planner_ref(selection: dict[str, Any]) -> NodeTypeRef | None:
    raw = selection.get("jarvis.selection.planner_node_type_ref")
    if not isinstance(raw, dict):
        return None
    node_type_id = raw.get("node_type_id")
    version = raw.get("version")
    if not isinstance(node_type_id, str) or not isinstance(version, str):
        return None
    return NodeTypeRef(node_type_id=node_type_id, version=version)
