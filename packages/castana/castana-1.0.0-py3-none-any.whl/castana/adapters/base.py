"""
Shared utilities for framework adapters.
"""
from __future__ import annotations

import atexit
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from castana.domain import HealthStatus

if TYPE_CHECKING:
    from castana.main import HealthCheck

MEDIA_TYPE_HEALTH_JSON = "application/health+json"


def get_http_status_code(health_status: HealthStatus) -> int:
    return 503 if health_status == HealthStatus.FAIL else 200


def build_error_result(health_check: "HealthCheck", exc: Exception) -> Dict[str, Any]:
    return {
        "status": HealthStatus.FAIL,
        "version": health_check.version,
        "checks": {},
        "output": f"Health check execution failed: {exc}",
    }


def get_runner_kwargs(health_check: "HealthCheck") -> Dict[str, Any]:
    return {
        "global_timeout": health_check.global_timeout,
        "executor": health_check.executor,
        "version": health_check.version,
        "redact_sensitive": health_check.redact_sensitive,
        "default_retry_attempts": health_check.default_retry_attempts,
        "default_retry_delay": health_check.default_retry_delay,
        "observers": health_check.observers,
    }


def get_endpoint_configs(
    include_live_ready: bool,
) -> List[Tuple[str, Optional[List[str]], str]]:
    endpoints = [("", None, "health")]

    if include_live_ready:
        endpoints.extend([
            ("/live", ["liveness"], "liveness"),
            ("/ready", ["readiness"], "readiness"),
        ])

    return endpoints


def register_shutdown_handler(health_check: "HealthCheck") -> None:
    if not health_check._atexit_registered:
        atexit.register(health_check.shutdown, wait=True)
        health_check._atexit_registered = True
