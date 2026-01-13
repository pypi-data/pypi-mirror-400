from __future__ import annotations

import asyncio

from .future import WolvesFuture
from .runtime import AsyncRuntime
from .types import WolvesEvent


# Global map of EventLoggers by sdk_key.
# This ensures events can still be sent even after a client is destroyed,
# as long as there are pending events in the queue.
_EVENT_LOGGER_MAP: dict[str, EventLogger] = {}


class EventLogger:
    def __init__(
        self,
        sdk_key: str,
        network: object,
        runtime: AsyncRuntime,
        *,
        max_queue_size: int = 100,
        flush_interval_s: float = 10.0,
    ) -> None:
        self._sdk_key = sdk_key
        self._network = network
        self._runtime = runtime
        self._max_queue_size = max_queue_size
        self._flush_interval_s = flush_interval_s

        self._queue: list[WolvesEvent] = []
        self._periodic_task: asyncio.Task[None] | None = None
        self._flush_lock: asyncio.Lock | None = None
        self._stopped = False
        self._last_flush_success: bool | None = None

        self._runtime.submit(self._start())

    def enqueue(self, event: WolvesEvent) -> None:
        self._runtime.submit(self._enqueue(event))

    def flush(self) -> WolvesFuture[None]:
        return self._runtime.submit(self._flush())

    def stop(self) -> WolvesFuture[None]:
        return self._runtime.submit(self._stop())

    async def _start(self) -> None:
        if self._periodic_task is not None:
            return
        if self._flush_lock is None:
            self._flush_lock = asyncio.Lock()

        # If there's an existing logger with the same sdk_key, flush it first
        existing_logger = _EVENT_LOGGER_MAP.get(self._sdk_key)
        if existing_logger is not None and existing_logger is not self:
            # Stop the old logger's periodic task
            if existing_logger._periodic_task is not None:
                existing_logger._periodic_task.cancel()
                try:
                    await existing_logger._periodic_task
                except asyncio.CancelledError:
                    pass
                existing_logger._periodic_task = None
            # Flush remaining events from the old logger
            try:
                await existing_logger._flush()
            except Exception:
                pass  # noop - errors already handled in flush

        # Register this logger in the global map (replaces any existing)
        _EVENT_LOGGER_MAP[self._sdk_key] = self

        self._periodic_task = asyncio.create_task(self._periodic_flush())

    async def _periodic_flush(self) -> None:
        while True:
            await asyncio.sleep(self._flush_interval_s)
            await asyncio.shield(self._flush())

    async def _enqueue(self, event: WolvesEvent) -> None:
        if self._stopped:
            return
        self._queue.append(event)
        if len(self._queue) >= self._max_queue_size:
            asyncio.create_task(self._flush())

    async def _flush(self) -> None:
        if self._flush_lock is None:
            self._flush_lock = asyncio.Lock()

        async with self._flush_lock:
            if not self._queue:
                return

            events = list(self._queue)
            self._queue.clear()

            try:
                send_events = getattr(self._network, "send_events")
                await send_events(events)
                self._last_flush_success = True
            except Exception:
                self._last_flush_success = False
                self._queue[:0] = events
                if len(self._queue) > self._max_queue_size:
                    self._queue = self._queue[len(self._queue) - self._max_queue_size :]

    async def _stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True

        if self._periodic_task is not None:
            self._periodic_task.cancel()
            try:
                await self._periodic_task
            except asyncio.CancelledError:
                pass
            self._periodic_task = None

        # Flush all pending events before stopping
        await self._flush()

        # Remove from global map after ensuring all events are sent
        _EVENT_LOGGER_MAP.pop(self._sdk_key, None)
