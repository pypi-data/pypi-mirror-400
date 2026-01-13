from __future__ import annotations

from typing import Protocol

from arp_standard_model import (
    CandidateSet,
    CandidateSetRequest,
    NodeRun,
    NodeRunCompleteRequest,
    NodeRunEvaluationReportRequest,
    NodeRunsCreateRequest,
    NodeRunsCreateResponse,
    NodeType,
)


class RunCoordinatorClientLike(Protocol):
    async def create_node_runs(self, body: NodeRunsCreateRequest) -> NodeRunsCreateResponse:
        ...

    async def get_node_run(self, node_run_id: str) -> NodeRun:
        ...

    async def complete_node_run(self, node_run_id: str, body: NodeRunCompleteRequest) -> None:
        ...

    async def report_node_run_evaluation(
        self, node_run_id: str, body: NodeRunEvaluationReportRequest
    ) -> None:
        ...


class SelectionClientLike(Protocol):
    async def generate_candidate_set(self, body: CandidateSetRequest) -> CandidateSet:
        ...


class NodeRegistryClientLike(Protocol):
    async def get_node_type(self, node_type_id: str, version: str | None = None) -> NodeType:
        ...
