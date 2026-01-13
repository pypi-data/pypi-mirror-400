"""
Base observer interface for health check observability.
"""
from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from castana.domain import ProbeResult


class ProbeObserver(ABC):

    def on_probe_start(self, probe_name: str, attempt: int) -> None:
        pass

    def on_probe_result(self, result: "ProbeResult") -> None:
        pass

    def on_probe_retry(
        self,
        probe_name: str,
        attempt: int,
        previous_status: str,
        delay: float,
    ) -> None:
        pass

    def on_probe_timeout(self, probe_name: str, timeout_seconds: float) -> None:
        pass

    def on_suite_complete(
        self,
        result: Dict[str, Any],
        duration_ms: float,
        probe_count: int,
    ) -> None:
        pass
