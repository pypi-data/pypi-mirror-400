"""
Metrics integrations for Castana.

This module provides optional metrics integrations for health check observability.
All metrics implementations use the observer pattern and require optional dependencies.

Available observers:
    - PrometheusObserver: Prometheus metrics (requires prometheus-client)

Example:
    from castana import HealthCheck
    from castana.metrics.prometheus import PrometheusObserver

    metrics = PrometheusObserver(namespace="myapp")
    health = HealthCheck(observers=[metrics])
"""
# Note: We don't import PrometheusObserver here to avoid requiring prometheus-client
# Users should import directly: from castana.metrics.prometheus import PrometheusObserver

__all__ = []
