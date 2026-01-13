from __future__ import annotations

import asyncio

import pytest
from arp_llm.providers.dev_mock import DevMockChatFixture, DevMockChatModel
from arp_standard_model import (
    Candidate,
    CandidateSet,
    CompositeBeginRequest,
    EndpointLocator,
    EvaluationStatus,
    NodeKind,
    NodeRun,
    NodeRunCompleteRequest,
    NodeRunEvaluationReportRequest,
    NodeRunState,
    NodeRunTerminalState,
    NodeRunsCreateRequest,
    NodeRunsCreateResponse,
    NodeType,
    NodeTypeRef,
)
from arp_standard_server import ArpServerError

from jarvis_composite_executor.config import CompositeConfig
from jarvis_composite_executor.engine.arggen import ArgGen
from jarvis_composite_executor.engine.driver import CompositeAssignmentDriver
from jarvis_composite_executor.engine.planner import Planner


class RecordingRunCoordinator:
    def __init__(self) -> None:
        self.completed: list[NodeRunCompleteRequest] = []
        self.evaluations: list[NodeRunEvaluationReportRequest] = []

    async def create_node_runs(self, body: NodeRunsCreateRequest) -> NodeRunsCreateResponse:
        _ = body
        raise RuntimeError("not implemented")

    async def get_node_run(self, node_run_id: str) -> NodeRun:
        _ = node_run_id
        raise RuntimeError("not implemented")

    async def complete_node_run(self, node_run_id: str, body: NodeRunCompleteRequest) -> None:
        _ = node_run_id
        self.completed.append(body)

    async def report_node_run_evaluation(self, node_run_id: str, body: NodeRunEvaluationReportRequest) -> None:
        _ = node_run_id
        self.evaluations.append(body)


class EmptySelection:
    async def generate_candidate_set(self, body) -> CandidateSet:
        _ = body
        return CandidateSet(candidate_set_id="set", subtask_id="sub", candidates=[])


class CandidateSelection:
    async def generate_candidate_set(self, body) -> CandidateSet:
        _ = body
        return CandidateSet(
            candidate_set_id="set",
            subtask_id="sub",
            candidates=[Candidate(node_type_ref=NodeTypeRef(node_type_id="node", version="1"), score=1.0)],
        )


class EmptyNodeRegistry:
    async def get_node_type(self, node_type_id: str, version: str | None = None) -> NodeType:
        _ = node_type_id, version
        return NodeType(
            node_type_id="node",
            version="1",
            kind=NodeKind.atomic,
            description=None,
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
        )


def _base_config() -> CompositeConfig:
    return CompositeConfig(
        max_steps_default=2,
        max_depth_default=2,
        poll_timeout_sec=0.05,
        poll_interval_sec=0.0,
        arggen_max_retries=0,
        context_window=None,
        max_concurrency=None,
    )


def _base_request(node_run_id: str = "node") -> CompositeBeginRequest:
    return CompositeBeginRequest(
        run_id="run",
        node_run_id=node_run_id,
        node_type_ref=NodeTypeRef(node_type_id="jarvis.composite.planner", version="0.3.7"),
        inputs={"goal": "test"},
        coordinator_endpoint=EndpointLocator.model_validate("http://127.0.0.1:8081"),
    )


def test_driver_canceled_before_start() -> None:
    run_coordinator = RecordingRunCoordinator()
    planner = Planner(DevMockChatModel(fixtures=[DevMockChatFixture(text="p", parsed={"subtasks": [], "summary": None})]))
    arggen = ArgGen(DevMockChatModel(fixtures=[DevMockChatFixture(text="a", parsed={})]), max_retries=0)
    driver = CompositeAssignmentDriver(
        run_coordinator=run_coordinator,
        selection=CandidateSelection(),
        node_registry=EmptyNodeRegistry(),
        planner=planner,
        arggen=arggen,
        config=_base_config(),
        canceled={"node"},
    )

    asyncio.run(driver.run(_base_request()))

    assert run_coordinator.completed[0].state == NodeRunTerminalState.canceled


def test_driver_empty_plan_finalizes() -> None:
    run_coordinator = RecordingRunCoordinator()
    planner_fixture = DevMockChatFixture(text="planner", parsed={"subtasks": [], "summary": "done"})
    planner = Planner(DevMockChatModel(fixtures=[planner_fixture]))
    arggen = ArgGen(DevMockChatModel(fixtures=[DevMockChatFixture(text="a", parsed={})]), max_retries=0)

    driver = CompositeAssignmentDriver(
        run_coordinator=run_coordinator,
        selection=CandidateSelection(),
        node_registry=EmptyNodeRegistry(),
        planner=planner,
        arggen=arggen,
        config=_base_config(),
        canceled=set(),
    )

    asyncio.run(driver.run(_base_request()))

    assert run_coordinator.evaluations[0].evaluation_result.status == EvaluationStatus.success
    assert run_coordinator.completed[0].state == NodeRunTerminalState.succeeded


def test_driver_no_candidates() -> None:
    planner_fixture = DevMockChatFixture(
        text="planner",
        parsed={"subtasks": [{"subtask_id": "s1", "goal": "do thing", "notes": None}], "summary": None},
    )
    planner = Planner(DevMockChatModel(fixtures=[planner_fixture]))
    arggen = ArgGen(DevMockChatModel(fixtures=[DevMockChatFixture(text="a", parsed={})]), max_retries=0)

    driver = CompositeAssignmentDriver(
        run_coordinator=RecordingRunCoordinator(),
        selection=EmptySelection(),
        node_registry=EmptyNodeRegistry(),
        planner=planner,
        arggen=arggen,
        config=_base_config(),
        canceled=set(),
    )

    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(driver.run(_base_request()))

    assert excinfo.value.code == "composite_no_candidates"


def test_driver_no_child_runs() -> None:
    class NoChildRunCoordinator(RecordingRunCoordinator):
        async def create_node_runs(self, body: NodeRunsCreateRequest) -> NodeRunsCreateResponse:
            _ = body
            return NodeRunsCreateResponse(node_runs=[])

        async def get_node_run(self, node_run_id: str) -> NodeRun:
            raise RuntimeError("unexpected")

    planner_fixture = DevMockChatFixture(
        text="planner",
        parsed={"subtasks": [{"subtask_id": "s1", "goal": "do thing", "notes": None}], "summary": None},
    )
    arggen_fixture = DevMockChatFixture(text="arggen", parsed={"text": "ok"})
    llm = DevMockChatModel(fixtures=[planner_fixture, arggen_fixture])

    driver = CompositeAssignmentDriver(
        run_coordinator=NoChildRunCoordinator(),
        selection=CandidateSelection(),
        node_registry=EmptyNodeRegistry(),
        planner=Planner(llm),
        arggen=ArgGen(llm, max_retries=0),
        config=_base_config(),
        canceled=set(),
    )

    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(driver.run(_base_request()))

    assert excinfo.value.code == "composite_no_child_runs"


def test_driver_failed_child_breaks() -> None:
    class FailedRunCoordinator(RecordingRunCoordinator):
        async def create_node_runs(self, body: NodeRunsCreateRequest) -> NodeRunsCreateResponse:
            _ = body
            node_run = NodeRun(
                node_run_id="child",
                node_type_ref=NodeTypeRef(node_type_id="node", version="1"),
                state=NodeRunState.failed,
                run_id="run",
            )
            return NodeRunsCreateResponse(node_runs=[node_run])

        async def get_node_run(self, node_run_id: str) -> NodeRun:
            _ = node_run_id
            return NodeRun(
                node_run_id="child",
                node_type_ref=NodeTypeRef(node_type_id="node", version="1"),
                state=NodeRunState.failed,
                run_id="run",
            )

    planner_fixture = DevMockChatFixture(
        text="planner",
        parsed={"subtasks": [{"subtask_id": "s1", "goal": "do thing", "notes": None}], "summary": None},
    )
    arggen_fixture = DevMockChatFixture(text="arggen", parsed={"text": "ok"})
    llm = DevMockChatModel(fixtures=[planner_fixture, arggen_fixture])

    coordinator = FailedRunCoordinator()
    driver = CompositeAssignmentDriver(
        run_coordinator=coordinator,
        selection=CandidateSelection(),
        node_registry=EmptyNodeRegistry(),
        planner=Planner(llm),
        arggen=ArgGen(llm, max_retries=0),
        config=_base_config(),
        canceled=set(),
    )

    asyncio.run(driver.run(_base_request()))

    assert driver._canceled == set()
    assert coordinator.completed[0].state == NodeRunTerminalState.failed


def test_driver_composite_inputs_are_filled() -> None:
    class CompositeNodeRegistry(EmptyNodeRegistry):
        async def get_node_type(self, node_type_id: str, version: str | None = None) -> NodeType:
            _ = node_type_id, version
            return NodeType(
                node_type_id="planner",
                version="1",
                kind=NodeKind.composite,
                description=None,
                input_schema={"type": "object", "properties": {}, "required": []},
            )

    class CapturingRunCoordinator(RecordingRunCoordinator):
        def __init__(self) -> None:
            super().__init__()
            self.created: list[NodeRunsCreateRequest] = []

        async def create_node_runs(self, body: NodeRunsCreateRequest) -> NodeRunsCreateResponse:
            self.created.append(body)
            node_run = NodeRun(
                node_run_id="child",
                node_type_ref=body.node_runs[0].node_type_ref,
                state=NodeRunState.succeeded,
                run_id=body.run_id,
            )
            return NodeRunsCreateResponse(node_runs=[node_run])

        async def get_node_run(self, node_run_id: str) -> NodeRun:
            return NodeRun(
                node_run_id=node_run_id,
                node_type_ref=NodeTypeRef(node_type_id="planner", version="1"),
                state=NodeRunState.succeeded,
                run_id="run",
            )

    planner_fixture = DevMockChatFixture(
        text="planner",
        parsed={"subtasks": [{"subtask_id": "s1", "goal": "do thing", "notes": None}], "summary": None},
    )
    arggen_fixture = DevMockChatFixture(text="arggen", parsed={})
    llm = DevMockChatModel(fixtures=[planner_fixture, arggen_fixture])
    class CompositeSelection:
        async def generate_candidate_set(self, body) -> CandidateSet:
            _ = body
            return CandidateSet(
                candidate_set_id="set",
                subtask_id="s1",
                candidates=[
                    Candidate(node_type_ref=NodeTypeRef(node_type_id="planner", version="1"), score=1.0)
                ],
            )

    coordinator = CapturingRunCoordinator()
    driver = CompositeAssignmentDriver(
        run_coordinator=coordinator,
        selection=CompositeSelection(),
        node_registry=CompositeNodeRegistry(),
        planner=Planner(llm),
        arggen=ArgGen(llm, max_retries=0),
        config=_base_config(),
        canceled=set(),
    )

    asyncio.run(driver.run(_base_request()))

    inputs = coordinator.created[0].node_runs[0].inputs
    assert inputs["goal"] == "do thing"
    assert inputs["depth"] == 1
    assert inputs["max_depth"] == 2


def test_wait_for_terminal_timeout_and_canceled() -> None:
    class FlakyRunCoordinator(RecordingRunCoordinator):
        async def get_node_run(self, node_run_id: str) -> NodeRun:
            raise RuntimeError("boom")

    driver = CompositeAssignmentDriver(
        run_coordinator=FlakyRunCoordinator(),
        selection=EmptySelection(),
        node_registry=EmptyNodeRegistry(),
        planner=Planner(DevMockChatModel(fixtures=[DevMockChatFixture(text="p", parsed={"subtasks": [], "summary": None})])),
        arggen=ArgGen(DevMockChatModel(fixtures=[DevMockChatFixture(text="a", parsed={})]), max_retries=0),
        config=_base_config(),
        canceled=set(),
    )

    result = asyncio.run(driver._wait_for_terminal("node"))
    assert result is None

    driver._canceled.add("node")
    canceled = asyncio.run(driver._wait_for_terminal("node"))
    assert canceled is None


def test_wait_for_terminal_progress() -> None:
    class ProgressRunCoordinator(RecordingRunCoordinator):
        def __init__(self) -> None:
            super().__init__()
            self.calls = 0

        async def get_node_run(self, node_run_id: str) -> NodeRun:
            self.calls += 1
            state = NodeRunState.running if self.calls == 1 else NodeRunState.succeeded
            return NodeRun(
                node_run_id=node_run_id,
                node_type_ref=NodeTypeRef(node_type_id="node", version="1"),
                state=state,
                run_id="run",
            )

    driver = CompositeAssignmentDriver(
        run_coordinator=ProgressRunCoordinator(),
        selection=EmptySelection(),
        node_registry=EmptyNodeRegistry(),
        planner=Planner(DevMockChatModel(fixtures=[DevMockChatFixture(text="p", parsed={"subtasks": [], "summary": None})])),
        arggen=ArgGen(DevMockChatModel(fixtures=[DevMockChatFixture(text="a", parsed={})]), max_retries=0),
        config=_base_config(),
        canceled=set(),
    )

    result = asyncio.run(driver._wait_for_terminal("node"))

    assert result is not None
    assert result.state == NodeRunState.succeeded
