from __future__ import annotations

import asyncio
import threading
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Callable, Coroutine, Dict, List, Optional, Any, Set

from castana.probes.base import BaseProbe

if TYPE_CHECKING:
    from castana.observers.base import ProbeObserver


class HealthCheck:
    def __init__(
        self,
        name: str = "app",
        version: str = "1.0.0",
        global_timeout: float = 30.0,
        max_workers: Optional[int] = None,
        cache_ttl: Optional[float] = None,
        redact_sensitive: bool = False,
        default_retry_attempts: int = 0,
        default_retry_delay: float = 0.0,
        observers: Optional[List["ProbeObserver"]] = None,
    ):
        if global_timeout <= 0:
            raise ValueError("global_timeout must be positive")

        if max_workers is not None and max_workers <= 0:
            raise ValueError("max_workers must be positive")

        if cache_ttl is not None and cache_ttl < 0:
            raise ValueError("cache_ttl must be non-negative")

        if default_retry_attempts < 0:
            raise ValueError("default_retry_attempts must be non-negative")

        if default_retry_delay < 0:
            raise ValueError("default_retry_delay must be non-negative")

        self.name = name
        self.version = version
        self.global_timeout = global_timeout
        self.cache_ttl = cache_ttl
        self.redact_sensitive = redact_sensitive
        self.default_retry_attempts = default_retry_attempts
        self.default_retry_delay = default_retry_delay
        self.probes: Dict[str, BaseProbe] = {}
        self.probe_groups: Dict[str, Set[str]] = {}

        if max_workers:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
        else:
            self.executor = None

        self._cache_lock = threading.Lock()
        self._async_cache_lock = None
        self._cached_result = None
        self._cache_timestamp = 0.0
        self._is_shutdown = False
        self._atexit_registered = False
        self._sync_api_used = False
        self._async_api_used = False
        self._warned_mixed = False
        self.observers = list(observers) if observers else []

    def _get_async_lock(self):
        if self._async_cache_lock is None:
            self._async_cache_lock = asyncio.Lock()
        return self._async_cache_lock

    def add_observer(self, observer: "ProbeObserver"):
        self.observers.append(observer)

    def add_probe(self, probe: BaseProbe, groups: Optional[List[str]] = None):
        if probe.name in self.probes:
            raise ValueError(f"Probe '{probe.name}' already registered")

        self.probes[probe.name] = probe
        self.probe_groups[probe.name] = set(groups) if groups else {"__all__"}

    def add_probes(self, probes: List[BaseProbe], groups: Optional[List[str]] = None):
        for probe in probes:
            self.add_probe(probe, groups=groups)

    def probe(
        self,
        name: str,
        timeout: float = 5.0,
        component_type: str = "component",
        critical: bool = True,
        retry_attempts: int = 0,
        retry_delay: float = 0.0,
        groups: Optional[List[str]] = None,
    ) -> Callable:
        from castana.probes.base import FunctionProbe

        def decorator(fn: Callable) -> Callable:
            probe_instance = FunctionProbe(
                fn=fn,
                name=name,
                timeout=timeout,
                component_type=component_type,
                critical=critical,
                retry_attempts=retry_attempts,
                retry_delay=retry_delay,
            )
            self.add_probe(probe_instance, groups=groups)
            return fn
        return decorator

    def get_probes(self, groups: Optional[List[str]] = None) -> List[BaseProbe]:
        if groups is None:
            return list(self.probes.values())

        target_groups = set(groups) | {"__all__"}
        return [
            probe for name, probe in self.probes.items()
            if self.probe_groups[name] & target_groups
        ]

    def try_get_or_run(self, run_fn) -> Dict[str, Any]:
        self._sync_api_used = True

        if not self.cache_ttl or self._is_shutdown:
            return run_fn()

        if not self._warned_mixed and self._sync_api_used and self._async_api_used:
            self._warned_mixed = True
            warnings.warn(
                "HealthCheck used in both sync and async contexts",
                RuntimeWarning,
                stacklevel=2,
            )

        with self._cache_lock:
            if self._cached_result is not None:
                age = time.monotonic() - self._cache_timestamp
                if age < self.cache_ttl:
                    return self._cached_result

            result = run_fn()
            self._cached_result = result
            self._cache_timestamp = time.monotonic()
            return result

    async def async_try_get_or_run(
        self,
        run_fn: Callable[[], Coroutine[Any, Any, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        self._async_api_used = True

        if not self.cache_ttl or self._is_shutdown:
            return await run_fn()

        if not self._warned_mixed and self._async_api_used and self._sync_api_used:
            self._warned_mixed = True
            warnings.warn(
                "HealthCheck used in both sync and async contexts",
                RuntimeWarning,
                stacklevel=2,
            )

        async with self._get_async_lock():
            if self._cached_result is not None:
                age = time.monotonic() - self._cache_timestamp
                if age < self.cache_ttl:
                    return self._cached_result

            result = await run_fn()
            self._cached_result = result
            self._cache_timestamp = time.monotonic()
            return result

    def shutdown(self, wait: bool = False):
        self._is_shutdown = True

        executor = self.executor
        self.executor = None

        with self._cache_lock:
            self._cached_result = None
            self._cache_timestamp = 0.0

        if executor:
            executor.shutdown(wait=wait)
