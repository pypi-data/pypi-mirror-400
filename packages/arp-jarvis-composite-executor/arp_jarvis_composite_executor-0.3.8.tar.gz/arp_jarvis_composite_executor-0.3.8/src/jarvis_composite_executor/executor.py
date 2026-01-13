from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from arp_llm.types import ChatModel
from arp_standard_model import (
    CompositeBeginRequest,
    CompositeBeginResponse,
    CompositeExecutorBeginCompositeNodeRunRequest,
    CompositeExecutorCancelCompositeNodeRunRequest,
    CompositeExecutorHealthRequest,
    CompositeExecutorVersionRequest,
    Error,
    Health,
    NodeRunCompleteRequest,
    NodeRunTerminalState,
    Status,
    VersionInfo,
)
from arp_standard_server import ArpServerError
from arp_standard_server.composite_executor import BaseCompositeExecutorServer

from . import __version__
from .clients import (
    NodeRegistryClientLike,
    RunCoordinatorClientLike,
    RunCoordinatorGatewayClient,
    SelectionClientLike,
)
from .config import CompositeConfig
from .engine import ArgGen, CompositeAssignmentDriver, Planner
from .utils import normalize_base_url, now

logger = logging.getLogger(__name__)


class CompositeExecutor(BaseCompositeExecutorServer):
    """Composite execution surface; plug your composite engine here."""

    # Core method - API surface and main extension points
    def __init__(
        self,
        *,
        service_name: str = "arp-jarvis-composite-executor",
        service_version: str = __version__,
        selection_service: SelectionClientLike | None = None,
        node_registry: NodeRegistryClientLike | None = None,
        llm: ChatModel | None = None,
        config: CompositeConfig | None = None,
        run_coordinator_factory: Callable[[CompositeBeginRequest], RunCoordinatorClientLike] | None = None,
    ) -> None:
        """
        Not part of ARP spec; required to construct the executor.

        Args:
          - service_name: Name exposed by /v1/version.
          - service_version: Version exposed by /v1/version.
          - run_coordinator: Optional wrapper for Run Coordinator calls.
          - selection_service: Optional wrapper for Selection Service calls.

        Potential modifications:
          - Inject your composite planner/executor implementation.
          - Add background task orchestration or queues.
        """
        self._service_name = service_name
        self._service_version = service_version
        self._selection_service = selection_service
        self._node_registry = node_registry
        self._llm = llm
        self._config = config
        self._run_coordinator_factory = run_coordinator_factory
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._canceled: set[str] = set()
        self._semaphore = None
        if config and config.max_concurrency and config.max_concurrency > 0:
            self._semaphore = asyncio.Semaphore(config.max_concurrency)

    # Core methods - Composite Executor API implementations
    async def health(self, request: CompositeExecutorHealthRequest) -> Health:
        """
        Mandatory: Required by the ARP Composite Executor API.

        Args:
          - request: CompositeExecutorHealthRequest (unused).
        """
        _ = request
        return Health(status=Status.ok, time=now())

    async def version(self, request: CompositeExecutorVersionRequest) -> VersionInfo:
        """
        Mandatory: Required by the ARP Composite Executor API.

        Args:
          - request: CompositeExecutorVersionRequest (unused).
        """
        _ = request
        return VersionInfo(
            service_name=self._service_name,
            service_version=self._service_version,
            supported_api_versions=["v1"],
        )

    async def begin_composite_node_run(
        self, request: CompositeExecutorBeginCompositeNodeRunRequest
    ) -> CompositeBeginResponse:
        """
        Mandatory: Required by the ARP Composite Executor API.

        Args:
          - request: CompositeExecutorBeginCompositeNodeRunRequest with assignment info.

        Potential modifications:
          - Kick off background execution and return accepted=true.
          - Validate constraints before accepting.
        """
        self._ensure_ready()
        logger.info(
            "Composite assignment received (run_id=%s, node_run_id=%s, node_type_id=%s)",
            request.body.run_id,
            request.body.node_run_id,
            request.body.node_type_ref.node_type_id,
        )
        self._start_assignment(request.body)
        return CompositeBeginResponse(
            accepted=True,
            message="Composite assignment accepted (JARVIS).",
        )

    async def cancel_composite_node_run(self, request: CompositeExecutorCancelCompositeNodeRunRequest) -> None:
        """
        Mandatory: Required by the ARP Composite Executor API.

        Args:
          - request: CompositeExecutorCancelCompositeNodeRunRequest with node_run_id.

        Potential modifications:
          - Add cooperative cancellation to your composite executor implementation.
        """
        node_run_id = request.params.node_run_id
        self._canceled.add(node_run_id)
        task = self._tasks.pop(node_run_id, None)
        if task is not None:
            task.cancel()
            logger.info("Composite cancel requested (node_run_id=%s)", node_run_id)
        return None

    def _start_assignment(self, request: CompositeBeginRequest) -> None:
        node_run_id = request.node_run_id
        if node_run_id in self._tasks:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self._drive_assignment(request))
            return
        task = loop.create_task(self._drive_assignment(request))
        task.add_done_callback(lambda _: self._tasks.pop(node_run_id, None))
        self._tasks[node_run_id] = task

    async def _drive_assignment(self, request: CompositeBeginRequest) -> None:
        node_run_id = request.node_run_id
        if node_run_id in self._canceled:
            return
        selection = self._selection_service
        node_registry = self._node_registry
        llm = self._llm
        config = self._config
        if selection is None or node_registry is None or llm is None or config is None:
            logger.error("Composite assignment missing dependencies (node_run_id=%s)", node_run_id)
            return
        run_coordinator = (
            self._run_coordinator_factory(request)
            if self._run_coordinator_factory
            else RunCoordinatorGatewayClient(
                base_url=normalize_base_url(str(request.coordinator_endpoint.root)),
                bearer_token=request.assignment_token,
            )
        )
        try:
            driver = CompositeAssignmentDriver(
                run_coordinator=run_coordinator,
                selection=selection,
                node_registry=node_registry,
                planner=Planner(llm),
                arggen=ArgGen(llm, max_retries=config.arggen_max_retries),
                config=config,
                canceled=self._canceled,
            )
            await _maybe_await(self._semaphore, driver.run(request))
            logger.info("Composite assignment completed (node_run_id=%s)", node_run_id)
        except asyncio.CancelledError:
            try:
                await run_coordinator.complete_node_run(
                    node_run_id,
                    NodeRunCompleteRequest(state=NodeRunTerminalState.canceled),
                )
            except Exception:
                logger.exception("Unable to report composite cancellation")
            return
        except ArpServerError as exc:
            logger.exception("Composite assignment failed", exc_info=exc)
            await _report_failure(run_coordinator, node_run_id, exc)
        except Exception as exc:
            logger.exception("Composite assignment failed", exc_info=exc)
            await _report_failure(
                run_coordinator,
                node_run_id,
                ArpServerError(code="composite_error", message=str(exc), status_code=502),
            )

    def _ensure_ready(self) -> None:
        if self._selection_service is None:
            logger.error("Selection Service is not configured for Composite Executor")
            raise ArpServerError(
                code="selection_service_missing",
                message="Selection Service is required for composite execution",
                status_code=503,
            )
        if self._node_registry is None:
            logger.error("Node Registry is not configured for Composite Executor")
            raise ArpServerError(
                code="node_registry_missing",
                message="Node Registry is required for composite execution",
                status_code=503,
            )
        if self._llm is None:
            logger.error("LLM is not configured for Composite Executor")
            raise ArpServerError(
                code="composite_llm_missing",
                message="Composite Executor requires an LLM for planning and arg-gen",
                status_code=503,
            )
        if self._config is None:
            logger.error("Composite Executor config is not configured")
            raise ArpServerError(
                code="composite_config_missing",
                message="Composite Executor configuration is required",
                status_code=503,
            )


async def _report_failure(
    run_coordinator: RunCoordinatorClientLike,
    node_run_id: str,
    exc: ArpServerError,
) -> None:
    try:
        await run_coordinator.complete_node_run(
            node_run_id,
            NodeRunCompleteRequest(
                state=NodeRunTerminalState.failed,
                error=Error(code=exc.code, message=exc.message, details=exc.details),
            ),
        )
    except Exception:
        logger.exception("Unable to report composite failure")


async def _maybe_await(
    semaphore: asyncio.Semaphore | None,
    coro: Awaitable[None],
) -> None:
    if semaphore is None:
        await coro
        return
    async with semaphore:
        await coro
