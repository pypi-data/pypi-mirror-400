from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable, List, Optional

from fastapi import APIRouter, Response, Request
from fastapi.responses import JSONResponse

from castana.main import HealthCheck
from castana.runner import AsyncRunner
from castana.adapters.base import (
    MEDIA_TYPE_HEALTH_JSON,
    build_error_result,
    get_http_status_code,
    get_runner_kwargs,
)


def _create_health_endpoint(
    health_check: HealthCheck,
    groups: Optional[List[str]] = None,
) -> Callable:
    async def endpoint(request: Request, response: Response):
        async def run_probes():
            probes = health_check.get_probes(groups=groups)
            runner_kwargs = get_runner_kwargs(health_check)
            runner = AsyncRunner(probes=probes, **runner_kwargs)
            return await runner.execute()

        try:
            result = await health_check.async_try_get_or_run(run_probes)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            result = build_error_result(health_check, e)

        status_code = get_http_status_code(result["status"])
        response.status_code = status_code
        response.headers["Content-Type"] = MEDIA_TYPE_HEALTH_JSON
        return result

    return endpoint


def create_health_router(
    health_check: HealthCheck,
    path: str = "/health",
    include_live_ready: bool = False,
) -> APIRouter:
    router = APIRouter()

    responses = {
        200: {"content": {MEDIA_TYPE_HEALTH_JSON: {}}},
        503: {"content": {MEDIA_TYPE_HEALTH_JSON: {}}},
    }

    router.add_api_route(
        path,
        _create_health_endpoint(health_check, groups=None),
        methods=["GET"],
        response_class=JSONResponse,
        responses=responses,
    )

    if include_live_ready:
        router.add_api_route(
            f"{path}/live",
            _create_health_endpoint(health_check, groups=["liveness"]),
            methods=["GET"],
            response_class=JSONResponse,
            responses=responses,
        )

        router.add_api_route(
            f"{path}/ready",
            _create_health_endpoint(health_check, groups=["readiness"]),
            methods=["GET"],
            response_class=JSONResponse,
            responses=responses,
        )

    return router


class HealthRouter:
    def __init__(self, health_check: HealthCheck, path: str = "/health"):
        self.health_check = health_check
        self.path = path
        self.router = create_health_router(health_check, path)


def create_health_lifespan(health_check: HealthCheck):
    @asynccontextmanager
    async def lifespan(app) -> AsyncIterator[None]:
        yield
        health_check.shutdown(wait=True)

    return lifespan
