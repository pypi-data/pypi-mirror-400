import asyncio

from arp_llm.providers.dev_mock import DevMockChatFixture, DevMockChatModel
from arp_standard_model import CompositeBeginRequest, EndpointLocator, NodeTypeRef
from jarvis_composite_executor.config import CompositeConfig
from jarvis_composite_executor.engine.arggen import ArgGen
from jarvis_composite_executor.engine.driver import CompositeAssignmentDriver
from jarvis_composite_executor.engine.planner import Planner

from .fakes import FakeNodeRegistry, FakeRunCoordinator, FakeSelection, make_candidate_set, make_node_type


def test_driver_runs_sequential_flow() -> None:
    planner_fixture = DevMockChatFixture(
        text="planner",
        parsed={"subtasks": [{"subtask_id": "s1", "goal": "do thing", "notes": None}], "summary": None},
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
    candidate_ref = NodeTypeRef(node_type_id="jarvis.core.echo", version="0.3.7")
    selection = FakeSelection(make_candidate_set(candidate=candidate_ref))
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

    driver = CompositeAssignmentDriver(
        run_coordinator=run_coordinator,
        selection=selection,
        node_registry=node_registry,
        planner=Planner(llm),
        arggen=ArgGen(llm, max_retries=0),
        config=config,
        canceled=set(),
    )

    request = CompositeBeginRequest(
        run_id="run_1",
        node_run_id="node_run_1",
        node_type_ref=NodeTypeRef(node_type_id="jarvis.composite.planner", version="0.3.7"),
        inputs={"goal": "test"},
        coordinator_endpoint=EndpointLocator.model_validate("http://127.0.0.1:8081"),
    )

    asyncio.run(driver.run(request))

    assert len(run_coordinator.created) == 1
    assert len(run_coordinator.completed) == 1
