import asyncio
from typing import Any, Protocol

from agent_observatory.internal.logging import log_internal_error

from .base import Exporter


class ExporterWorkerProtocol(Protocol):
    """
    Minimal protocol shared by all exporter workers.
    """

    def enqueue(self, payload: dict[str, Any]) -> None: ...


class AsyncExporterWorkerProtocol(ExporterWorkerProtocol, Protocol):
    """
    Protocol for async/background exporter workers.
    """

    async def start(self) -> None: ...
    async def stop(self) -> None: ...


class ExporterWorker:
    """
    Async, background exporter worker (production).
    """

    def __init__(self, exporter: Exporter, max_queue_size: int = 100) -> None:
        self._exporter = exporter
        self._queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=max_queue_size)
        self._task: asyncio.Task[None] | None = None
        self._running = False

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        while self._running:
            try:
                payload = await self._queue.get()
                self._exporter.export(payload)
            except asyncio.CancelledError:
                break
            except Exception as e:
                log_internal_error(f"export failed: {e}")

    def enqueue(self, payload: dict) -> None:
        try:
            self._queue.put_nowait(payload)
        except asyncio.QueueFull:
            log_internal_error("export queue full - dropping trace")


class InlineExporterWorker:
    """
    Synchronous exporter worker (inline mode).
    """

    def __init__(self, exporter: Exporter) -> None:
        self._exporter = exporter

    def enqueue(self, payload: dict) -> None:
        try:
            self._exporter.export(payload)
        except Exception as e:
            log_internal_error(f"inline export failed: {e}")
