from __future__ import annotations

import logging
import time
import asyncio
import inspect
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, List, Optional

logger = logging.getLogger(__name__)

from castana._compat import async_timeout
from castana.domain import ProbeResult, HealthStatus
from castana.exceptions import WarnCondition

if TYPE_CHECKING:
    from castana.observers.base import ProbeObserver


class BaseProbe(ABC):
    def __init__(
        self,
        name: str,
        timeout: float = 5.0,
        component_type: str = "component",
        critical: bool = True,
        retry_attempts: int = 0,
        retry_delay: float = 0.0,
    ):
        if not isinstance(name, str):
            raise TypeError(f"name must be str, got {type(name).__name__}")
        if not name:
            raise ValueError("name cannot be empty")

        if not isinstance(timeout, (int, float)):
            raise TypeError(f"timeout must be number, got {type(timeout).__name__}")
        if timeout <= 0:
            raise ValueError(f"timeout must be positive, got {timeout}")

        if not isinstance(component_type, str):
            raise TypeError(f"component_type must be str, got {type(component_type).__name__}")

        if not isinstance(critical, bool):
            raise TypeError(f"critical must be bool, got {type(critical).__name__}")

        if not isinstance(retry_attempts, int):
            raise TypeError(f"retry_attempts must be int, got {type(retry_attempts).__name__}")
        if retry_attempts < 0:
            raise ValueError(f"retry_attempts must be non-negative, got {retry_attempts}")

        if not isinstance(retry_delay, (int, float)):
            raise TypeError(f"retry_delay must be number, got {type(retry_delay).__name__}")
        if retry_delay < 0:
            raise ValueError(f"retry_delay must be non-negative, got {retry_delay}")

        self._name = name
        self.timeout = float(timeout)
        self.component_type = component_type
        self.critical = critical
        self.retry_attempts = retry_attempts
        self.retry_delay = float(retry_delay)

    @property
    def name(self) -> str:
        return self._name

    async def run(
        self,
        default_retry_attempts: int = 0,
        default_retry_delay: float = 0.0,
        observers: Optional[List["ProbeObserver"]] = None,
    ) -> ProbeResult:
        observers = observers or []

        retry_attempts = self.retry_attempts if self.retry_attempts > 0 else default_retry_attempts
        retry_delay = self.retry_delay if self.retry_delay > 0 else default_retry_delay

        total_attempts = 1 + retry_attempts
        last_result = None
        overall_start = time.perf_counter()

        for attempt in range(total_attempts):
            for observer in observers:
                try:
                    observer.on_probe_start(self.name, attempt)
                except Exception:
                    pass

            start = time.perf_counter()
            try:
                async with async_timeout(self.timeout):
                    if inspect.iscoroutinefunction(self.check):
                        result = await self.check()
                    else:
                        result = await asyncio.to_thread(self.check)

                duration_ms = (time.perf_counter() - overall_start) * 1000
                probe_result = self._build_result(
                    status=HealthStatus.PASS,
                    observed_value=result,
                    latency_ms=duration_ms
                )
                for observer in observers:
                    try:
                        observer.on_probe_result(probe_result)
                    except Exception:
                        pass
                return probe_result

            except TimeoutError:
                duration_ms = (time.perf_counter() - overall_start) * 1000
                last_result = self._build_result(
                    status=HealthStatus.FAIL,
                    output=f"Timeout after {self.timeout}s",
                    latency_ms=duration_ms
                )
                for observer in observers:
                    try:
                        observer.on_probe_timeout(self.name, self.timeout)
                    except Exception:
                        pass

            except WarnCondition as w:
                duration_ms = (time.perf_counter() - overall_start) * 1000
                probe_result = self._build_result(
                    status=HealthStatus.WARN,
                    output=str(w),
                    latency_ms=duration_ms
                )
                for observer in observers:
                    try:
                        observer.on_probe_result(probe_result)
                    except Exception:
                        pass
                return probe_result

            except Exception as e:
                duration_ms = (time.perf_counter() - overall_start) * 1000
                last_result = self._build_result(
                    status=HealthStatus.FAIL,
                    output=str(e),
                    latency_ms=duration_ms
                )

            if attempt < total_attempts - 1 and retry_delay > 0:
                for observer in observers:
                    try:
                        observer.on_probe_retry(
                            self.name,
                            attempt +1,
                            last_result.status.value if last_result else "fail",
                            retry_delay,
                        )
                    except Exception:
                        pass
                await asyncio.sleep(retry_delay)

        if last_result:
            for observer in observers:
                observer.on_probe_result(last_result)
        return last_result

    @abstractmethod
    def check(self) -> Any:
        pass

    def _build_result(
        self,
        status: HealthStatus,
        output: Optional[str] = None,
        observed_value: Any = None,
        latency_ms: float = 0,
    ) -> ProbeResult:
        observed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

        return ProbeResult(
            status=status,
            name=self.name,
            component_type=self.component_type,
            observed_value=observed_value,
            output=output,
            time=observed_at,
            metadata=MappingProxyType({"latency_ms": round(latency_ms, 2)}),
            critical=self.critical,
        )


class _SyncFunctionProbe(BaseProbe):
    def __init__(self, fn, name, timeout, component_type, critical, retry_attempts, retry_delay):
        self._fn = fn
        super().__init__(
            name=name,
            timeout=timeout,
            component_type=component_type,
            critical=critical,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
        )

    def check(self) -> Any:
        return self._fn()


class _AsyncFunctionProbe(BaseProbe):
    def __init__(self, fn, name, timeout, component_type, critical, retry_attempts, retry_delay):
        self._fn = fn
        super().__init__(
            name=name,
            timeout=timeout,
            component_type=component_type,
            critical=critical,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
        )

    async def check(self) -> Any:
        return await self._fn()


class FunctionProbe:
    def __new__(
        cls,
        fn: callable,
        name: str,
        timeout: float = 5.0,
        component_type: str = "component",
        critical: bool = True,
        retry_attempts: int = 0,
        retry_delay: float = 0.0,
    ):
        if inspect.iscoroutinefunction(fn):
            return _AsyncFunctionProbe(
                fn=fn,
                name=name,
                timeout=timeout,
                component_type=component_type,
                critical=critical,
                retry_attempts=retry_attempts,
                retry_delay=retry_delay,
            )
        else:
            return _SyncFunctionProbe(
                fn=fn,
                name=name,
                timeout=timeout,
                component_type=component_type,
                critical=critical,
                retry_attempts=retry_attempts,
                retry_delay=retry_delay,
            )
