import asyncio

from arp_llm.providers.dev_mock import DevMockChatFixture, DevMockChatModel
from arp_standard_model import (
    CompositeBeginRequest,
    CompositeExecutorBeginCompositeNodeRunRequest,
    EndpointLocator,
    NodeTypeRef,
)
from jarvis_composite_executor.config import CompositeConfig
from jarvis_composite_executor.executor import CompositeExecutor

from .fakes import FakeNodeRegistry, FakeRunCoordinator, FakeSelection, make_candidate_set, make_node_type


def test_begin_composite_node_run_accepts() -> None:
    planner_fixture = DevMockChatFixture(
        text="planner",
        parsed={
            "subtasks": [{"subtask_id": "s1", "goal": "do thing", "notes": None}],
            "summary": None,
        },
    )
    arggen_fixture = DevMockChatFixture(text="arggen", parsed={"text": "hello"})
    llm = DevMockChatModel(fixtures=[planner_fixture, arggen_fixture])

    node_type = make_node_type(
        node_type_id="jarvis.core.echo",
        version="0.3.7",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
    )
    candidate_set = make_candidate_set(candidate=NodeTypeRef(node_type_id="jarvis.core.echo", version="0.3.7"))
    selection = FakeSelection(candidate_set)
    node_registry = FakeNodeRegistry(node_type)
    run_coordinator = FakeRunCoordinator()
    config = CompositeConfig(
        max_steps_default=3,
        max_depth_default=2,
        poll_timeout_sec=1.0,
        poll_interval_sec=0.01,
        arggen_max_retries=0,
        context_window=None,
        max_concurrency=None,
    )

    executor = CompositeExecutor(
        selection_service=selection,
        node_registry=node_registry,
        llm=llm,
        config=config,
        run_coordinator_factory=lambda _: run_coordinator,
    )
    request = CompositeExecutorBeginCompositeNodeRunRequest(
        body=CompositeBeginRequest(
            run_id="run_1",
            node_run_id="node_run_1",
            node_type_ref=NodeTypeRef(node_type_id="jarvis.composite.planner", version="0.3.7"),
            inputs={"goal": "test"},
            coordinator_endpoint=EndpointLocator.model_validate("http://127.0.0.1:8081"),
        )
    )

    result = asyncio.run(executor.begin_composite_node_run(request))

    assert result.accepted is True
