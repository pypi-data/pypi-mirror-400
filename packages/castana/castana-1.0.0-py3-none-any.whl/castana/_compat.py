"""
Python version compatibility shims.

Provides asyncio.timeout equivalent for Python 3.9/3.10.
"""
from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator


@asynccontextmanager
async def _async_timeout_shim(delay: float) -> AsyncIterator[None]:
    task = asyncio.current_task()
    if task is None:
        raise RuntimeError("async_timeout must be called from within a task")

    loop = asyncio.get_running_loop()

    timed_out = False

    def _timeout_handler() -> None:
        nonlocal timed_out
        timed_out = True
        if not task.done():
            task.cancel()

    handle = loop.call_later(delay, _timeout_handler)
    try:
        yield
    except asyncio.CancelledError:
        if timed_out:
            raise TimeoutError(f"Operation timed out after {delay}s")
        raise
    finally:
        handle.cancel()

if sys.version_info >= (3, 11):
    async_timeout = asyncio.timeout
else:
    async_timeout = _async_timeout_shim
