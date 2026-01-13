try:
    from castana.adapters.fastapi import create_health_router, create_health_lifespan
except Exception:  # pragma: no cover
    create_health_router = None
    create_health_lifespan = None

try:
    from castana.adapters.flask import FlaskHealth, create_health_blueprint
except Exception:  # pragma: no cover
    FlaskHealth = None
    create_health_blueprint = None

try:
    from castana.adapters.django import DjangoHealthView, register_shutdown, get_health_urlpatterns
except Exception:  # pragma: no cover
    DjangoHealthView = None
    register_shutdown = None
    get_health_urlpatterns = None

__all__ = [
    "create_health_router",
    "create_health_lifespan",
    "FlaskHealth",
    "create_health_blueprint",
    "DjangoHealthView",
    "register_shutdown",
    "get_health_urlpatterns",
]

