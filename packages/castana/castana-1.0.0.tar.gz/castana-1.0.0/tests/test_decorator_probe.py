import asyncio
import inspect
import pytest
from castana import HealthCheck, FunctionProbe, BaseProbe
from castana.runner import AsyncRunner


class TestFunctionProbe:

    def test_sync_function_probe_creation(self):
        def my_check():
            return "OK"
        
        probe = FunctionProbe(fn=my_check, name="sync-test")
        
        assert probe.name == "sync-test"
        assert probe.check() == "OK"
        assert not inspect.iscoroutinefunction(probe.check)

    def test_async_function_probe_creation(self):
        async def my_async_check():
            return "ASYNC_OK"
        
        probe = FunctionProbe(fn=my_async_check, name="async-test")
        
        assert probe.name == "async-test"
        assert inspect.iscoroutinefunction(probe.check)
        
        # Verify the async function can be awaited
        result = asyncio.run(probe.check())
        assert result == "ASYNC_OK"

    def test_function_probe_parameters(self):
        def my_check():
            return 1
        
        probe = FunctionProbe(
            fn=my_check,
            name="param-test",
            timeout=10.0,
            component_type="datastore",
            critical=False,
            retry_attempts=3,
            retry_delay=0.5,
        )
        
        assert probe.name == "param-test"
        assert probe.timeout == 10.0
        assert probe.component_type == "datastore"
        assert probe.critical is False
        assert probe.retry_attempts == 3
        assert probe.retry_delay == 0.5


class TestHealthCheckProbeDecorator:

    def test_decorator_registers_sync_probe(self):
        health = HealthCheck()
        
        @health.probe(name="sync-decorator-test")
        def check_something():
            return {"status": "healthy"}
        
        assert "sync-decorator-test" in health.probes
        probe = health.probes["sync-decorator-test"]
        assert isinstance(probe, BaseProbe)
        assert probe.check() == {"status": "healthy"}

    def test_decorator_registers_async_probe(self):
        health = HealthCheck()
        
        @health.probe(name="async-decorator-test")
        async def check_async():
            return "async_result"
        
        assert "async-decorator-test" in health.probes
        probe = health.probes["async-decorator-test"]
        assert isinstance(probe, BaseProbe)
        assert inspect.iscoroutinefunction(probe.check)

    def test_decorator_preserves_original_function(self):
        health = HealthCheck()
        
        @health.probe(name="preserve-test")
        def my_function():
            return 42
        
        # The decorated function should still be callable outside of health checks
        assert my_function() == 42

    def test_decorator_forwards_parameters(self):
        """Decorator parameters forwarded to probe."""
        health = HealthCheck()
        
        @health.probe(
            name="params-test",
            timeout=15.0,
            component_type="system",
            critical=False,
            retry_attempts=2,
            retry_delay=1.0,
        )
        def check_with_params():
            return True
        
        probe = health.probes["params-test"]
        assert probe.timeout == 15.0
        assert probe.component_type == "system"
        assert probe.critical is False
        assert probe.retry_attempts == 2
        assert probe.retry_delay == 1.0

    def test_decorator_with_groups(self):
        """Decorator assigns probes to groups."""
        health = HealthCheck()
        
        @health.probe(name="grouped-probe", groups=["liveness", "readiness"])
        def grouped_check():
            return "ok"
        
        assert health.probe_groups["grouped-probe"] == {"liveness", "readiness"}

    def test_duplicate_name_raises_error(self):
        """Duplicate probe name raises ValueError."""
        health = HealthCheck()
        
        @health.probe(name="duplicate")
        def first_check():
            return 1
        
        with pytest.raises(ValueError) as exc_info:
            @health.probe(name="duplicate")
            def second_check():
                return 2
        
        assert "Probe 'duplicate' already registered" in str(exc_info.value)


class TestDecoratorIntegration:
    """Integration tests for decorated probes with the runner."""

    @pytest.mark.asyncio
    async def test_sync_decorated_probe_runs_correctly(self):
        """Sync decorated probe executes correctly."""
        health = HealthCheck()
        
        @health.probe(name="integration-sync")
        def sync_check():
            return "sync_value"
        
        runner = AsyncRunner(
            probes=list(health.probes.values()),
            global_timeout=10.0,
        )
        result = await runner.execute()
        
        assert result["status"].value == "pass"
        assert "integration-sync" in result["checks"]
        assert result["checks"]["integration-sync"][0]["observedValue"] == "sync_value"

    @pytest.mark.asyncio
    async def test_async_decorated_probe_runs_correctly(self):
        """Async decorated probe executes correctly."""
        health = HealthCheck()
        
        @health.probe(name="integration-async")
        async def async_check():
            await asyncio.sleep(0.01)
            return "async_value"
        
        runner = AsyncRunner(
            probes=list(health.probes.values()),
            global_timeout=10.0,
        )
        result = await runner.execute()
        
        assert result["status"].value == "pass"
        assert "integration-async" in result["checks"]
        assert result["checks"]["integration-async"][0]["observedValue"] == "async_value"

    @pytest.mark.asyncio
    async def test_mixed_decorated_probes(self):
        """Mixed sync/async decorated probes work together."""
        health = HealthCheck()
        
        @health.probe(name="mixed-sync")
        def sync_check():
            return "sync"
        
        @health.probe(name="mixed-async")
        async def async_check():
            return "async"
        
        runner = AsyncRunner(
            probes=list(health.probes.values()),
            global_timeout=10.0,
        )
        result = await runner.execute()
        
        assert result["status"].value == "pass"
        assert len(result["checks"]) == 2
        assert result["checks"]["mixed-sync"][0]["observedValue"] == "sync"
        assert result["checks"]["mixed-async"][0]["observedValue"] == "async"
