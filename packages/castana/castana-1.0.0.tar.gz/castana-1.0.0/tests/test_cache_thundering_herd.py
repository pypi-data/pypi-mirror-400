import threading
import time
from concurrent.futures import ThreadPoolExecutor

from castana import HealthCheck


def test_try_get_or_run_prevents_thundering_herd_with_concurrent_callers():
    """When cache is empty/stale, only one caller should execute run_fn."""

    health = HealthCheck(name="svc", cache_ttl=5.0)

    call_count_lock = threading.Lock()
    call_count = 0

    def run_fn():
        nonlocal call_count
        with call_count_lock:
            call_count += 1
        # Make the work slow enough that other threads overlap.
        time.sleep(0.05)
        return {"status": "pass", "version": "t", "checks": {}}

    concurrency = 16
    start_barrier = threading.Barrier(concurrency)

    def worker():
        start_barrier.wait()
        return health.try_get_or_run(run_fn)

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        results = list(pool.map(lambda _: worker(), range(concurrency)))

    assert call_count == 1
    # All callers should observe the same cached result.
    assert len({id(r) for r in results}) == 1
