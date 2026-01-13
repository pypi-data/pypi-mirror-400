from __future__ import annotations

import asyncio

import pytest
from arp_standard_model import (
    CompositeBeginRequest,
    CompositeExecutorBeginCompositeNodeRunRequest,
    EndpointLocator,
    NodeRunTerminalState,
    NodeTypeRef,
)
from arp_standard_server import ArpServerError

from jarvis_composite_executor.executor import CompositeExecutor, _maybe_await, _report_failure


class FakeRunCoordinator:
    def __init__(self) -> None:
        self.completed: list[tuple[str, NodeRunTerminalState]] = []

    async def create_node_runs(self, body):
        _ = body
        raise RuntimeError("not implemented")

    async def get_node_run(self, node_run_id: str):
        _ = node_run_id
        raise RuntimeError("not implemented")

    async def report_node_run_evaluation(self, node_run_id: str, body) -> None:
        _ = node_run_id, body
        raise RuntimeError("not implemented")

    async def complete_node_run(self, node_run_id: str, body) -> None:
        self.completed.append((node_run_id, body.state))


class FailingRunCoordinator:
    async def create_node_runs(self, body):
        _ = body
        raise RuntimeError("not implemented")

    async def get_node_run(self, node_run_id: str):
        _ = node_run_id
        raise RuntimeError("not implemented")

    async def report_node_run_evaluation(self, node_run_id: str, body) -> None:
        _ = node_run_id, body
        raise RuntimeError("not implemented")

    async def complete_node_run(self, node_run_id: str, body) -> None:
        _ = node_run_id, body
        raise RuntimeError("fail")


def test_begin_composite_requires_selection() -> None:
    executor = CompositeExecutor(selection_service=None, node_registry=None, llm=None, config=None)
    request = CompositeExecutorBeginCompositeNodeRunRequest(
        body=CompositeBeginRequest(
            run_id="run-1",
            node_run_id="node-1",
            node_type_ref=NodeTypeRef(node_type_id="jarvis.composite.planner", version="0.3.7"),
            inputs={"goal": "test"},
            coordinator_endpoint=EndpointLocator.model_validate("http://127.0.0.1:8081"),
        )
    )

    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(executor.begin_composite_node_run(request))

    assert excinfo.value.code == "selection_service_missing"


def test_report_failure() -> None:
    coordinator = FakeRunCoordinator()
    error = ArpServerError(code="boom", message="fail", status_code=500)

    asyncio.run(_report_failure(coordinator, "node-1", error))

    assert coordinator.completed == [("node-1", NodeRunTerminalState.failed)]


def test_report_failure_logs_errors() -> None:
    asyncio.run(
        _report_failure(
            FailingRunCoordinator(),
            "node-1",
            ArpServerError(code="boom", message="fail", status_code=500),
        )
    )


def test_maybe_await_with_semaphore() -> None:
    results: list[str] = []

    async def runner() -> None:
        results.append("ok")

    asyncio.run(_maybe_await(asyncio.Semaphore(1), runner()))

    assert results == ["ok"]


def test_maybe_await_without_semaphore() -> None:
    results: list[str] = []

    async def runner() -> None:
        results.append("ok")

    asyncio.run(_maybe_await(None, runner()))

    assert results == ["ok"]
