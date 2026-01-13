import pytest

from castana import HealthCheck


def test_healthcheck_rejects_non_positive_global_timeout():
    with pytest.raises(ValueError, match=r"global_timeout must be positive"):
        HealthCheck(global_timeout=0)

    with pytest.raises(ValueError, match=r"global_timeout must be positive"):
        HealthCheck(global_timeout=-1)


def test_healthcheck_rejects_non_positive_max_workers():
    with pytest.raises(ValueError, match=r"max_workers must be positive"):
        HealthCheck(max_workers=0)

    with pytest.raises(ValueError, match=r"max_workers must be positive"):
        HealthCheck(max_workers=-2)


def test_healthcheck_rejects_negative_cache_ttl():
    with pytest.raises(ValueError, match=r"cache_ttl must be non-negative"):
        HealthCheck(cache_ttl=-0.1)


def test_healthcheck_allows_zero_cache_ttl():
    HealthCheck(cache_ttl=0)
