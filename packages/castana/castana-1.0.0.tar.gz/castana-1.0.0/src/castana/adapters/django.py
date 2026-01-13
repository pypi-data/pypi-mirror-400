from __future__ import annotations

from typing import List, Optional

from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views import View

from castana.domain import HealthStatus
from castana.main import HealthCheck
from castana.runner import SyncRunner
from castana.adapters.base import (
    MEDIA_TYPE_HEALTH_JSON,
    build_error_result,
    get_http_status_code,
    get_runner_kwargs,
    register_shutdown_handler,
)


class DjangoHealthView(View):
    health_check: Optional[HealthCheck] = None
    groups: Optional[List[str]] = None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if self.health_check is None:
            return JsonResponse(
                {
                    "status": HealthStatus.FAIL,
                    "checks": {},
                    "output": "Health checker not configured",
                },
                status=503,
                content_type=MEDIA_TYPE_HEALTH_JSON,
            )

        def run_probes():
            probes = self.health_check.get_probes(groups=self.groups)
            runner_kwargs = get_runner_kwargs(self.health_check)
            runner = SyncRunner(probes=probes, **runner_kwargs)
            return runner.execute()

        try:
            result = self.health_check.try_get_or_run(run_probes)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            result = build_error_result(self.health_check, e)

        status_code = get_http_status_code(result["status"])
        response = JsonResponse(result, status=status_code)
        response["Content-Type"] = MEDIA_TYPE_HEALTH_JSON
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response


def get_health_urlpatterns(
    health_check: HealthCheck,
    base_path: str = "health/",
    include_live_ready: bool = False,
):
    from django.urls import path

    patterns = [
        path(base_path, DjangoHealthView.as_view(health_check=health_check)),
    ]

    if include_live_ready:
        base = base_path.rstrip("/")
        patterns.extend([
            path(f"{base}/live", DjangoHealthView.as_view(
                health_check=health_check,
                groups=["liveness"],
            )),
            path(f"{base}/ready", DjangoHealthView.as_view(
                health_check=health_check,
                groups=["readiness"],
            )),
        ])

    return patterns


def register_shutdown(health_check: HealthCheck) -> None:
    register_shutdown_handler(health_check)
