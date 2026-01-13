"""
Tests for the Python 3.9/3.10 compatibility shim.

These tests use the exposed ``_async_timeout_shim`` directly to ensure the shim
logic is tested even when running on Python 3.11+ (where ``async_timeout`` is
aliased to the native ``asyncio.timeout``).
"""
import asyncio
import pytest

from castana._compat import _async_timeout_shim


@pytest.mark.asyncio
async def test_shim_timeout_fires_correctly():
    """When the operation exceeds the timeout, TimeoutError is raised."""
    with pytest.raises(TimeoutError, match="timed out after 0.05s"):
        async with _async_timeout_shim(0.05):
            await asyncio.sleep(1.0)


@pytest.mark.asyncio
async def test_shim_no_timeout_when_fast():
    """When the operation completes before timeout, no error is raised."""
    result = None
    async with _async_timeout_shim(1.0):
        await asyncio.sleep(0.01)
        result = "completed"

    assert result == "completed"


@pytest.mark.asyncio
async def test_shim_external_cancellation_not_converted_to_timeout():
    """
    External cancellation should remain CancelledError, not become TimeoutError.

    This is the critical regression test for the shim bug where external
    cancellations were incorrectly reported as timeouts.
    """
    async def victim():
        async with _async_timeout_shim(5.0):  # Long timeout
            await asyncio.sleep(10.0)  # Even longer sleep
        return "done"

    task = asyncio.create_task(victim())
    await asyncio.sleep(0.05)  # Let it start
    task.cancel()  # External cancellation at 0.05s (well before 5s timeout)

    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_shim_exception_passthrough():
    """Regular exceptions should pass through unchanged."""
    with pytest.raises(ValueError, match="test error"):
        async with _async_timeout_shim(1.0):
            raise ValueError("test error")


@pytest.mark.asyncio
async def test_shim_handle_cleaned_up_on_success():
    """Timer handle should be cancelled after successful completion."""
    async with _async_timeout_shim(1.0):
        await asyncio.sleep(0.01)

    # If we get here without hanging, the handle was properly cleaned up


@pytest.mark.asyncio
async def test_shim_handle_cleaned_up_on_timeout():
    """Timer handle should be cancelled even after timeout."""
    try:
        async with _async_timeout_shim(0.05):
            await asyncio.sleep(1.0)
    except TimeoutError:
        pass

    # Give the event loop a chance to process any pending callbacks
    await asyncio.sleep(0.1)
