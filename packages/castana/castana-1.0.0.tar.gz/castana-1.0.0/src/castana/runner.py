from __future__ import annotations

import asyncio
import inspect
import logging
import time
from concurrent.futures import Executor, ThreadPoolExecutor, wait, FIRST_COMPLETED, TimeoutError as FuturesTimeoutError
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Dict, Any, Optional

logger = logging.getLogger(__name__)

from castana._compat import async_timeout
from castana.domain import ProbeResult, HealthStatus
from castana.probes.base import BaseProbe
from castana.utils import aggregate_results
from castana.exceptions import WarnCondition

if TYPE_CHECKING:
    from castana.observers.base import ProbeObserver


def _error_result(name: str, output: str, critical: bool = True) -> ProbeResult:
    return ProbeResult(
        status=HealthStatus.FAIL,
        name=name,
        output=output,
        time=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        critical=critical,
    )

class BaseRunner:
    def __init__(
        self,
        probes: List[BaseProbe],
        global_timeout: float = 30.0,
        version: str = "1.0.0",
        default_retry_attempts: int = 0,
        default_retry_delay: float = 0.0,
        observers: Optional[List["ProbeObserver"]] = None,
    ):
        self.probes = probes
        self.global_timeout = global_timeout
        self.version = version
        self.default_retry_attempts = default_retry_attempts
        self.default_retry_delay = default_retry_delay
        self.observers = observers or []

    def _run_sync_probe(self, probe: BaseProbe, deadline: Optional[float] = None) -> ProbeResult:
        retry_attempts = probe.retry_attempts if probe.retry_attempts > 0 else self.default_retry_attempts
        retry_delay = probe.retry_delay if probe.retry_delay > 0 else self.default_retry_delay

        total_attempts = 1 + retry_attempts
        last_result = None
        overall_start = time.perf_counter()

        for attempt in range(total_attempts):
            if attempt > 0 and deadline and time.monotonic() > deadline:
                if last_result:
                    return last_result
                return _error_result(
                    name=probe.name,
                    output=f"Deadline exceeded before retry attempt {attempt +1}",
                    critical=probe.critical,
                )

            for observer in self.observers:
                observer.on_probe_start(probe.name, attempt)

            start = time.perf_counter()
            try:
                result = probe.check()

                duration_ms = (time.perf_counter() - overall_start) * 1000
                timeout_ms = probe.timeout * 1000

                if duration_ms > timeout_ms:
                    probe_result = probe._build_result(
                        status=HealthStatus.WARN,
                        output=f"Slow response: {duration_ms:.0f}ms (threshold: {timeout_ms:.0f}ms)",
                        observed_value=result,
                        latency_ms=duration_ms
                    )
                    for observer in self.observers:
                        observer.on_probe_timeout(probe.name, probe.timeout)
                        observer.on_probe_result(probe_result)
                    return probe_result

                probe_result = probe._build_result(
                    status=HealthStatus.PASS,
                    observed_value=result,
                    latency_ms=duration_ms
                )
                for observer in self.observers:
                    observer.on_probe_result(probe_result)
                return probe_result

            except WarnCondition as w:
                duration_ms = (time.perf_counter() - overall_start) * 1000
                probe_result = probe._build_result(
                    status=HealthStatus.WARN,
                    output=str(w),
                    latency_ms=duration_ms
                )
                for observer in self.observers:
                    observer.on_probe_result(probe_result)
                return probe_result

            except Exception as e:
                duration_ms = (time.perf_counter() - overall_start) * 1000
                last_result = probe._build_result(
                    status=HealthStatus.FAIL,
                    output=str(e),
                    latency_ms=duration_ms
                )

            if attempt < total_attempts - 1 and retry_delay > 0:
                for observer in self.observers:
                    observer.on_probe_retry(
                        probe.name,
                        attempt +1,
                        last_result.status.value if last_result else "fail",
                        retry_delay,
                    )
                time.sleep(retry_delay)

        if last_result:
            for observer in self.observers:
                observer.on_probe_result(last_result)
        return last_result

class AsyncRunner(BaseRunner):
    def __init__(
        self,
        probes: List[BaseProbe],
        global_timeout: float = 30.0,
        executor: Optional[Executor] = None,
        version: str = "1.0.0",
        redact_sensitive: bool = False,
        default_retry_attempts: int = 0,
        default_retry_delay: float = 0.0,
        observers: Optional[List["ProbeObserver"]] = None,
    ):
        super().__init__(
            probes=probes,
            global_timeout=global_timeout,
            version=version,
            default_retry_attempts=default_retry_attempts,
            default_retry_delay=default_retry_delay,
            observers=observers,
        )
        self.executor = executor
        self.redact_sensitive = redact_sensitive

    async def execute(self) -> Dict[str, Any]:
        suite_start = time.perf_counter()
        probe_count = len(self.probes)

        tasks = []
        for probe in self.probes:
            if inspect.iscoroutinefunction(probe.check):
                coro = probe.run(
                    default_retry_attempts=self.default_retry_attempts,
                    default_retry_delay=self.default_retry_delay,
                    observers=self.observers,
                )
            else:
                coro = self._run_sync_in_thread(probe)

            tasks.append(self._wrap_probe_context(probe, coro))

        try:
            async with async_timeout(self.global_timeout):
                results = await asyncio.gather(*tasks, return_exceptions=True)
        except TimeoutError:
            return {
                "status": HealthStatus.FAIL,
                "version": self.version,
                "checks": {},
                "output": f"Global timeout exceeded ({self.global_timeout}s)"
            }

        suite_duration_ms = (time.perf_counter() - suite_start) * 1000
        clean_results = self._clean_results(results)
        result = aggregate_results(clean_results, version=self.version, redact_sensitive=self.redact_sensitive)

        if not self.redact_sensitive:
            result["metrics"] = {
                "duration_ms": round(suite_duration_ms, 2),
                "probe_count": probe_count,
                "global_timeout_ms": round(self.global_timeout * 1000, 2),
            }

        for observer in self.observers:
            try:
                observer.on_suite_complete(result, suite_duration_ms, probe_count)
            except Exception:
                pass

        return result

    async def _wrap_probe_context(self, probe: BaseProbe, coro) -> ProbeResult:
        try:
            return await coro
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            return _error_result(
                name=probe.name,
                output=f"Runner Exception: {str(e)}",
                critical=probe.critical,
            )

    async def _run_sync_in_thread(self, probe: BaseProbe) -> ProbeResult:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, self._run_sync_probe, probe)

    def _clean_results(self, results) -> List[ProbeResult]:
        clean = []
        for res in results:
            if isinstance(res, ProbeResult):
                clean.append(res)
            elif isinstance(res, Exception):
                clean.append(_error_result(
                    name="runner",
                    output=f"Runner Exception: {str(res)}"
                ))
        return clean


class SyncRunner(BaseRunner):
    def __init__(
        self,
        probes: List[BaseProbe],
        global_timeout: float = 30.0,
        version: str = "1.0.0",
        executor: Optional[Executor] = None,
        redact_sensitive: bool = False,
        default_retry_attempts: int = 0,
        default_retry_delay: float = 0.0,
        observers: Optional[List["ProbeObserver"]] = None,
    ):
        super().__init__(
            probes=probes,
            global_timeout=global_timeout,
            version=version,
            default_retry_attempts=default_retry_attempts,
            default_retry_delay=default_retry_delay,
            observers=observers,
        )
        self.executor = executor
        self.redact_sensitive = redact_sensitive

    def execute(self) -> Dict[str, Any]:
        suite_start = time.perf_counter()
        probe_count = len(self.probes)

        sync_probes = []
        async_probes = []

        for probe in self.probes:
            if inspect.iscoroutinefunction(probe.check):
                async_probes.append(probe)
            else:
                sync_probes.append(probe)

        results = []

        if self.executor is not None:
            self._run_all_probes(self.executor, sync_probes, async_probes, results)
        else:
            with ThreadPoolExecutor() as executor:
                self._run_all_probes(executor, sync_probes, async_probes, results)

        suite_duration_ms = (time.perf_counter() - suite_start) * 1000
        result = aggregate_results(results, version=self.version, redact_sensitive=self.redact_sensitive)

        if not self.redact_sensitive:
            result["metrics"] = {
                "duration_ms": round(suite_duration_ms, 2),
                "probe_count": probe_count,
                "global_timeout_ms": round(self.global_timeout * 1000, 2),
            }

        for observer in self.observers:
            try:
                observer.on_suite_complete(result, suite_duration_ms, probe_count)
            except Exception:
                pass

        return result

    def _run_all_probes(self, executor, sync_probes, async_probes, results):
        deadline = time.monotonic() + self.global_timeout

        future_to_probe = {}

        for probe in sync_probes:
            future = executor.submit(self._run_sync_probe, probe, deadline)
            future_to_probe[future] = probe.name

        if async_probes:
            future = executor.submit(self._run_async_batch, async_probes)
            future_to_probe[future] = "__async_batch__"

        pending = set(future_to_probe.keys())

        while pending:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                for future in pending:
                    probe_name = future_to_probe[future]
                    future.cancel()
                    if probe_name == "__async_batch__":
                        for p in async_probes:
                            results.append(_error_result(
                                name=p.name,
                                output=f"Global timeout exceeded ({self.global_timeout}s)",
                                critical=p.critical,
                            ))
                    else:
                        results.append(_error_result(
                            name=probe_name,
                            output=f"Global timeout exceeded ({self.global_timeout}s)",
                        ))
                break

            done, pending = wait(pending, timeout=remaining, return_when=FIRST_COMPLETED)

            for future in done:
                probe_name = future_to_probe[future]
                try:
                    res = future.result(timeout=0)
                    if isinstance(res, list):
                        results.extend(res)
                    else:
                        results.append(res)
                except Exception as e:
                    if probe_name == "__async_batch__":
                        for p in async_probes:
                            results.append(_error_result(
                                name=p.name,
                                output=f"Probe execution failed: {e}",
                                critical=p.critical,
                            ))
                    else:
                        results.append(_error_result(
                            name=probe_name,
                            output=f"Probe execution failed: {e}",
                        ))

    def _run_async_batch(self, probes: List[BaseProbe]) -> List[ProbeResult]:
        async def batch():
            return await asyncio.gather(*[
                p.run(
                    default_retry_attempts=self.default_retry_attempts,
                    default_retry_delay=self.default_retry_delay,
                    observers=self.observers,
                ) for p in probes
            ])

        return asyncio.run(batch())
