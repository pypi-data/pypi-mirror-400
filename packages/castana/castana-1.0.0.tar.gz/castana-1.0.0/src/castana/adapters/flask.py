from __future__ import annotations

from typing import Callable, List, Optional

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


def _create_health_view(
    health_check: HealthCheck,
    groups: Optional[List[str]] = None,
) -> Callable:
    def health_view():
        from flask import jsonify, make_response, request

        if health_check is None:
            response = make_response(
                jsonify(
                    {
                        "status": HealthStatus.FAIL,
                        "checks": {},
                        "output": "Health checker not configured",
                    }
                ),
                503,
            )
            response.headers["Content-Type"] = MEDIA_TYPE_HEALTH_JSON
            return response

        def run_probes():
            probes = health_check.get_probes(groups=groups)
            runner_kwargs = get_runner_kwargs(health_check)
            runner = SyncRunner(probes=probes, **runner_kwargs)
            return runner.execute()

        try:
            result = health_check.try_get_or_run(run_probes)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            result = build_error_result(health_check, e)

        status_code = get_http_status_code(result["status"])
        response = make_response(jsonify(result), status_code)
        response.headers["Content-Type"] = MEDIA_TYPE_HEALTH_JSON
        return response

    return health_view


class FlaskHealth:
    def __init__(
        self,
        app=None,
        health_check: Optional[HealthCheck] = None,
        url_prefix: str = "/health",
        name: str = "castana_health",
        include_live_ready: bool = False,
    ):
        self.health_check = health_check
        self.url_prefix = url_prefix
        self.name = name
        self.include_live_ready = include_live_ready

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        from flask import Blueprint

        bp = Blueprint(self.name, __name__)

        bp.add_url_rule(
            "/",
            "health",
            view_func=_create_health_view(self.health_check, groups=None),
            strict_slashes=False,
        )

        if self.include_live_ready:
            bp.add_url_rule(
                "/live",
                "liveness",
                view_func=_create_health_view(self.health_check, groups=["liveness"]),
                strict_slashes=False,
            )

            bp.add_url_rule(
                "/ready",
                "readiness",
                view_func=_create_health_view(self.health_check, groups=["readiness"]),
                strict_slashes=False,
            )

        app.register_blueprint(bp, url_prefix=self.url_prefix)

        if self.health_check is not None:
            register_shutdown_handler(self.health_check)


def create_health_blueprint(
    health_check: HealthCheck,
    name: str = "castana_health",
    url_prefix: str = "/health",
    include_live_ready: bool = False,
):
    from flask import Blueprint

    bp = Blueprint(name, __name__, url_prefix=url_prefix)

    bp.add_url_rule(
        "/",
        "health",
        view_func=_create_health_view(health_check, groups=None),
        strict_slashes=False,
    )

    if include_live_ready:
        bp.add_url_rule(
            "/live",
            "liveness",
            view_func=_create_health_view(health_check, groups=["liveness"]),
            strict_slashes=False,
        )

        bp.add_url_rule(
            "/ready",
            "readiness",
            view_func=_create_health_view(health_check, groups=["readiness"]),
            strict_slashes=False,
        )

    register_shutdown_handler(health_check)

    return bp
