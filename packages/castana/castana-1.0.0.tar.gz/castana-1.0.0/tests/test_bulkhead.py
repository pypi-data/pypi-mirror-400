import asyncio
import time

import pytest

from castana import BaseProbe, HealthCheck
from castana.runner import AsyncRunner, SyncRunner


class SlowSyncProbe(BaseProbe):
    def __init__(self, name: str, sleep_s: float):
        super().__init__(name=name)
        self.sleep_s = sleep_s

    def check(self):
        time.sleep(self.sleep_s)
        return "ok"


class FastSyncProbe(BaseProbe):
    def check(self):
        return "ok"


@pytest.mark.asyncio
async def test_bulkhead_isolation_from_default_thread_pool_saturation():
    loop = asyncio.get_running_loop()

    # Saturate the loop's default executor with slow tasks.
    # We cap concurrency so the test remains stable across environments.
    default_workers = 10
    saturation_executor = None

    # First, schedule tasks to occupy the default thread pool.
    saturation_tasks = [
        loop.run_in_executor(saturation_executor, time.sleep, 0.3)
        for _ in range(default_workers)
    ]

    health = HealthCheck(name="protected", max_workers=1)
    health.add_probe(SlowSyncProbe(name="slow_probe", sleep_s=0.05))

    runner = AsyncRunner(
        probes=list(health.probes.values()),
        global_timeout=5.0,
        executor=health.executor,
    )

    start = time.perf_counter()
    await runner.execute()
    duration = time.perf_counter() - start

    # If the probe ran on the default executor, it could queue behind the
    # saturation tasks. With a dedicated executor, it should complete quickly.
    assert duration < 0.2

    await asyncio.gather(*saturation_tasks)
    health.shutdown(wait=False)


def test_try_get_or_run_after_shutdown_does_not_use_closed_executor():
    health = HealthCheck(name="svc", max_workers=1, cache_ttl=1.0)
    health.add_probe(FastSyncProbe(name="p"))

    health.shutdown(wait=False)

    def run_probes():
        runner = SyncRunner(
            probes=list(health.probes.values()),
            global_timeout=5.0,
            version=health.version,
            executor=health.executor,
        )
        return runner.execute()

    result = health.try_get_or_run(run_probes)
    assert result["status"] in {"pass", "warn", "fail"}
    assert result["checks"]["p"][0]["status"] == "pass"


@pytest.mark.asyncio
async def test_async_try_get_or_run_after_shutdown_does_not_use_closed_executor():
    health = HealthCheck(name="svc", max_workers=1, cache_ttl=1.0)
    health.add_probe(FastSyncProbe(name="p"))

    health.shutdown(wait=False)

    async def run_probes():
        runner = AsyncRunner(
            probes=list(health.probes.values()),
            global_timeout=5.0,
            version=health.version,
            executor=health.executor,
        )
        return await runner.execute()

    result = await health.async_try_get_or_run(run_probes)
    assert result["checks"]["p"][0]["status"] == "pass"
