import json
import pytest

from django.conf import settings
from django.test import RequestFactory

from castana.main import HealthCheck
from castana.adapters.django import DjangoHealthView, register_shutdown
from castana.domain import HealthStatus
from castana.probes.base import BaseProbe


# Configure minimal Django settings for testing
if not settings.configured:
    settings.configure(
        DEFAULT_CHARSET='utf-8',
        DEBUG=True,
    )


class PassingProbe(BaseProbe):
    """Simple probe that always passes."""
    def check(self):
        return "ok"


class FailingProbe(BaseProbe):
    """Simple probe that always fails."""
    def check(self):
        raise RuntimeError("Database connection failed")


@pytest.fixture
def rf():
    """Django RequestFactory fixture."""
    return RequestFactory()


def test_django_adapter_returns_200_on_pass(rf):
    """Health check returns 200 when all probes pass."""
    health = HealthCheck()
    health.add_probe(PassingProbe(name="test"))

    view = DjangoHealthView.as_view(health_check=health)
    request = rf.get("/health")
    response = view(request)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/health+json"
    assert response["Cache-Control"] == "no-cache, no-store, must-revalidate"

    data = json.loads(response.content)
    assert data["status"] == HealthStatus.PASS


def test_django_adapter_returns_503_on_fail(rf):
    """Health check returns 503 when a probe fails."""
    health = HealthCheck()
    health.add_probe(FailingProbe(name="db"))

    view = DjangoHealthView.as_view(health_check=health)
    request = rf.get("/health")
    response = view(request)

    assert response.status_code == 503

    data = json.loads(response.content)
    assert data["status"] == HealthStatus.FAIL


def test_django_adapter_handles_unconfigured(rf):
    """Returns 503 when no HealthCheck is configured."""
    view = DjangoHealthView.as_view(health_check=None)
    request = rf.get("/health")
    response = view(request)

    assert response.status_code == 503

    data = json.loads(response.content)
    assert "not configured" in data["output"]


def test_django_adapter_returns_fail_json_on_runner_crash(rf, monkeypatch):
    """Unexpected runner crashes should still return health+json FAIL response."""
    health = HealthCheck()
    health.add_probe(PassingProbe(name="ok"))

    from castana.adapters import django as django_adapter

    def explode(self):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(django_adapter.SyncRunner, "execute", explode)

    view = DjangoHealthView.as_view(health_check=health)
    request = rf.get("/health")
    response = view(request)

    assert response.status_code == 503
    assert response["Content-Type"] == "application/health+json"
    data = json.loads(response.content)
    assert data["status"] == HealthStatus.FAIL
    assert "kaboom" in data["output"]


def test_django_register_shutdown():
    """register_shutdown sets the flag and doesn't double-register."""
    health = HealthCheck()

    assert not getattr(health, "_atexit_registered", False)

    register_shutdown(health)
    assert health._atexit_registered is True

    # Calling again should be a no-op (no error)
    register_shutdown(health)
    assert health._atexit_registered is True
