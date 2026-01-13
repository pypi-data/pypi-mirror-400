from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine, Mapping
from contextlib import suppress
import logging
import os
from typing import Any

from arp_standard_model import (
    AtomicExecuteRequest,
    AtomicExecuteResult,
    AtomicExecutorCancelAtomicNodeRunRequest,
    AtomicExecutorExecuteAtomicNodeRunRequest,
    AtomicExecutorHealthRequest,
    AtomicExecutorVersionRequest,
    Error,
    Health,
    NodeRunState,
    Status,
    VersionInfo,
)
from arp_standard_server.atomic_executor import BaseAtomicExecutorServer

from jarvis_atomic_nodes.discovery import load_handlers

from . import __version__
from .utils import now

logger = logging.getLogger(__name__)

AtomicHandler = Callable[[AtomicExecuteRequest], Coroutine[Any, Any, dict[str, object]]]


class AtomicExecutor(BaseAtomicExecutorServer):
    """Atomic execution surface; implement your node logic here."""

    # Core method - API surface and main extension points
    def __init__(
        self,
        *,
        service_name: str = "jarvis-atomic-executor",
        service_version: str = __version__,
        handlers: Mapping[str, AtomicHandler] | None = None,
        default_timeout_seconds: float | None = None,
        max_concurrency: int | None = None,
    ) -> None:
        """
        Not part of ARP spec; required to construct the executor.

        Args:
          - service_name: Name exposed by /v1/version.
          - service_version: Version exposed by /v1/version.
          - handlers: Registry mapping `node_type_id` → async handler.
          - default_timeout_seconds: Optional coarse timeout per execution.
          - max_concurrency: Optional cap on concurrent executions.

        Potential modifications:
          - Inject dependencies needed by your atomic handlers.
          - Add persistence or tracing helpers.
        """
        # Service identity (reported via `/v1/version`).
        self._service_name = service_name
        self._service_version = service_version

        # Handler registry: `node_type_id` → coroutine handler.
        # Default: load installed node packs via entry points.
        if handlers is not None:
            self._handlers = dict(handlers)
        else:
            self._handlers = dict(load_handlers())
            if not self._handlers:
                self._handlers = {"jarvis.core.echo": self._handle_echo}

        # Optional execution controls (coarse): timeout + concurrency cap.
        self._default_timeout_seconds = default_timeout_seconds
        if self._default_timeout_seconds is None:
            self._default_timeout_seconds = _env_float("JARVIS_DEFAULT_TIMEOUT_SECS")
        max_concurrency_value = max_concurrency or _env_int("JARVIS_MAX_CONCURRENCY")
        self._semaphore: asyncio.Semaphore | None = None
        if max_concurrency_value is not None and max_concurrency_value > 0:
            self._semaphore = asyncio.Semaphore(max_concurrency_value)

        # In-flight task registry, used to implement best-effort cancellation.
        self._tasks: dict[str, asyncio.Task[dict[str, object]]] = {}
        logger.info(
            "Atomic Executor ready (handlers=%s, default_timeout=%s, max_concurrency=%s)",
            len(self._handlers),
            self._default_timeout_seconds,
            max_concurrency_value,
        )

    # Core methods - Atomic Executor API implementations
    async def health(self, request: AtomicExecutorHealthRequest) -> Health:
        """
        Mandatory: Required by the ARP Atomic Executor API.

        Args:
          - request: AtomicExecutorHealthRequest (unused).
        """
        _ = request
        return Health(status=Status.ok, time=now())

    async def version(self, request: AtomicExecutorVersionRequest) -> VersionInfo:
        """
        Mandatory: Required by the ARP Atomic Executor API.

        Args:
          - request: AtomicExecutorVersionRequest (unused).
        """
        _ = request
        return VersionInfo(
            service_name=self._service_name,
            service_version=self._service_version,
            supported_api_versions=["v1"],
        )

    async def execute_atomic_node_run(self, request: AtomicExecutorExecuteAtomicNodeRunRequest) -> AtomicExecuteResult:
        """
        Mandatory: Required by the ARP Atomic Executor API.

        Args:
          - request: AtomicExecutorExecuteAtomicNodeRunRequest with NodeRun inputs.

        Potential modifications:
          - Add routing to different handlers by node_type_id.
          - Enforce budgets/constraints before execution.
          - Emit richer outputs or artifacts.
        """
        # Capture execution timing for the result envelope.
        started_at = now()
        node_run_id = request.body.node_run_id

        # Resolve the requested node type to an in-process handler.
        node_type_id = request.body.node_type_ref.node_type_id
        logger.info(
            "Atomic execute requested (run_id=%s, node_run_id=%s, node_type_id=%s)",
            request.body.run_id,
            node_run_id,
            node_type_id,
        )
        if (handler := self._handlers.get(node_type_id)) is None:
            logger.warning(
                "Atomic execute failed (node_run_id=%s, node_type_id=%s, reason=unknown_node_type)",
                node_run_id,
                node_type_id,
            )
            return AtomicExecuteResult(
                node_run_id=node_run_id,
                state=NodeRunState.failed,
                outputs=None,
                output_artifacts=None,
                started_at=started_at,
                ended_at=now(),
                error=Error(code="unknown_node_type", message=f"Unknown node_type_id: {node_type_id}"),
            )

        # Apply an optional concurrency cap. If not configured, run immediately.
        semaphore = self._semaphore
        if semaphore is None:
            return await self._execute(handler=handler, request=request.body, started_at=started_at)
        async with semaphore:
            return await self._execute(handler=handler, request=request.body, started_at=started_at)

    async def _execute(
        self,
        *,
        handler: AtomicHandler,
        request: AtomicExecuteRequest,
        started_at,
    ) -> AtomicExecuteResult:
        node_run_id = request.node_run_id

        # Run the handler in a task so `cancel_atomic_node_run` can cancel it.
        task = asyncio.create_task(handler(request))
        self._tasks[node_run_id] = task
        try:
            # Optional coarse timeout (best-effort). Timeouts become `failed`.
            if (timeout := self._default_timeout_seconds) is not None and timeout > 0:
                outputs = await asyncio.wait_for(task, timeout=timeout)
            else:
                outputs = await task
            logger.info("Atomic execute succeeded (node_run_id=%s)", node_run_id)
            return AtomicExecuteResult(
                node_run_id=node_run_id,
                state=NodeRunState.succeeded,
                outputs=outputs,
                output_artifacts=None,
                started_at=started_at,
                ended_at=now(),
                error=None,
            )
        except asyncio.TimeoutError:
            # Best-effort: cancel the handler task and wait for cancellation to propagate.
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            logger.warning("Atomic execute timed out (node_run_id=%s)", node_run_id)
            return AtomicExecuteResult(
                node_run_id=node_run_id,
                state=NodeRunState.failed,
                outputs=None,
                output_artifacts=None,
                started_at=started_at,
                ended_at=now(),
                error=Error(code="timeout", message="Atomic execution timed out"),
            )
        except asyncio.CancelledError:
            # Cancellation can happen via the cancel endpoint or server shutdown.
            logger.warning("Atomic execute canceled (node_run_id=%s)", node_run_id)
            return AtomicExecuteResult(
                node_run_id=node_run_id,
                state=NodeRunState.canceled,
                outputs=None,
                output_artifacts=None,
                started_at=started_at,
                ended_at=now(),
                error=Error(code="canceled", message="Atomic execution canceled"),
            )
        except Exception:
            # Avoid leaking internal details in the response; use logs for diagnostics.
            logger.exception("Atomic handler failed")
            return AtomicExecuteResult(
                node_run_id=node_run_id,
                state=NodeRunState.failed,
                outputs=None,
                output_artifacts=None,
                started_at=started_at,
                ended_at=now(),
                error=Error(code="handler_error", message="Atomic handler failed"),
            )
        finally:
            # Always clear the in-flight task registry entry.
            self._tasks.pop(node_run_id, None)

    async def cancel_atomic_node_run(self, request: AtomicExecutorCancelAtomicNodeRunRequest) -> None:
        """
        Mandatory: Required by the ARP Atomic Executor API.

        Args:
          - request: AtomicExecutorCancelAtomicNodeRunRequest with node_run_id.

        Potential modifications:
          - Add cooperative cancellation to your executor implementation.
        """
        # Best-effort cancellation: cancel the task if it's in-flight; otherwise no-op.
        node_run_id = request.params.node_run_id
        if (task := self._tasks.get(node_run_id)) is not None:
            task.cancel()
            logger.info("Atomic execute cancellation requested (node_run_id=%s)", node_run_id)
        return None

    async def _handle_echo(self, request: AtomicExecuteRequest) -> dict[str, object]:
        # Deterministic baseline handler used for smoke tests and conformance.
        return {"echo": request.inputs}


def _env_int(name: str) -> int | None:
    # Returns `None` if unset/invalid/non-positive (treat as "disabled").
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if value > 0 else None


def _env_float(name: str) -> float | None:
    # Returns `None` if unset/invalid/non-positive (treat as "disabled").
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    return value if value > 0 else None
