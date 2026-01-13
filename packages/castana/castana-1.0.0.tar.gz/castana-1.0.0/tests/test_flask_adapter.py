import pytest
import time

from castana import HealthCheck
from castana.adapters.flask import FlaskHealth, MEDIA_TYPE_HEALTH_JSON
from castana.probes.base import BaseProbe


class OkProbe(BaseProbe):
    def check(self):
        return "ok"


class FailProbe(BaseProbe):
    def check(self):
        raise RuntimeError("boom")


class CountingProbe(BaseProbe):
    """Probe that counts how many times it's been called."""
    call_count = 0
    
    def check(self):
        CountingProbe.call_count += 1
        return f"call_{CountingProbe.call_count}"


@pytest.fixture
def flask_app():
    flask = pytest.importorskip("flask")
    app = flask.Flask(__name__)
    app.testing = True
    return app


def test_flask_adapter_returns_200_on_pass(flask_app):
    health = HealthCheck(name="svc")
    health.add_probe(OkProbe(name="ok"))

    FlaskHealth(flask_app, health_check=health, url_prefix="/health", name="health_ok")

    client = flask_app.test_client()
    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith(MEDIA_TYPE_HEALTH_JSON)
    payload = resp.get_json()
    assert payload["status"] in ("pass", "warn")


def test_flask_adapter_returns_503_on_fail(flask_app):
    health = HealthCheck(name="svc")
    health.add_probe(FailProbe(name="db"))

    FlaskHealth(flask_app, health_check=health, url_prefix="/health", name="health_fail")

    client = flask_app.test_client()
    resp = client.get("/health")

    assert resp.status_code == 503
    payload = resp.get_json()
    assert payload["status"] == "fail"
    assert payload["checks"]["db"][0]["output"] == "boom"


def test_flask_adapter_handles_unconfigured_as_503(flask_app):
    FlaskHealth(flask_app, health_check=None, url_prefix="/health", name="health_none")

    client = flask_app.test_client()
    resp = client.get("/health")

    assert resp.status_code == 503
    payload = resp.get_json()
    assert payload["status"] == "fail"
    assert "not configured" in payload["output"]


def test_flask_adapter_returns_fail_json_on_runner_crash(flask_app, monkeypatch):
    health = HealthCheck(name="svc")
    health.add_probe(OkProbe(name="ok"))

    from castana.adapters import flask as flask_adapter

    def explode(self):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(flask_adapter.SyncRunner, "execute", explode)

    FlaskHealth(flask_app, health_check=health, url_prefix="/health", name="health_crash")

    client = flask_app.test_client()
    resp = client.get("/health")

    assert resp.status_code == 503
    assert resp.headers["Content-Type"].startswith(MEDIA_TYPE_HEALTH_JSON)
    payload = resp.get_json()
    assert payload["status"] == "fail"
    assert "kaboom" in payload["output"]


def test_flask_adapter_caches_results(flask_app):
    """Verify that cache_ttl prevents repeated probe execution."""
    # Reset counter
    CountingProbe.call_count = 0
    
    health = HealthCheck(name="svc", cache_ttl=1.0)  # 1 second cache
    health.add_probe(CountingProbe(name="counter"))

    FlaskHealth(flask_app, health_check=health, url_prefix="/health", name="health_cache")

    client = flask_app.test_client()
    
    # First request - should execute probe
    resp1 = client.get("/health")
    assert resp1.status_code == 200
    assert CountingProbe.call_count == 1
    
    # Second request - should return cached result
    resp2 = client.get("/health")
    assert resp2.status_code == 200
    assert CountingProbe.call_count == 1  # Still 1, not 2
    
    # Third request - should still be cached
    resp3 = client.get("/health")
    assert CountingProbe.call_count == 1  # Still 1


def test_flask_adapter_cache_expires(flask_app):
    """Verify that cache expires after TTL."""
    # Reset counter
    CountingProbe.call_count = 0
    
    health = HealthCheck(name="svc", cache_ttl=0.1)  # 100ms cache
    health.add_probe(CountingProbe(name="counter"))

    FlaskHealth(flask_app, health_check=health, url_prefix="/health", name="health_expire")

    client = flask_app.test_client()
    
    # First request
    client.get("/health")
    assert CountingProbe.call_count == 1
    
    # Wait for cache to expire
    time.sleep(0.15)
    
    # Second request - cache expired, should re-execute
    client.get("/health")
    assert CountingProbe.call_count == 2
