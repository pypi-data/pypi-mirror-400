import asyncio

import pytest

from castana import HealthCheck


def _result():
    return {"status": "pass", "version": "t", "checks": {}}


def test_mixed_sync_then_async_emits_warning():
    health = HealthCheck(name="svc", cache_ttl=1.0)

    health.try_get_or_run(_result)

    async def run_async():
        return _result()

    with pytest.warns(RuntimeWarning, match=r"HealthCheck used in both sync and async contexts"):
        asyncio.run(health.async_try_get_or_run(run_async))


@pytest.mark.asyncio
async def test_mixed_async_then_sync_emits_warning():
    health = HealthCheck(name="svc", cache_ttl=1.0)

    async def run_async():
        return _result()

    await health.async_try_get_or_run(run_async)

    with pytest.warns(RuntimeWarning, match=r"HealthCheck used in both sync and async contexts"):
        health.try_get_or_run(_result)


def test_mixing_without_cache_ttl_does_not_warn():
    health = HealthCheck(name="svc", cache_ttl=None)

    health.try_get_or_run(_result)

    async def run_async():
        return _result()

    # With caching disabled, there is no shared cache coordination problem.
    asyncio.run(health.async_try_get_or_run(run_async))
