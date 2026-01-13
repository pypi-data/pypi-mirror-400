import asyncio
import pytest
import time
from castana import BaseProbe, HealthStatus
from castana.runner import AsyncRunner, SyncRunner
from castana.exceptions import WarnCondition

# --- Mocks ---

class MockAsyncProbe(BaseProbe):
    async def check(self):
        await asyncio.sleep(0.01) # Simulate I/O
        return "async_ok"

class MockSyncProbe(BaseProbe):
    def check(self):
        time.sleep(0.01) # Simulate blocking I/O
        return "sync_ok"

class MockFailProbe(BaseProbe):
    async def check(self):
        raise ValueError("boom")

class MockWarnProbe(BaseProbe):
    async def check(self):
        raise WarnCondition("careful now")

# --- Tests ---

@pytest.mark.asyncio
async def test_async_runner_hybrid_execution():
    probes = [
        MockAsyncProbe(name="async_p"),
        MockSyncProbe(name="sync_p")
    ]
    
    runner = AsyncRunner(probes)
    result = await runner.execute()

    assert result["status"] == HealthStatus.PASS
    checks = result["checks"]
    
    # Check Async Probe
    assert checks["async_p"][0]["status"] == "pass"
    assert checks["async_p"][0]["observedValue"] == "async_ok"
    assert checks["async_p"][0]["time"]
    assert "latency_ms" in checks["async_p"][0]["metadata"]
    
    # Check Sync Probe (Should have been wrapped in thread)
    assert checks["sync_p"][0]["status"] == "pass"
    assert checks["sync_p"][0]["observedValue"] == "sync_ok"

@pytest.mark.asyncio
async def test_runner_aggregates_status():
    probes = [
        MockAsyncProbe(name="ok"),
        MockFailProbe(name="bad")
    ]
    
    runner = AsyncRunner(probes)
    result = await runner.execute()

    assert result["status"] == HealthStatus.FAIL
    assert result["checks"]["bad"][0]["status"] == "fail"
    assert result["checks"]["bad"][0]["output"] == "boom"

@pytest.mark.asyncio
async def test_runner_warn_logic():
    probes = [
        MockAsyncProbe(name="ok"),
        MockWarnProbe(name="slow")
    ]
    
    runner = AsyncRunner(probes)
    result = await runner.execute()

    assert result["status"] == HealthStatus.WARN
    assert result["checks"]["slow"][0]["status"] == "warn"
    assert result["checks"]["slow"][0]["output"] == "careful now"


class ExplodingRunProbe(BaseProbe):
    async def run(self, **kwargs):
        raise ValueError("runner_boom")

    async def check(self):
        return "unused"


@pytest.mark.asyncio
async def test_async_runner_attributes_unhandled_exception_to_probe_name():
    probes = [ExplodingRunProbe(name="bad_probe")]

    runner = AsyncRunner(probes)
    result = await runner.execute()

    assert result["status"] == HealthStatus.FAIL
    assert "bad_probe" in result["checks"]
    assert result["checks"]["bad_probe"][0]["output"] == "Runner Exception: runner_boom"
    assert "runner" not in result["checks"]


class MockSlowSyncProbe(BaseProbe):
    def __init__(self, name: str, sleep_s: float):
        super().__init__(name=name)
        self.sleep_s = sleep_s

    def check(self):
        time.sleep(self.sleep_s)
        return "sync_slept"


class MockFastAsyncProbe(BaseProbe):
    def __init__(self, name: str, set_when_done: asyncio.Event):
        super().__init__(name=name)
        self.set_when_done = set_when_done

    async def check(self):
        self.set_when_done.set()
        return "async_done"


@pytest.mark.asyncio
async def test_async_runner_does_not_block_event_loop_with_slow_sync_probe():
    async_done = asyncio.Event()

    probes = [
        MockSlowSyncProbe(name="slow_sync", sleep_s=0.2),
        MockFastAsyncProbe(name="fast_async", set_when_done=async_done),
    ]

    runner = AsyncRunner(probes)

    runner_task = asyncio.create_task(runner.execute())

    # If the slow sync probe ran on the event loop, this would time out.
    await asyncio.wait_for(async_done.wait(), timeout=0.05)

    result = await runner_task
    assert set(result["checks"].keys()) == {"fast_async", "slow_sync"}
    assert result["checks"]["fast_async"][0]["observedValue"] == "async_done"
    assert result["checks"]["slow_sync"][0]["observedValue"] == "sync_slept"
    assert result["checks"]["fast_async"][0]["time"]
    assert "latency_ms" in result["checks"]["fast_async"][0]["metadata"]


# --- SyncRunner Tests ---

class SyncFailProbe(BaseProbe):
    def check(self):
        raise ValueError("sync_boom")


class SyncWarnProbe(BaseProbe):
    def check(self):
        raise WarnCondition("sync_warning")


def test_sync_runner_basic_execution():
    probes = [
        MockSyncProbe(name="sync_a"),
        MockSyncProbe(name="sync_b"),
    ]

    runner = SyncRunner(probes)
    result = runner.execute()

    assert result["status"] == HealthStatus.PASS
    assert "sync_a" in result["checks"]
    assert "sync_b" in result["checks"]
    assert result["checks"]["sync_a"][0]["status"] == "pass"
    assert result["checks"]["sync_a"][0]["observedValue"] == "sync_ok"


def test_sync_runner_handles_failure():
    probes = [
        MockSyncProbe(name="ok"),
        SyncFailProbe(name="bad"),
    ]

    runner = SyncRunner(probes)
    result = runner.execute()

    assert result["status"] == HealthStatus.FAIL
    assert result["checks"]["bad"][0]["status"] == "fail"
    assert result["checks"]["bad"][0]["output"] == "sync_boom"


def test_sync_runner_handles_warn():
    probes = [
        MockSyncProbe(name="ok"),
        SyncWarnProbe(name="slow"),
    ]

    runner = SyncRunner(probes)
    result = runner.execute()

    assert result["status"] == HealthStatus.WARN
    assert result["checks"]["slow"][0]["status"] == "warn"
    assert result["checks"]["slow"][0]["output"] == "sync_warning"


def test_sync_runner_includes_version():
    probes = [MockSyncProbe(name="test")]

    runner = SyncRunner(probes, version="2.0.0")
    result = runner.execute()

    assert result["version"] == "2.0.0"


def test_sync_runner_handles_async_probes():
    probes = [
        MockAsyncProbe(name="async_in_sync"),
        MockSyncProbe(name="pure_sync"),
    ]

    runner = SyncRunner(probes)
    result = runner.execute()

    assert result["status"] == HealthStatus.PASS
    assert result["checks"]["async_in_sync"][0]["observedValue"] == "async_ok"
    assert result["checks"]["pure_sync"][0]["observedValue"] == "sync_ok"


# --- Critical vs Optional Tests ---

class NonCriticalFailProbe(BaseProbe):
    def __init__(self, name: str):
        super().__init__(name=name, critical=False)
    
    async def check(self):
        raise ValueError("non-critical failure")


@pytest.mark.asyncio
async def test_non_critical_probe_failure_does_not_cause_global_fail():
    probes = [
        MockAsyncProbe(name="ok"),
        NonCriticalFailProbe(name="optional"),
    ]
    
    runner = AsyncRunner(probes)
    result = await runner.execute()

    # Global status should be PASS (not FAIL) because the failing probe is non-critical
    assert result["status"] == HealthStatus.PASS
    
    # The individual probe should still show as failed in the checks
    assert result["checks"]["optional"][0]["status"] == "fail"
    assert result["checks"]["optional"][0]["output"] == "non-critical failure"


@pytest.mark.asyncio
async def test_critical_probe_failure_causes_global_fail():
    """Critical probe failure causes global FAIL."""
    probes = [
        MockAsyncProbe(name="ok"),
        MockFailProbe(name="critical"),  # Default is critical=True
    ]
    
    runner = AsyncRunner(probes)
    result = await runner.execute()

    assert result["status"] == HealthStatus.FAIL


@pytest.mark.asyncio
async def test_mixed_critical_and_non_critical_failures():
    """Mixed critical/non-critical failures cause FAIL."""
    probes = [
        MockFailProbe(name="critical"),
        NonCriticalFailProbe(name="optional"),
    ]
    
    runner = AsyncRunner(probes)
    result = await runner.execute()

    # Critical failure should cause FAIL
    assert result["status"] == HealthStatus.FAIL
    
    # Both should show as failed
    assert result["checks"]["critical"][0]["status"] == "fail"
    assert result["checks"]["optional"][0]["status"] == "fail"

