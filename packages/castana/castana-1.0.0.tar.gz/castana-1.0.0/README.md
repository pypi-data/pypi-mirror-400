# Castana

[![PyPI version](https://img.shields.io/pypi/v/castana.svg)](https://pypi.org/project/castana/)
[![Python versions](https://img.shields.io/pypi/pyversions/castana.svg)](https://pypi.org/project/castana/)
[![License](https://img.shields.io/pypi/l/castana.svg)](https://github.com/suaue/castana/blob/master/LICENSE)

Health check library for Python that handles async and sync probes together.

## Features

- Runs async and sync probes in the same health check
- Auto-detects database drivers (SQLAlchemy, asyncpg, psycopg, redis-py)
- IETF-compliant JSON responses
- No dependencies for core library
- Thread pool isolation for health checks

## Installation

```bash
pip install castana
```

Optional extras:

```bash
pip install "castana[http]"      # httpx for HTTP probes
pip install "castana[system]"    # psutil for memory checks
pip install "castana[redis]"     # redis-py
pip install "castana[postgres]"  # asyncpg/psycopg
pip install "castana[all]"       # all extras
```

## Basic Usage

```python
from castana import HealthCheck
from castana.probes import PostgresProbe, RedisProbe, DiskProbe

health = HealthCheck(name="my-service", version="1.0.0")

health.add_probe(PostgresProbe(conn=db_pool, name="db"))
health.add_probe(RedisProbe(client=redis_client, name="cache"))
health.add_probe(DiskProbe(warning_mb=500))
```

### FastAPI

```python
from fastapi import FastAPI
from castana.adapters.fastapi import create_health_router, create_health_lifespan

app = FastAPI(lifespan=create_health_lifespan(health))
app.include_router(create_health_router(health))
```

### Flask

```python
from flask import Flask
from castana.adapters.flask import FlaskHealth

app = Flask(__name__)
FlaskHealth(app, health_check=health)
```

### Django

urls.py:
```python
from django.urls import path
from castana.adapters.django import DjangoHealthView

urlpatterns = [
    path('health/', DjangoHealthView.as_view(health_check=health)),
]
```

apps.py:
```python
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        from castana.adapters.django import register_shutdown
        register_shutdown(health)
```

## Response Format

```json
{
  "status": "pass",
  "version": "1.0.0",
  "checks": {
    "db": [{
      "status": "pass",
      "componentType": "datastore",
      "observedValue": 1,
      "time": "2026-01-05T14:32:07+00:00",
      "metadata": {"latency_ms": 2.34}
    }]
  },
  "metrics": {
    "duration_ms": 2.5,
    "probe_count": 1
  }
}
```

HTTP status codes:
- `200` - status is `pass` or `warn`
- `503` - status is `fail`

## Available Probes

| Probe | Description | Dependencies |
|:------|:------------|:--------------|
| DiskProbe | Disk space check | None |
| MemoryProbe | Memory usage check | psutil |
| HttpProbe | HTTP endpoint check | httpx |
| RedisProbe | Redis ping check | redis-py |
| PostgresProbe | PostgreSQL check | asyncpg/psycopg/SQLAlchemy |

## Configuration

```python
health = HealthCheck(
    name="my-api",
    version="1.0.0",
    global_timeout=30.0,
    max_workers=4,
    cache_ttl=5.0,
)
```

**Options:**
- `name`: Service identifier
- `version`: Service version string
- `global_timeout`: Maximum time for entire health check suite
- `max_workers`: Dedicated thread pool size
- `cache_ttl`: Cache results for N seconds

### Caching

Set `cache_ttl` to cache results and reduce probe execution frequency:

```python
health = HealthCheck(cache_ttl=5.0)
```

Concurrent requests wait for the first result instead of all running probes.

### Critical Probes

By default, probe failures cause global `fail` status. Mark non-critical probes:

```python
health.add_probe(RedisProbe(client=redis, name="cache"))  # Critical
health.add_probe(DiskProbe(name="backup-disk", critical=False))  # Optional
```

### Kubernetes Probes

Separate liveness and readiness checks:

```python
health = HealthCheck()
health.add_probe(DiskProbe(name="disk"), groups=["liveness", "readiness"])
health.add_probe(PostgresProbe(conn=db_pool, name="db"), groups=["readiness"])
```

Enable separate endpoints:

```python
# FastAPI
app.include_router(create_health_router(health, include_live_ready=True))

# Flask
FlaskHealth(app, health_check=health, include_live_ready=True)

# Django
urlpatterns = get_health_urlpatterns(health, include_live_ready=True)
```

Endpoints:
- `/health` - All probes
- `/health/live` - Liveness group only
- `/health/ready` - Readiness group only

### Retry Logic

```python
health.add_probe(HttpProbe(
    name="external-api",
    url="https://api.example.com/health",
    retry_attempts=2,
    retry_delay=0.3,
))
```

Global defaults:

```python
health = HealthCheck(
    default_retry_attempts=3,
    default_retry_delay=1.0,
)
```

Failures and timeouts trigger retries. `WarnCondition` does not retry.

## Custom Probes

### Decorator

```python
from castana import HealthCheck, WarnCondition

health = HealthCheck()

@health.probe(name="config-check", timeout=1.0)
def check_config():
    if not config.IS_LOADED:
        raise ValueError("Config not loaded")
    return {"env": "production"}

@health.probe(name="db-ping")
async def check_database():
    return await db.ping()
```

### Class-based

```python
from castana import BaseProbe, WarnCondition

class QueueProbe(BaseProbe):
    def __init__(self, queue):
        super().__init__(name="queue-depth", timeout=5.0)
        self.queue = queue

    async def check(self):
        depth = await self.queue.get_depth()
        if depth > 1000:
            raise WarnCondition(f"Queue depth: {depth}")
        return depth

class DiskSpaceProbe(BaseProbe):
    def check(self):
        return "OK"
```

## License

MIT
