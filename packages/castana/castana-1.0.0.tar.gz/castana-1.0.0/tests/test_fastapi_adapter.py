import pytest
import time
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient

from castana import HealthCheck, BaseProbe, HealthStatus
from castana.adapters.fastapi import create_health_router
from castana.adapters.base import MEDIA_TYPE_HEALTH_JSON

class OkProbe(BaseProbe):
    async def check(self):
        return "ok"

class FailProbe(BaseProbe):
    async def check(self):
        raise RuntimeError("boom")

class CountingProbe(BaseProbe):
    call_count = 0
    async def check(self):
        CountingProbe.call_count += 1
        return f"call_{CountingProbe.call_count}"

@pytest.fixture
def api_app():
    return FastAPI()

def test_fastapi_adapter_returns_200_on_pass(api_app):
    health = HealthCheck(name="svc")
    health.add_probe(OkProbe(name="ok"))

    router = create_health_router(health)
    api_app.include_router(router)  # Already includes /health path

    client = TestClient(api_app)
    resp = client.get("/health")

    assert resp.status_code == 200
    assert MEDIA_TYPE_HEALTH_JSON in resp.headers["Content-Type"]
    payload = resp.json()
    assert payload["status"] == "pass"

def test_fastapi_adapter_returns_503_on_fail(api_app):
    health = HealthCheck(name="svc")
    health.add_probe(FailProbe(name="db"))

    router = create_health_router(health)
    api_app.include_router(router)

    client = TestClient(api_app)
    resp = client.get("/health")

    assert resp.status_code == 503
    payload = resp.json()
    assert payload["status"] == "fail"
    assert payload["checks"]["db"][0]["output"] == "boom"

def test_fastapi_adapter_runner_crash(api_app, monkeypatch):
    health = HealthCheck(name="svc")
    health.add_probe(OkProbe(name="ok"))

    from castana.adapters import fastapi as fastapi_adapter
    
    async def explode(self):
        raise RuntimeError("kaboom")

    # Mock AsyncRunner.execute
    monkeypatch.setattr(fastapi_adapter.AsyncRunner, "execute", explode)

    router = create_health_router(health)
    api_app.include_router(router)

    client = TestClient(api_app)
    resp = client.get("/health")

    assert resp.status_code == 503
    payload = resp.json()
    assert payload["status"] == "fail"

def test_fastapi_liveness_readiness(api_app):
    health = HealthCheck(name="svc")
    health.add_probe(OkProbe(name="live_probe"), groups=["liveness"])
    health.add_probe(FailProbe(name="ready_probe"), groups=["readiness"])
    
    # include_live_ready=True should create /live and /ready under the router's path
    router = create_health_router(health, include_live_ready=True)
    api_app.include_router(router)

    client = TestClient(api_app)

    # 1. /health/live should PASS (ignoring the fail probe)
    resp_live = client.get("/health/live")
    assert resp_live.status_code == 200
    assert resp_live.json()["status"] == "pass"
    assert "live_probe" in resp_live.json()["checks"]
    assert "ready_probe" not in resp_live.json()["checks"]

    # 2. /health/ready should FAIL
    resp_ready = client.get("/health/ready")
    assert resp_ready.status_code == 503
    assert resp_ready.json()["status"] == "fail"
    assert "ready_probe" in resp_ready.json()["checks"]

    # 3. /health should FAIL (includes ALL probes by default)
    resp_all = client.get("/health")
    assert resp_all.status_code == 503
    assert resp_all.json()["status"] == "fail"

def test_fastapi_cache(api_app):
    CountingProbe.call_count = 0
    health = HealthCheck(name="svc", cache_ttl=1.0)
    health.add_probe(CountingProbe(name="counter"))

    router = create_health_router(health)
    api_app.include_router(router)
    client = TestClient(api_app)

    # 1st call
    client.get("/health")
    assert CountingProbe.call_count == 1

    # 2nd call (cached)
    client.get("/health")
    assert CountingProbe.call_count == 1

    # Expire cache
    time.sleep(1.1)

    # 3rd call
    client.get("/health")
    assert CountingProbe.call_count == 2
