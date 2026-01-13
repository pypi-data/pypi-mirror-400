"""Tests for the observer pattern and ProbeObserver implementations."""
import asyncio
import pytest
from typing import List, Dict, Any, Optional

from castana import BaseProbe, HealthCheck, HealthStatus, ProbeObserver
from castana.domain import ProbeResult
from castana.runner import AsyncRunner, SyncRunner
from castana.exceptions import WarnCondition


# --- Test Observer Implementation ---

class RecordingObserver(ProbeObserver):
    """Observer that records all events for testing."""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.probe_starts: List[Dict[str, Any]] = []
        self.probe_results: List[ProbeResult] = []
        self.probe_retries: List[Dict[str, Any]] = []
        self.probe_timeouts: List[Dict[str, Any]] = []
        self.suite_completes: List[Dict[str, Any]] = []

    def on_probe_start(self, probe_name: str, attempt: int) -> None:
        self.probe_starts.append({"name": probe_name, "attempt": attempt})
        self.events.append({"type": "start", "name": probe_name, "attempt": attempt})

    def on_probe_result(self, result: ProbeResult) -> None:
        self.probe_results.append(result)
        self.events.append({"type": "result", "name": result.name, "status": result.status})

    def on_probe_retry(
        self,
        probe_name: str,
        attempt: int,
        previous_status: str,
        delay: float,
    ) -> None:
        self.probe_retries.append({
            "name": probe_name,
            "attempt": attempt,
            "previous_status": previous_status,
            "delay": delay,
        })
        self.events.append({"type": "retry", "name": probe_name, "attempt": attempt})

    def on_probe_timeout(self, probe_name: str, timeout_seconds: float) -> None:
        self.probe_timeouts.append({"name": probe_name, "timeout": timeout_seconds})
        self.events.append({"type": "timeout", "name": probe_name})

    def on_suite_complete(
        self,
        result: Dict[str, Any],
        duration_ms: float,
        probe_count: int,
    ) -> None:
        self.suite_completes.append({
            "status": result["status"],
            "duration_ms": duration_ms,
            "probe_count": probe_count,
        })
        self.events.append({"type": "suite_complete", "probe_count": probe_count})


class ExplodingObserver(ProbeObserver):
    """Observer that throws exceptions in all callbacks."""

    def on_probe_start(self, probe_name: str, attempt: int) -> None:
        raise RuntimeError("Observer exploded on start")

    def on_probe_result(self, result: ProbeResult) -> None:
        raise RuntimeError("Observer exploded on result")

    def on_probe_retry(self, probe_name: str, attempt: int, previous_status: str, delay: float) -> None:
        raise RuntimeError("Observer exploded on retry")

    def on_probe_timeout(self, probe_name: str, timeout_seconds: float) -> None:
        raise RuntimeError("Observer exploded on timeout")

    def on_suite_complete(self, result: Dict[str, Any], duration_ms: float, probe_count: int) -> None:
        raise RuntimeError("Observer exploded on suite complete")


# --- Mock Probes ---

class MockAsyncProbe(BaseProbe):
    async def check(self):
        await asyncio.sleep(0.01)
        return "async_ok"


class MockSyncProbe(BaseProbe):
    def check(self):
        return "sync_ok"


class MockFailProbe(BaseProbe):
    async def check(self):
        raise ValueError("boom")


class MockWarnProbe(BaseProbe):
    async def check(self):
        raise WarnCondition("careful now")


class MockRetryProbe(BaseProbe):
    def __init__(self, name: str, fail_count: int = 1):
        super().__init__(name=name, retry_attempts=2, retry_delay=0.01)
        self.fail_count = fail_count
        self.call_count = 0

    async def check(self):
        self.call_count += 1
        if self.call_count <= self.fail_count:
            raise ValueError(f"fail {self.call_count}")
        return "eventually_ok"


class MockTimeoutProbe(BaseProbe):
    def __init__(self, name: str):
        super().__init__(name=name, timeout=0.05)

    async def check(self):
        await asyncio.sleep(0.2)  # Longer than timeout
        return "never"


# --- AsyncRunner Observer Tests ---

@pytest.mark.asyncio
async def test_observer_receives_probe_start_event():
    """Observer should receive on_probe_start for each probe."""
    observer = RecordingObserver()
    probes = [MockAsyncProbe(name="test_probe")]

    runner = AsyncRunner(probes, observers=[observer])
    await runner.execute()

    assert len(observer.probe_starts) == 1
    assert observer.probe_starts[0]["name"] == "test_probe"
    assert observer.probe_starts[0]["attempt"] == 0


@pytest.mark.asyncio
async def test_observer_receives_probe_result_event():
    """Observer should receive on_probe_result for each probe result."""
    observer = RecordingObserver()
    probes = [MockAsyncProbe(name="test_probe")]

    runner = AsyncRunner(probes, observers=[observer])
    await runner.execute()

    assert len(observer.probe_results) == 1
    assert observer.probe_results[0].name == "test_probe"
    assert observer.probe_results[0].status == HealthStatus.PASS


@pytest.mark.asyncio
async def test_observer_receives_suite_complete_event():
    """Observer should receive on_suite_complete after all probes finish."""
    observer = RecordingObserver()
    probes = [
        MockAsyncProbe(name="p1"),
        MockAsyncProbe(name="p2"),
    ]

    runner = AsyncRunner(probes, observers=[observer])
    await runner.execute()

    assert len(observer.suite_completes) == 1
    assert observer.suite_completes[0]["probe_count"] == 2
    assert observer.suite_completes[0]["status"] == HealthStatus.PASS
    assert observer.suite_completes[0]["duration_ms"] > 0


@pytest.mark.asyncio
async def test_observer_receives_retry_events():
    """Observer should receive on_probe_retry before each retry attempt."""
    observer = RecordingObserver()
    probes = [MockRetryProbe(name="retry_probe", fail_count=1)]

    runner = AsyncRunner(probes, observers=[observer])
    await runner.execute()

    # Should have one retry event (after first failure, before second attempt)
    assert len(observer.probe_retries) == 1
    assert observer.probe_retries[0]["name"] == "retry_probe"
    assert observer.probe_retries[0]["attempt"] == 1  # Next attempt number
    assert observer.probe_retries[0]["previous_status"] == "fail"


@pytest.mark.asyncio
async def test_observer_receives_timeout_events():
    """Observer should receive on_probe_timeout when a probe times out."""
    observer = RecordingObserver()
    probes = [MockTimeoutProbe(name="slow_probe")]

    runner = AsyncRunner(probes, observers=[observer])
    await runner.execute()

    assert len(observer.probe_timeouts) == 1
    assert observer.probe_timeouts[0]["name"] == "slow_probe"
    assert observer.probe_timeouts[0]["timeout"] == 0.05


@pytest.mark.asyncio
async def test_multiple_observers_all_receive_events():
    """All registered observers should receive all events."""
    observer1 = RecordingObserver()
    observer2 = RecordingObserver()
    probes = [MockAsyncProbe(name="test")]

    runner = AsyncRunner(probes, observers=[observer1, observer2])
    await runner.execute()

    # Both observers should have received the same events
    assert len(observer1.probe_results) == 1
    assert len(observer2.probe_results) == 1
    assert len(observer1.suite_completes) == 1
    assert len(observer2.suite_completes) == 1


@pytest.mark.asyncio
async def test_observer_exception_does_not_affect_probe_execution():
    """Observer exceptions should not break probe execution."""
    exploding = ExplodingObserver()
    recording = RecordingObserver()
    probes = [MockAsyncProbe(name="test")]

    # Exploding observer registered first
    runner = AsyncRunner(probes, observers=[exploding, recording])
    result = await runner.execute()

    # Probe should still execute successfully
    assert result["status"] == HealthStatus.PASS
    assert result["checks"]["test"][0]["status"] == "pass"

    # Recording observer should still receive events
    assert len(recording.probe_results) == 1


# --- SyncRunner Observer Tests ---

def test_sync_runner_observer_receives_events():
    """SyncRunner should notify observers for sync probes."""
    observer = RecordingObserver()
    probes = [MockSyncProbe(name="sync_test")]

    runner = SyncRunner(probes, observers=[observer])
    runner.execute()

    assert len(observer.probe_starts) == 1
    assert observer.probe_starts[0]["name"] == "sync_test"
    assert len(observer.probe_results) == 1
    assert observer.probe_results[0].name == "sync_test"
    assert len(observer.suite_completes) == 1


def test_sync_runner_observer_with_mixed_probes():
    """SyncRunner should notify observers for both sync and async probes."""
    observer = RecordingObserver()
    probes = [
        MockSyncProbe(name="sync_p"),
        MockAsyncProbe(name="async_p"),
    ]

    runner = SyncRunner(probes, observers=[observer])
    runner.execute()

    # Should have results for both probes
    result_names = {r.name for r in observer.probe_results}
    assert result_names == {"sync_p", "async_p"}
    assert len(observer.suite_completes) == 1
    assert observer.suite_completes[0]["probe_count"] == 2


# --- HealthCheck Observer Integration Tests ---

@pytest.mark.asyncio
async def test_healthcheck_passes_observers_to_runner():
    """HealthCheck should pass its observers to created runners."""
    observer = RecordingObserver()

    health = HealthCheck(observers=[observer])
    health.add_probe(MockAsyncProbe(name="test"))

    # Simulate what the adapter does
    probes = health.get_probes()
    runner = AsyncRunner(
        probes=probes,
        global_timeout=health.global_timeout,
        observers=health.observers,
    )
    await runner.execute()

    assert len(observer.probe_results) == 1


def test_healthcheck_add_observer():
    """HealthCheck.add_observer should add observers."""
    health = HealthCheck()
    observer = RecordingObserver()

    assert len(health.observers) == 0

    health.add_observer(observer)

    assert len(health.observers) == 1
    assert health.observers[0] is observer


def test_healthcheck_observers_property():
    """HealthCheck.observers should return the list of observers."""
    observer1 = RecordingObserver()
    observer2 = RecordingObserver()

    health = HealthCheck(observers=[observer1, observer2])

    assert len(health.observers) == 2
    assert observer1 in health.observers
    assert observer2 in health.observers


# --- Request-Level Metrics Tests ---

@pytest.mark.asyncio
async def test_async_runner_includes_request_metrics():
    """AsyncRunner should include metrics in result when not redacting."""
    probes = [MockAsyncProbe(name="test")]

    runner = AsyncRunner(probes, redact_sensitive=False)
    result = await runner.execute()

    assert "metrics" in result
    assert "duration_ms" in result["metrics"]
    assert "probe_count" in result["metrics"]
    assert "global_timeout_ms" in result["metrics"]
    assert result["metrics"]["probe_count"] == 1
    assert result["metrics"]["duration_ms"] > 0


@pytest.mark.asyncio
async def test_async_runner_excludes_metrics_when_redacting():
    """AsyncRunner should not include metrics when redact_sensitive=True."""
    probes = [MockAsyncProbe(name="test")]

    runner = AsyncRunner(probes, redact_sensitive=True)
    result = await runner.execute()

    assert "metrics" not in result


def test_sync_runner_includes_request_metrics():
    """SyncRunner should include metrics in result when not redacting."""
    probes = [MockSyncProbe(name="test")]

    runner = SyncRunner(probes, redact_sensitive=False)
    result = runner.execute()

    assert "metrics" in result
    assert "duration_ms" in result["metrics"]
    assert "probe_count" in result["metrics"]
    assert result["metrics"]["probe_count"] == 1


def test_sync_runner_excludes_metrics_when_redacting():
    """SyncRunner should not include metrics when redact_sensitive=True."""
    probes = [MockSyncProbe(name="test")]

    runner = SyncRunner(probes, redact_sensitive=True)
    result = runner.execute()

    assert "metrics" not in result
