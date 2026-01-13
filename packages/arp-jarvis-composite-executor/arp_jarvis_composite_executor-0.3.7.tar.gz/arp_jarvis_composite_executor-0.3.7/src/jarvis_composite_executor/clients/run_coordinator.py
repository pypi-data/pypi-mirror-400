from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

from arp_standard_client.errors import ArpApiError
from arp_standard_client.run_coordinator import RunCoordinatorClient
from arp_standard_model import (
    Health,
    NodeRun,
    NodeRunCompleteRequest,
    NodeRunEvaluationReportRequest,
    NodeRunsCreateRequest,
    NodeRunsCreateResponse,
    RunCoordinatorCompleteNodeRunParams,
    RunCoordinatorCompleteNodeRunRequest,
    RunCoordinatorCreateNodeRunsRequest,
    RunCoordinatorGetNodeRunParams,
    RunCoordinatorGetNodeRunRequest,
    RunCoordinatorHealthRequest,
    RunCoordinatorReportNodeRunEvaluationParams,
    RunCoordinatorReportNodeRunEvaluationRequest,
    RunCoordinatorStreamNodeRunEventsParams,
    RunCoordinatorStreamNodeRunEventsRequest,
    RunCoordinatorVersionRequest,
    VersionInfo,
)
from arp_standard_server import ArpServerError

T = TypeVar("T")


class RunCoordinatorGatewayClient:
    """Outgoing Run Coordinator client wrapper for the Composite Executor."""

    def __init__(
        self,
        *,
        base_url: str,
        bearer_token: str | None = None,
        client: RunCoordinatorClient | None = None,
    ) -> None:
        self.base_url = base_url
        self._client = client or RunCoordinatorClient(base_url=base_url, bearer_token=bearer_token)

    async def create_node_runs(self, body: NodeRunsCreateRequest) -> NodeRunsCreateResponse:
        return await self._call(
            self._client.create_node_runs,
            RunCoordinatorCreateNodeRunsRequest(body=body),
        )

    async def get_node_run(self, node_run_id: str) -> NodeRun:
        return await self._call(
            self._client.get_node_run,
            RunCoordinatorGetNodeRunRequest(params=RunCoordinatorGetNodeRunParams(node_run_id=node_run_id)),
        )

    async def complete_node_run(self, node_run_id: str, body: NodeRunCompleteRequest) -> None:
        return await self._call(
            self._client.complete_node_run,
            RunCoordinatorCompleteNodeRunRequest(
                params=RunCoordinatorCompleteNodeRunParams(node_run_id=node_run_id),
                body=body,
            ),
        )

    async def report_node_run_evaluation(self, node_run_id: str, body: NodeRunEvaluationReportRequest) -> None:
        return await self._call(
            self._client.report_node_run_evaluation,
            RunCoordinatorReportNodeRunEvaluationRequest(
                params=RunCoordinatorReportNodeRunEvaluationParams(node_run_id=node_run_id),
                body=body,
            ),
        )

    async def stream_node_run_events(self, node_run_id: str) -> str:
        return await self._call(
            self._client.stream_node_run_events,
            RunCoordinatorStreamNodeRunEventsRequest(
                params=RunCoordinatorStreamNodeRunEventsParams(node_run_id=node_run_id)
            ),
        )

    async def health(self) -> Health:
        return await self._call(
            self._client.health,
            RunCoordinatorHealthRequest(),
        )

    async def version(self) -> VersionInfo:
        return await self._call(
            self._client.version,
            RunCoordinatorVersionRequest(),
        )

    async def _call(self, fn: Callable[[Any], T], request: Any) -> T:
        try:
            return await asyncio.to_thread(fn, request)
        except ArpApiError as exc:
            raise ArpServerError(
                code=exc.code,
                message=exc.message,
                status_code=exc.status_code or 502,
                details=exc.details,
            ) from exc
        except Exception as exc:
            raise ArpServerError(
                code="run_coordinator_unavailable",
                message="Run Coordinator request failed",
                status_code=502,
                details={
                    "run_coordinator_url": self.base_url,
                    "error": str(exc),
                },
            ) from exc
