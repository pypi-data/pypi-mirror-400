import os
import shutil
from typing import Any, Optional

from castana.probes.base import BaseProbe
from castana.exceptions import WarnCondition


def _get_default_disk_path() -> str:
    if os.name == 'nt':
        return os.environ.get('SystemDrive', 'C:') + '\\'
    return '/'


class DiskProbe(BaseProbe):
    def __init__(
        self,
        path: Optional[str] = None,
        name: str = "disk",
        timeout: float = 5.0,
        warning_mb: int = 1000,
        critical_mb: int = 100,
        critical: bool = True,
        retry_attempts: int = 0,
        retry_delay: float = 0.0,
    ):
        super().__init__(
            name,
            timeout=timeout,
            component_type="system",
            critical=critical,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
        )
        self.path = path if path is not None else _get_default_disk_path()
        self.warning_mb = warning_mb
        self.critical_mb = critical_mb

    def check(self) -> float:
        total, used, free = shutil.disk_usage(self.path)
        free_mb = free / (1024 * 1024)

        if free_mb < self.critical_mb:
            raise OSError(f"Disk space critical: {free_mb:.0f}MB < {self.critical_mb}MB")

        if free_mb < self.warning_mb:
            raise WarnCondition(f"Disk space low: {free_mb:.0f}MB < {self.warning_mb}MB")

        return round(free_mb, 2)


class MemoryProbe(BaseProbe):
    def __init__(
        self,
        name: str = "memory",
        timeout: float = 5.0,
        warning_percent: float = 85.0,
        critical_percent: float = 95.0,
        critical: bool = True,
        retry_attempts: int = 0,
        retry_delay: float = 0.0,
    ):
        super().__init__(
            name,
            timeout=timeout,
            component_type="system",
            critical=critical,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
        )
        self.warning_percent = warning_percent
        self.critical_percent = critical_percent

        try:
            import psutil
            self._psutil = psutil
        except ImportError:
            raise ImportError("MemoryProbe requires 'psutil'. Install it via: pip install castana[system]")

    def check(self) -> float:
        mem = self._psutil.virtual_memory()
        usage_percent = mem.percent

        if usage_percent > self.critical_percent:
            raise OSError(f"Memory critical: {usage_percent}%")

        if usage_percent > self.warning_percent:
            raise WarnCondition(f"Memory high: {usage_percent}%")

        return usage_percent
