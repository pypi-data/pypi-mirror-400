from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, cast

import pytest
from arp_auth import AuthClient
from arp_standard_client.node_registry import NodeRegistryClient
from arp_standard_client.run_coordinator import RunCoordinatorClient
from arp_standard_client.selection import SelectionClient
from arp_standard_client.errors import ArpApiError
from arp_standard_model import (
    CandidateSet,
    CandidateSetRequest,
    EvaluationResult,
    EvaluationStatus,
    Health,
    NodeKind,
    NodeRun,
    NodeRunCompleteRequest,
    NodeRunCreateSpec,
    NodeRunState,
    NodeRunsCreateRequest,
    NodeRunsCreateResponse,
    NodeRunEvaluationReportRequest,
    NodeRunTerminalState,
    Status,
    SubtaskSpec,
    NodeType,
    NodeTypeRef,
    VersionInfo,
)
from arp_standard_server import ArpServerError

from jarvis_composite_executor.clients import (
    NodeRegistryGatewayClient,
    RunCoordinatorGatewayClient,
    SelectionGatewayClient,
)


class FakeToken:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token


class FakeAuthClient:
    def client_credentials(self, *, audience: str | None = None, scope: str | None = None) -> FakeToken:
        _ = audience, scope
        return FakeToken("token")


class DummyRawClient:
    def __init__(self) -> None:
        self.headers: dict[str, str] | None = None

    def with_headers(self, headers: dict[str, str]) -> "DummyRawClient":
        self.headers = headers
        return self


class DummyClient:
    def __init__(self) -> None:
        self.raw_client = DummyRawClient()


def _auth_client() -> AuthClient:
    return cast(AuthClient, FakeAuthClient())


def _selection_gateway(service: DummySelectionService) -> SelectionGatewayClient:
    raw_client = cast(SelectionClient, DummyClient())
    factory = cast(
        Callable[[Any], SelectionClient],
        lambda raw: cast(SelectionClient, service),
    )
    return SelectionGatewayClient(
        base_url="http://selection",
        auth_client=_auth_client(),
        client=raw_client,
        client_factory=factory,
    )


def _registry_gateway(service: DummyNodeRegistryService) -> NodeRegistryGatewayClient:
    raw_client = cast(NodeRegistryClient, DummyClient())
    factory = cast(
        Callable[[Any], NodeRegistryClient],
        lambda raw: cast(NodeRegistryClient, service),
    )
    return NodeRegistryGatewayClient(
        base_url="http://registry",
        auth_client=_auth_client(),
        client=raw_client,
        client_factory=factory,
    )


class DummySelectionService:
    def __init__(self, response: CandidateSet | None = None, error: Exception | None = None) -> None:
        self._response = response
        self._error = error

    def generate_candidate_set(self, request) -> CandidateSet:
        _ = request
        if self._error:
            raise self._error
        assert self._response is not None
        return self._response

    def health(self, request) -> Health:
        _ = request
        if self._error:
            raise self._error
        return Health(status=Status.ok, time=datetime.now(timezone.utc))

    def version(self, request) -> VersionInfo:
        _ = request
        if self._error:
            raise self._error
        return VersionInfo(service_name="selection", service_version="0.0.0", supported_api_versions=["v1"])


class DummyNodeRegistryService:
    def __init__(self, response: NodeType | None = None, error: Exception | None = None) -> None:
        self._response = response
        self._error = error

    def get_node_type(self, request) -> NodeType:
        _ = request
        if self._error:
            raise self._error
        assert self._response is not None
        return self._response

    def health(self, request) -> Health:
        _ = request
        if self._error:
            raise self._error
        return Health(status=Status.ok, time=datetime.now(timezone.utc))

    def version(self, request) -> VersionInfo:
        _ = request
        if self._error:
            raise self._error
        return VersionInfo(service_name="registry", service_version="0.0.0", supported_api_versions=["v1"])


class DummyRunCoordinatorService:
    def __init__(self, response: NodeRunsCreateResponse | None = None, error: Exception | None = None) -> None:
        self._response = response
        self._error = error
        self.node_run = NodeRun(
            node_run_id="nr-1",
            node_type_ref=NodeTypeRef(node_type_id="node", version="1"),
            state=NodeRunState.succeeded,
            run_id="run-1",
        )
        self.completed: list[object] = []
        self.reported: list[object] = []

    def create_node_runs(self, request) -> NodeRunsCreateResponse:
        _ = request
        if self._error:
            raise self._error
        assert self._response is not None
        return self._response

    def health(self, request):
        _ = request
        if self._error:
            raise self._error
        return Health(status=Status.ok, time=datetime.now(timezone.utc))

    def version(self, request):
        _ = request
        if self._error:
            raise self._error
        return VersionInfo(service_name="svc", service_version="0.0.0", supported_api_versions=["v1"])

    def get_node_run(self, request) -> NodeRun:
        _ = request
        if self._error:
            raise self._error
        return self.node_run

    def complete_node_run(self, request) -> None:
        if self._error:
            raise self._error
        self.completed.append(request)
        return None

    def report_node_run_evaluation(self, request) -> None:
        if self._error:
            raise self._error
        self.reported.append(request)
        return None

    def stream_node_run_events(self, request) -> str:
        _ = request
        if self._error:
            raise self._error
        return "stream"


def test_selection_gateway_success() -> None:
    candidate_set = CandidateSet(
        candidate_set_id="set-1",
        subtask_id="subtask-1",
        candidates=[],
        top_k=1,
    )
    gateway = _selection_gateway(DummySelectionService(response=candidate_set))

    subtask = SubtaskSpec(subtask_id="subtask-1", goal="do")
    result = asyncio.run(gateway.generate_candidate_set(CandidateSetRequest(subtask_spec=subtask)))

    assert result.candidate_set_id == "set-1"


def test_selection_gateway_arp_error() -> None:
    gateway = _selection_gateway(
        DummySelectionService(error=ArpApiError(code="bad", message="nope", status_code=400))
    )

    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(gateway.generate_candidate_set(CandidateSetRequest(subtask_spec=SubtaskSpec(subtask_id="s", goal="g"))))

    assert excinfo.value.code == "bad"
    assert excinfo.value.status_code == 400


def test_selection_gateway_unavailable() -> None:
    gateway = _selection_gateway(DummySelectionService(error=RuntimeError("boom")))

    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(gateway.generate_candidate_set(CandidateSetRequest(subtask_spec=SubtaskSpec(subtask_id="s", goal="g"))))

    assert excinfo.value.code == "selection_service_unavailable"


def test_selection_gateway_health_and_version() -> None:
    gateway = _selection_gateway(
        DummySelectionService(response=CandidateSet(candidate_set_id="s", subtask_id="t", candidates=[]))
    )

    health = asyncio.run(gateway.health())
    version = asyncio.run(gateway.version())

    assert health.status == Status.ok
    assert version.service_name == "selection"


def test_node_registry_gateway_success() -> None:
    node_type = NodeType(
        node_type_id="node",
        version="1",
        kind=NodeKind.atomic,
        description=None,
        input_schema=None,
    )
    gateway = _registry_gateway(DummyNodeRegistryService(response=node_type))

    result = asyncio.run(gateway.get_node_type("node", "1"))

    assert result.node_type_id == "node"


def test_node_registry_gateway_arp_error() -> None:
    gateway = _registry_gateway(
        DummyNodeRegistryService(error=ArpApiError(code="missing", message="no", status_code=404))
    )

    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(gateway.get_node_type("node", "1"))

    assert excinfo.value.code == "missing"
    assert excinfo.value.status_code == 404


def test_node_registry_gateway_unavailable() -> None:
    gateway = _registry_gateway(DummyNodeRegistryService(error=RuntimeError("boom")))

    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(gateway.get_node_type("node", "1"))

    assert excinfo.value.code == "node_registry_unavailable"


def test_node_registry_gateway_health_and_version() -> None:
    gateway = _registry_gateway(
        DummyNodeRegistryService(
            response=NodeType(node_type_id="node", version="1", kind=NodeKind.atomic, description=None, input_schema=None)
        )
    )

    health = asyncio.run(gateway.health())
    version = asyncio.run(gateway.version())

    assert health.status == Status.ok
    assert version.service_name == "registry"


def test_run_coordinator_gateway_success() -> None:
    node_run = NodeRun(
        node_run_id="nr-1",
        node_type_ref=NodeTypeRef(node_type_id="node", version="1"),
        state=NodeRunState.succeeded,
        run_id="run-1",
    )
    response = NodeRunsCreateResponse(node_runs=[node_run])
    gateway = RunCoordinatorGatewayClient(
        base_url="http://coordinator",
        bearer_token="token",
        client=cast(RunCoordinatorClient, DummyRunCoordinatorService(response=response)),
    )

    spec = NodeRunCreateSpec(node_type_ref=node_run.node_type_ref, inputs={"goal": "test"})
    result = asyncio.run(
        gateway.create_node_runs(
            NodeRunsCreateRequest(run_id="run-1", parent_node_run_id="p", node_runs=[spec])
        )
    )

    assert result.node_runs[0].node_run_id == "nr-1"


def test_run_coordinator_gateway_arp_error() -> None:
    gateway = RunCoordinatorGatewayClient(
        base_url="http://coordinator",
        bearer_token="token",
        client=cast(
            RunCoordinatorClient,
            DummyRunCoordinatorService(error=ArpApiError(code="bad", message="no", status_code=500)),
        ),
    )

    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(gateway.health())

    assert excinfo.value.code == "bad"
    assert excinfo.value.status_code == 500


def test_run_coordinator_gateway_unavailable() -> None:
    gateway = RunCoordinatorGatewayClient(
        base_url="http://coordinator",
        bearer_token="token",
        client=cast(RunCoordinatorClient, DummyRunCoordinatorService(error=RuntimeError("boom"))),
    )

    with pytest.raises(ArpServerError) as excinfo:
        asyncio.run(gateway.version())

    assert excinfo.value.code == "run_coordinator_unavailable"


def test_run_coordinator_gateway_methods() -> None:
    coordinator = DummyRunCoordinatorService(
        response=NodeRunsCreateResponse(
            node_runs=[
                NodeRun(
                    node_run_id="nr-2",
                    node_type_ref=NodeTypeRef(node_type_id="node", version="1"),
                    state=NodeRunState.succeeded,
                    run_id="run-1",
                )
            ]
        )
    )
    gateway = RunCoordinatorGatewayClient(
        base_url="http://coordinator",
        bearer_token="token",
        client=cast(RunCoordinatorClient, coordinator),
    )

    spec = NodeRunCreateSpec(node_type_ref=NodeTypeRef(node_type_id="node", version="1"), inputs={"goal": "x"})
    asyncio.run(gateway.create_node_runs(NodeRunsCreateRequest(run_id="run-1", parent_node_run_id="p", node_runs=[spec])))
    asyncio.run(gateway.get_node_run("nr-1"))
    asyncio.run(gateway.complete_node_run("nr-1", NodeRunCompleteRequest(state=NodeRunTerminalState.succeeded)))
    asyncio.run(
        gateway.report_node_run_evaluation(
            "nr-1",
            NodeRunEvaluationReportRequest(evaluation_result=EvaluationResult(status=EvaluationStatus.success)),
        )
    )
    assert asyncio.run(gateway.stream_node_run_events("nr-1")) == "stream"
