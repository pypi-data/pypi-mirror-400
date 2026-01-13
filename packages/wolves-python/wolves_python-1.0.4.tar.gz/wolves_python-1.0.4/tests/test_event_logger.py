from __future__ import annotations

import asyncio
import threading
import time

from wolves_python.event_logger import EventLogger, _EVENT_LOGGER_MAP
from wolves_python.runtime import AsyncRuntime
from wolves_python.types import WolvesEvent, WolvesUser


class FakeNetwork:
    def __init__(self, *, fail_times: int = 0) -> None:
        self._lock = threading.Lock()
        self._fail_times = fail_times
        self.calls: list[list[str]] = []

    def set_fail_times(self, fail_times: int) -> None:
        with self._lock:
            self._fail_times = fail_times

    async def send_events(self, events: list[WolvesEvent]) -> None:
        await asyncio.sleep(0)
        with self._lock:
            self.calls.append([e.event_name for e in events])
            if self._fail_times > 0:
                self._fail_times -= 1
                raise RuntimeError("boom")


def _wait_until(predicate, *, timeout_s: float = 1.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    assert predicate()


def test_event_logger_flush_success() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    try:
        logger.enqueue(WolvesEvent(event_name="e1", user=WolvesUser(user_id="u"), time_ms=0))
        logger.flush().wait(timeout=2)
        _wait_until(lambda: len(network.calls) == 1)
        assert network.calls[0] == ["e1"]
        assert logger._last_flush_success is True  # type: ignore[attr-defined]
    finally:
        logger.stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_overflow_triggers_flush() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, max_queue_size=2, flush_interval_s=999)
    try:
        logger.enqueue(WolvesEvent(event_name="e1", user=None, time_ms=0))
        logger.enqueue(WolvesEvent(event_name="e2", user=None, time_ms=0))
        _wait_until(lambda: len(network.calls) == 1)
        assert network.calls[0] == ["e1", "e2"]
    finally:
        logger.stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_requeues_and_trims_on_failure() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork(fail_times=1)
    sdk_key = f"test-key-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, max_queue_size=2, flush_interval_s=999)
    try:
        async def seed_queue() -> None:
            logger._queue.extend(  # type: ignore[attr-defined]
                [
                    WolvesEvent(event_name="e1", user=None, time_ms=0),
                    WolvesEvent(event_name="e2", user=None, time_ms=0),
                    WolvesEvent(event_name="e3", user=None, time_ms=0),
                ]
            )

        runtime.submit(seed_queue()).wait(timeout=2)

        logger.flush().wait(timeout=2)
        _wait_until(lambda: len(network.calls) >= 1, timeout_s=2.0)
        assert network.calls[0] == ["e1", "e2", "e3"]
        assert logger._last_flush_success is False  # type: ignore[attr-defined]

        logger.flush().wait(timeout=2)
        _wait_until(lambda: len(network.calls) >= 2, timeout_s=2.0)
        assert network.calls[1] == ["e2", "e3"]
        assert logger._last_flush_success is True  # type: ignore[attr-defined]
    finally:
        logger.stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_periodic_flushes() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, flush_interval_s=0.05)
    try:
        logger.enqueue(WolvesEvent(event_name="e", user=None, time_ms=0))
        _wait_until(lambda: len(network.calls) >= 1, timeout_s=2.0)
    finally:
        logger.stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_start_and_stop_are_idempotent() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    try:
        runtime.submit(logger._start()).wait(timeout=2)  # type: ignore[attr-defined]
        logger.stop().wait(timeout=2)
        logger.stop().wait(timeout=2)
    finally:
        runtime.stop()


def test_event_logger_enqueue_after_stop_is_noop() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    try:
        logger.stop().wait(timeout=2)
        logger.enqueue(WolvesEvent(event_name="e", user=None, time_ms=0))
        time.sleep(0.05)
        assert network.calls == []
    finally:
        runtime.stop()


def test_event_logger_flush_noop_when_empty() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    try:
        logger.flush().wait(timeout=2)
        assert logger._last_flush_success is None  # type: ignore[attr-defined]
    finally:
        logger.stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_start_with_preexisting_lock_skips_lock_init_branch() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    try:
        async def reconfigure() -> None:
            if logger._periodic_task is not None:  # type: ignore[attr-defined]
                logger._periodic_task.cancel()  # type: ignore[attr-defined]
                try:
                    await logger._periodic_task  # type: ignore[attr-defined]
                except asyncio.CancelledError:
                    pass
                logger._periodic_task = None  # type: ignore[attr-defined]
            logger._flush_lock = asyncio.Lock()  # type: ignore[attr-defined]
            await logger._start()  # type: ignore[attr-defined]

        runtime.submit(reconfigure()).wait(timeout=2)
        assert logger._periodic_task is not None  # type: ignore[attr-defined]
    finally:
        logger.stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_flush_creates_lock_when_missing() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    try:
        async def seed_and_clear_lock() -> None:
            logger._flush_lock = None  # type: ignore[attr-defined]
            logger._queue.append(WolvesEvent(event_name="e", user=None, time_ms=0))  # type: ignore[attr-defined]

        runtime.submit(seed_and_clear_lock()).wait(timeout=2)
        logger.flush().wait(timeout=2)
        _wait_until(lambda: len(network.calls) == 1)
        assert logger._flush_lock is not None  # type: ignore[attr-defined]
    finally:
        logger.stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_failure_without_trim_covers_branch() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork(fail_times=1)
    sdk_key = f"test-key-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, max_queue_size=10, flush_interval_s=999)
    try:
        logger.enqueue(WolvesEvent(event_name="e", user=None, time_ms=0))
        logger.flush().wait(timeout=2)
        _wait_until(lambda: len(network.calls) == 1)
        assert logger._last_flush_success is False  # type: ignore[attr-defined]
    finally:
        logger.stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_stop_when_periodic_task_missing_covers_branch() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    try:
        async def clear_periodic() -> None:
            if logger._periodic_task is not None:  # type: ignore[attr-defined]
                logger._periodic_task.cancel()  # type: ignore[attr-defined]
                try:
                    await logger._periodic_task  # type: ignore[attr-defined]
                except asyncio.CancelledError:
                    pass
                logger._periodic_task = None  # type: ignore[attr-defined]

        runtime.submit(clear_periodic()).wait(timeout=2)
        logger.stop().wait(timeout=2)
    finally:
        runtime.stop()


# Tests for global EVENT_LOGGER_MAP persistence
def test_event_logger_registers_in_global_map() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-register-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    try:
        # Wait for start to complete
        time.sleep(0.1)
        assert sdk_key in _EVENT_LOGGER_MAP
        assert _EVENT_LOGGER_MAP[sdk_key] is logger
    finally:
        logger.stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_removes_from_global_map_on_stop() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-remove-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    try:
        # Wait for start to complete
        time.sleep(0.1)
        assert sdk_key in _EVENT_LOGGER_MAP

        # Stop should remove from map
        logger.stop().wait(timeout=2)
        assert sdk_key not in _EVENT_LOGGER_MAP
    finally:
        runtime.stop()


def test_event_logger_flushes_events_before_removing_from_map() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-flush-before-remove-{time.time()}"
    logger = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    try:
        logger.enqueue(WolvesEvent(event_name="persistence-event", user=None, time_ms=0))

        # Stop should flush events before removing from map
        logger.stop().wait(timeout=2)

        # Events should have been sent
        assert len(network.calls) == 1
        assert network.calls[0] == ["persistence-event"]

        # Logger should be removed from map
        assert sdk_key not in _EVENT_LOGGER_MAP
    finally:
        runtime.stop()


def test_event_logger_global_map_allows_interval_flush_after_reference_lost() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-interval-{time.time()}"

    def create_and_log() -> str:
        logger = EventLogger(sdk_key, network, runtime, flush_interval_s=0.05)
        logger.enqueue(WolvesEvent(event_name="orphan-event", user=None, time_ms=0))
        # Don't stop, just let reference go out of scope
        return sdk_key

    key = create_and_log()

    try:
        # Wait for interval flush to occur
        _wait_until(lambda: len(network.calls) >= 1, timeout_s=2.0)

        # Events should be sent via the interval
        assert network.calls[0] == ["orphan-event"]

        # Logger should still be in the map
        assert key in _EVENT_LOGGER_MAP
    finally:
        # Clean up
        if key in _EVENT_LOGGER_MAP:
            _EVENT_LOGGER_MAP[key].stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_separate_loggers_for_different_keys() -> None:
    runtime = AsyncRuntime()
    network1 = FakeNetwork()
    network2 = FakeNetwork()
    sdk_key1 = f"test-key-1-{time.time()}"
    sdk_key2 = f"test-key-2-{time.time()}"
    logger1 = EventLogger(sdk_key1, network1, runtime, flush_interval_s=999)
    logger2 = EventLogger(sdk_key2, network2, runtime, flush_interval_s=999)
    try:
        # Wait for start to complete
        time.sleep(0.1)

        # Both should be in map
        assert sdk_key1 in _EVENT_LOGGER_MAP
        assert sdk_key2 in _EVENT_LOGGER_MAP
        assert _EVENT_LOGGER_MAP[sdk_key1] is logger1
        assert _EVENT_LOGGER_MAP[sdk_key2] is logger2

        # Log different events
        logger1.enqueue(WolvesEvent(event_name="e1", user=None, time_ms=0))
        logger2.enqueue(WolvesEvent(event_name="e2", user=None, time_ms=0))

        # Flush logger1 only
        logger1.flush().wait(timeout=2)
        _wait_until(lambda: len(network1.calls) == 1)

        assert network1.calls[0] == ["e1"]
        assert len(network2.calls) == 0

        # Flush logger2
        logger2.flush().wait(timeout=2)
        _wait_until(lambda: len(network2.calls) == 1)

        assert network2.calls[0] == ["e2"]
    finally:
        logger1.stop().wait(timeout=2)
        logger2.stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_flushes_old_logger_when_duplicate_key_created() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-duplicate-{time.time()}"

    # First logger logs events but does NOT stop
    logger1 = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    time.sleep(0.1)  # Wait for start
    logger1.enqueue(WolvesEvent(event_name="old-event-1", user=None, time_ms=0))
    logger1.enqueue(WolvesEvent(event_name="old-event-2", user=None, time_ms=0))

    # Events should not be sent yet
    assert len(network.calls) == 0

    # Create second logger with same sdk_key - this should flush the old logger
    logger2 = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    time.sleep(0.1)  # Wait for start and old logger flush

    try:
        # Old logger's events should have been flushed
        _wait_until(lambda: len(network.calls) >= 1, timeout_s=2.0)
        assert "old-event-1" in network.calls[0]
        assert "old-event-2" in network.calls[0]

        # New logger should be in the map
        assert _EVENT_LOGGER_MAP[sdk_key] is logger2

        # New logger should work independently
        logger2.enqueue(WolvesEvent(event_name="new-event", user=None, time_ms=0))
        logger2.flush().wait(timeout=2)
        _wait_until(lambda: len(network.calls) >= 2, timeout_s=2.0)
        assert "new-event" in network.calls[-1]
    finally:
        logger2.stop().wait(timeout=2)
        runtime.stop()


def test_event_logger_stops_old_periodic_task_when_duplicate_key_created() -> None:
    runtime = AsyncRuntime()
    network = FakeNetwork()
    sdk_key = f"test-key-periodic-stop-{time.time()}"

    # First logger with short interval
    logger1 = EventLogger(sdk_key, network, runtime, flush_interval_s=0.05)
    time.sleep(0.1)  # Wait for start

    # Create second logger with same sdk_key - this should stop old periodic task
    logger2 = EventLogger(sdk_key, network, runtime, flush_interval_s=999)
    time.sleep(0.1)  # Wait for start

    try:
        # Old logger's periodic task should be stopped
        assert logger1._periodic_task is None

        # New logger's periodic task should be running
        assert logger2._periodic_task is not None

        # Only new logger should be in the map
        assert _EVENT_LOGGER_MAP[sdk_key] is logger2
    finally:
        logger2.stop().wait(timeout=2)
        runtime.stop()
