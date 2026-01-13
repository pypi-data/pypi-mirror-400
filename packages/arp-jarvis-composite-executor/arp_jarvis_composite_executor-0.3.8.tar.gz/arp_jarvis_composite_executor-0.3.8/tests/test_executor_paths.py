from __future__ import annotations

import asyncio
from typing import cast

import pytest
from arp_llm.providers.dev_mock import DevMockChatModel
from arp_standard_model import (
    CompositeBeginRequest,
    CompositeExecutorCancelCompositeNodeRunParams,
    CompositeExecutorCancelCompositeNodeRunRequest,
    CompositeExecutorHealthRequest,
    CompositeExecutorVersionRequest,
    EndpointLocator,
    NodeRunCompleteRequest,
    NodeRunTerminalState,
    NodeTypeRef,
)
from arp_standard_server import ArpServerError

import jarvis_composite_executor.executor as executor_module
from jarvis_composite_executor.config import CompositeConfig
from jarvis_composite_executor.executor import CompositeExecutor


class FakeRunCoordinator:
    def __init__(self) -> None:
        self.completed: list[NodeRunCompleteRequest] = []

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
        _ = node_run_id
        self.completed.append(body)


class DummySelection:
    async def generate_candidate_set(self, body):
        _ = body
        raise RuntimeError("not implemented")


class DummyRegistry:
    async def get_node_type(self, node_type_id: str, version: str | None = None):
        _ = node_type_id, version
        raise RuntimeError("not implemented")


class DummyTask:
    def __init__(self) -> None:
        self.canceled = False

    def cancel(self) -> None:
        self.canceled = True


def _config() -> CompositeConfig:
    return CompositeConfig(
        max_steps_default=1,
        max_depth_default=1,
        poll_timeout_sec=0.01,
        poll_interval_sec=0.0,
        arggen_max_retries=0,
        context_window=None,
        max_concurrency=1,
    )


def _request(node_run_id: str = "node") -> CompositeBeginRequest:
    return CompositeBeginRequest(
        run_id="run",
        node_run_id=node_run_id,
        node_type_ref=NodeTypeRef(node_type_id="jarvis.composite.planner", version="0.3.7"),
        inputs={"goal": "test"},
        coordinator_endpoint=EndpointLocator.model_validate("http://127.0.0.1:8081"),
    )


def test_health_and_version() -> None:
    executor = CompositeExecutor(
        selection_service=DummySelection(),
        node_registry=DummyRegistry(),
        llm=DevMockChatModel(),
        config=_config(),
        service_name="svc",
        service_version="1.2.3",
    )

    health = asyncio.run(executor.health(CompositeExecutorHealthRequest()))
    version = asyncio.run(executor.version(CompositeExecutorVersionRequest()))

    assert health.status.value == "ok"
    assert version.service_name == "svc"


def test_cancel_composite_node_run_cancels_task() -> None:
    executor = CompositeExecutor(
        selection_service=DummySelection(),
        node_registry=DummyRegistry(),
        llm=DevMockChatModel(),
        config=_config(),
    )
    task = DummyTask()
    executor._tasks["node"] = cast(asyncio.Task[None], task)

    asyncio.run(
        executor.cancel_composite_node_run(
            CompositeExecutorCancelCompositeNodeRunRequest(
                params=CompositeExecutorCancelCompositeNodeRunParams(node_run_id="node")
            )
        )
    )

    assert "node" in executor._canceled
    assert task.canceled is True


def test_start_assignment_when_already_running() -> None:
    executor = CompositeExecutor(selection_service=None, node_registry=None, llm=None, config=None)
    executor._tasks["node"] = cast(asyncio.Task[None], DummyTask())

    executor._start_assignment(_request())

    assert executor._tasks["node"] is not None


def test_start_assignment_outside_loop() -> None:
    executor = CompositeExecutor(selection_service=None, node_registry=None, llm=None, config=None)

    executor._start_assignment(_request())

    assert "node" not in executor._tasks


def test_drive_assignment_handles_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDriver:
        def __init__(self, **kwargs) -> None:
            _ = kwargs

        async def run(self, request) -> None:
            _ = request
            raise ArpServerError(code="boom", message="bad", status_code=500)

    coordinator = FakeRunCoordinator()

    monkeypatch.setattr(executor_module, "CompositeAssignmentDriver", FakeDriver)

    executor = CompositeExecutor(
        selection_service=DummySelection(),
        node_registry=DummyRegistry(),
        llm=DevMockChatModel(),
        config=_config(),
        run_coordinator_factory=lambda _: coordinator,
    )

    asyncio.run(executor._drive_assignment(_request()))

    assert coordinator.completed[0].state == NodeRunTerminalState.failed


def test_drive_assignment_handles_cancelled(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDriver:
        def __init__(self, **kwargs) -> None:
            _ = kwargs

        async def run(self, request) -> None:
            _ = request
            raise asyncio.CancelledError

    coordinator = FakeRunCoordinator()

    monkeypatch.setattr(executor_module, "CompositeAssignmentDriver", FakeDriver)

    executor = CompositeExecutor(
        selection_service=DummySelection(),
        node_registry=DummyRegistry(),
        llm=DevMockChatModel(),
        config=_config(),
        run_coordinator_factory=lambda _: coordinator,
    )

    asyncio.run(executor._drive_assignment(_request()))

    assert coordinator.completed[0].state == NodeRunTerminalState.canceled


def test_drive_assignment_handles_generic_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeDriver:
        def __init__(self, **kwargs) -> None:
            _ = kwargs

        async def run(self, request) -> None:
            _ = request
            raise RuntimeError("boom")

    coordinator = FakeRunCoordinator()

    monkeypatch.setattr(executor_module, "CompositeAssignmentDriver", FakeDriver)

    executor = CompositeExecutor(
        selection_service=DummySelection(),
        node_registry=DummyRegistry(),
        llm=DevMockChatModel(),
        config=_config(),
        run_coordinator_factory=lambda _: coordinator,
    )

    asyncio.run(executor._drive_assignment(_request()))

    error = coordinator.completed[0].error
    assert error is not None
    assert error.code == "composite_error"


def test_ensure_ready_missing_dependencies() -> None:
    executor = CompositeExecutor(selection_service=DummySelection(), node_registry=None, llm=None, config=None)
    with pytest.raises(ArpServerError) as excinfo:
        executor._ensure_ready()
    assert excinfo.value.code == "node_registry_missing"

    executor = CompositeExecutor(selection_service=DummySelection(), node_registry=DummyRegistry(), llm=None, config=None)
    with pytest.raises(ArpServerError) as excinfo:
        executor._ensure_ready()
    assert excinfo.value.code == "composite_llm_missing"

    executor = CompositeExecutor(selection_service=DummySelection(), node_registry=DummyRegistry(), llm=DevMockChatModel(), config=None)
    with pytest.raises(ArpServerError) as excinfo:
        executor._ensure_ready()
    assert excinfo.value.code == "composite_config_missing"
