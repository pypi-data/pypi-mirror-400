import asyncio

from arp_standard_model import (
    AtomicExecuteRequest,
    AtomicExecutorCancelAtomicNodeRunParams,
    AtomicExecutorCancelAtomicNodeRunRequest,
    AtomicExecutorExecuteAtomicNodeRunRequest,
    NodeRunState,
    NodeTypeRef,
)
from jarvis_atomic_executor.executor import AtomicExecutor


def test_execute_atomic_echo() -> None:
    executor = AtomicExecutor()
    request = AtomicExecutorExecuteAtomicNodeRunRequest(
        body=AtomicExecuteRequest(
            node_run_id="node_run_1",
            run_id="run_1",
            node_type_ref=NodeTypeRef(node_type_id="jarvis.core.echo", version="0.3.7"),
            inputs={"echo": "pong"},
        )
    )

    result = asyncio.run(executor.execute_atomic_node_run(request))

    assert result.state == NodeRunState.succeeded
    assert result.outputs == {"echo": "pong"}


def test_execute_atomic_unknown_node_type() -> None:
    executor = AtomicExecutor()
    request = AtomicExecutorExecuteAtomicNodeRunRequest(
        body=AtomicExecuteRequest(
            node_run_id="node_run_unknown",
            run_id="run_1",
            node_type_ref=NodeTypeRef(node_type_id="atomic.unknown", version="0.1.0"),
            inputs={"ping": "pong"},
        )
    )

    result = asyncio.run(executor.execute_atomic_node_run(request))

    assert result.state == NodeRunState.failed
    assert result.error is not None
    assert result.error.code == "unknown_node_type"


def test_cancel_atomic_node_run_cancels_in_flight_execution() -> None:
    started = asyncio.Event()

    async def slow_handler(_: AtomicExecuteRequest) -> dict[str, object]:
        started.set()
        await asyncio.sleep(10)
        return {"ok": True}

    executor = AtomicExecutor(handlers={"atomic.slow": slow_handler})
    execute_request = AtomicExecutorExecuteAtomicNodeRunRequest(
        body=AtomicExecuteRequest(
            node_run_id="node_run_cancel",
            run_id="run_1",
            node_type_ref=NodeTypeRef(node_type_id="atomic.slow", version="0.1.0"),
            inputs={},
        )
    )
    cancel_request = AtomicExecutorCancelAtomicNodeRunRequest(
        params=AtomicExecutorCancelAtomicNodeRunParams(node_run_id="node_run_cancel")
    )

    async def _run() -> NodeRunState:
        task = asyncio.create_task(executor.execute_atomic_node_run(execute_request))
        await started.wait()
        await executor.cancel_atomic_node_run(cancel_request)
        result = await task
        return result.state

    assert asyncio.run(_run()) == NodeRunState.canceled


def test_execute_timeout_returns_failed() -> None:
    started = asyncio.Event()

    async def slow_handler(_: AtomicExecuteRequest) -> dict[str, object]:
        started.set()
        await asyncio.sleep(10)
        return {"ok": True}

    executor = AtomicExecutor(handlers={"atomic.slow": slow_handler}, default_timeout_seconds=0.01)
    execute_request = AtomicExecutorExecuteAtomicNodeRunRequest(
        body=AtomicExecuteRequest(
            node_run_id="node_run_timeout",
            run_id="run_1",
            node_type_ref=NodeTypeRef(node_type_id="atomic.slow", version="0.1.0"),
            inputs={},
        )
    )

    async def _run() -> tuple[NodeRunState, str | None]:
        result = await executor.execute_atomic_node_run(execute_request)
        return result.state, None if result.error is None else result.error.code

    state, error_code = asyncio.run(_run())
    assert state == NodeRunState.failed
    assert error_code == "timeout"
