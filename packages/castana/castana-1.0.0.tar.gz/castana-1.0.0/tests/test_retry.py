"""Tests for probe retry logic."""

import pytest
import asyncio
from castana import BaseProbe, HealthCheck
from castana.runner import AsyncRunner, SyncRunner
from castana.domain import HealthStatus
from castana.exceptions import WarnCondition


class TransientFailureProbe(BaseProbe):
    """Probe that fails N times before succeeding."""
    
    def __init__(self, name: str, failures_before_success: int, **kwargs):
        super().__init__(name=name, **kwargs)
        self.failures_before_success = failures_before_success
        self.attempt_count = 0
    
    async def check(self):
        self.attempt_count += 1
        if self.attempt_count <= self.failures_before_success:
            raise ConnectionError(f"Transient failure #{self.attempt_count}")
        return "success"


class SyncTransientProbe(BaseProbe):
    """Sync probe that fails N times before succeeding."""
    
    def __init__(self, name: str, failures_before_success: int, **kwargs):
        super().__init__(name=name, **kwargs)
        self.failures_before_success = failures_before_success
        self.attempt_count = 0
    
    def check(self):
        self.attempt_count += 1
        if self.attempt_count <= self.failures_before_success:
            raise ConnectionError(f"Transient failure #{self.attempt_count}")
        return "success"


class AlwaysFailProbe(BaseProbe):
    """Probe that always fails."""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
        self.attempt_count = 0
    
    async def check(self):
        self.attempt_count += 1
        raise ConnectionError("Permanent failure")


class WarnProbe(BaseProbe):
    """Probe that raises WarnCondition."""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
        self.attempt_count = 0
    
    async def check(self):
        self.attempt_count += 1
        raise WarnCondition("This is a warning")


class TestProbeRetry:
    """Tests for retry_attempts and retry_delay."""

    @pytest.mark.asyncio
    async def test_probe_succeeds_after_transient_failure(self):
        """Probe succeeds after retry."""
        probe = TransientFailureProbe(
            name="transient",
            failures_before_success=2,
            retry_attempts=2,
            retry_delay=0.01,
        )
        
        result = await probe.run()
        
        assert result.status == HealthStatus.PASS
        assert result.observed_value == "success"
        assert probe.attempt_count == 3  # 1 initial + 2 retries

    @pytest.mark.asyncio
    async def test_probe_fails_after_all_retries_exhausted(self):
        """Probe fails after all retries exhausted."""
        probe = AlwaysFailProbe(
            name="always_fail",
            retry_attempts=2,
            retry_delay=0.01,
        )
        
        result = await probe.run()
        
        assert result.status == HealthStatus.FAIL
        assert "Permanent failure" in result.output
        assert probe.attempt_count == 3  # 1 initial + 2 retries

    @pytest.mark.asyncio
    async def test_probe_without_retry_fails_immediately(self):
        """Probe without retry fails immediately."""
        probe = AlwaysFailProbe(
            name="no_retry",
            retry_attempts=0,
        )
        
        result = await probe.run()
        
        assert result.status == HealthStatus.FAIL
        assert probe.attempt_count == 1

    @pytest.mark.asyncio
    async def test_warn_condition_is_not_retried(self):
        """WarnCondition doesn't trigger retries."""
        probe = WarnProbe(
            name="warn",
            retry_attempts=3,
            retry_delay=0.01,
        )
        
        result = await probe.run()
        
        assert result.status == HealthStatus.WARN
        assert "This is a warning" in result.output
        assert probe.attempt_count == 1  # No retries

    @pytest.mark.asyncio
    async def test_latency_includes_all_attempts(self):
        """Latency includes time for all attempts."""
        probe = TransientFailureProbe(
            name="latency_test",
            failures_before_success=1,
            retry_attempts=1,
            retry_delay=0.05,  # 50ms delay
        )
        
        result = await probe.run()
        
        assert result.status == HealthStatus.PASS
        # Latency should be at least 50ms (the retry_delay)
        assert result.metadata["latency_ms"] >= 50.0

    @pytest.mark.asyncio
    async def test_retry_delay_zero_does_not_sleep(self):
        """retry_delay=0 doesn't sleep between attempts."""
        probe = TransientFailureProbe(
            name="no_delay",
            failures_before_success=2,
            retry_attempts=2,
            retry_delay=0.0,
        )
        
        result = await probe.run()
        
        assert result.status == HealthStatus.PASS
        # Should be very fast (< 100ms) with no delay
        assert result.metadata["latency_ms"] < 100.0

    @pytest.mark.asyncio
    async def test_retry_with_timeout(self):
        """Timeouts trigger retries."""
        class SlowProbe(BaseProbe):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.attempt_count = 0
                
            async def check(self):
                self.attempt_count += 1
                if self.attempt_count == 1:
                    await asyncio.sleep(10)  # Will timeout
                return "success"
        
        probe = SlowProbe(
            name="slow",
            timeout=0.05,
            retry_attempts=1,
            retry_delay=0.01,
        )
        
        result = await probe.run()
        
        assert result.status == HealthStatus.PASS
        assert probe.attempt_count == 2


class TestGlobalRetryDefaults:
    """Tests for HealthCheck-level default retry settings."""

    @pytest.mark.asyncio
    async def test_async_runner_uses_default_retries(self):
        """AsyncRunner uses default retry settings."""
        probe = TransientFailureProbe(
            name="defaults",
            failures_before_success=2,
            retry_attempts=0, # Use default
            retry_delay=0.0,  # Use default
        )
        
        runner = AsyncRunner(
            probes=[probe],
            default_retry_attempts=2,
            default_retry_delay=0.01,
        )
        
        result = await runner.execute()
        
        assert result["status"] == HealthStatus.PASS
        assert probe.attempt_count == 3  # 1 initial + 2 retries

    def test_sync_runner_uses_default_retries(self):
        """SyncRunner uses default retry settings."""
        probe = SyncTransientProbe(
            name="sync_defaults",
            failures_before_success=2,
            retry_attempts=0, # Use default
            retry_delay=0.0,  # Use default
        )
        
        runner = SyncRunner(
            probes=[probe],
            default_retry_attempts=2,
            default_retry_delay=0.01,
        )
        
        result = runner.execute()
        
        assert result["status"] == HealthStatus.PASS
        assert probe.attempt_count == 3  # 1 initial + 2 retries

    @pytest.mark.asyncio
    async def test_probe_override_wins_over_defaults(self):
        """Probe settings override global defaults."""
        probe = TransientFailureProbe(
            name="override",
            failures_before_success=2,
            retry_attempts=1,  # Only retry once (not enough)
            retry_delay=0.01,
        )
        
        runner = AsyncRunner(
            probes=[probe],
            default_retry_attempts=10,  # Should be ignored
            default_retry_delay=0.01,
        )
        
        result = await runner.execute()
        
        assert result["status"] == HealthStatus.FAIL
        assert probe.attempt_count == 2  # 1 initial + 1 probe-retry
