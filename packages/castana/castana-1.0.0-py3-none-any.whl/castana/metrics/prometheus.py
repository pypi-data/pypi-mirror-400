"""
Prometheus metrics integration for Castana.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

from castana.observers.base import ProbeObserver

if TYPE_CHECKING:
    from castana.domain import ProbeResult


class PrometheusObserver(ProbeObserver):

    STATUS_VALUES = {"pass": 1.0, "warn": 0.5, "fail": 0.0}

    def __init__(self, namespace: str = "castana"):
        try:
            from prometheus_client import Counter, Gauge, Histogram
        except ImportError as e:
            raise ImportError(
                "prometheus_client is required for PrometheusObserver. "
                "Install it with: pip install prometheus-client"
            ) from e

        self.namespace = namespace

        self.probe_duration = Histogram(
            f"{namespace}_probe_duration_seconds",
            "Time spent executing health check probes",
            labelnames=["probe", "status"],
        )

        self.probe_status = Gauge(
            f"{namespace}_probe_status",
            "Current status of health check probe (1=pass, 0.5=warn, 0=fail)",
            labelnames=["probe"],
        )

        self.probe_total = Counter(
            f"{namespace}_probe_total",
            "Total number of probe executions",
            labelnames=["probe", "status"],
        )

        self.suite_duration = Histogram(
            f"{namespace}_suite_duration_seconds",
            "Time spent executing entire health check suite",
        )

        self.suite_status = Gauge(
            f"{namespace}_suite_status",
            "Overall health check status (1=pass, 0.5=warn, 0=fail)",
        )

    def on_probe_result(self, result: "ProbeResult") -> None:
        status_str = result.status.value if hasattr(result.status, "value") else str(result.status)

        latency_s = result.metadata.get("latency_ms", 0) / 1000
        self.probe_duration.labels(
            probe=result.name,
            status=status_str,
        ).observe(latency_s)

        status_value = self.STATUS_VALUES.get(status_str, 0.0)
        self.probe_status.labels(probe=result.name).set(status_value)

        self.probe_total.labels(probe=result.name, status=status_str).inc()

    def on_suite_complete(
        self,
        result: Dict[str, Any],
        duration_ms: float,
        probe_count: int,
    ) -> None:
        self.suite_duration.observe(duration_ms / 1000)

        status = result.get("status")
        status_str = status.value if status and hasattr(status, "value") else str(status)
        status_value = self.STATUS_VALUES.get(status_str, 0.0)
        self.suite_status.set(status_value)


__all__ = ["PrometheusObserver"]
