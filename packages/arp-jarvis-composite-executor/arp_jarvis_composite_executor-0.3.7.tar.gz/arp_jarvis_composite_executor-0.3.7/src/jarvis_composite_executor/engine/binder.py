from __future__ import annotations

from arp_standard_model import Candidate, CandidateSet


def choose_candidate(candidate_set: CandidateSet) -> Candidate | None:
    if candidate_set.candidates:
        return candidate_set.candidates[0]
    return None
