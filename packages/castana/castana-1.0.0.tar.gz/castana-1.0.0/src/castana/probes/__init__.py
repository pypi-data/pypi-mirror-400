"""
Castana health check probes.

Probes are imported lazily to avoid requiring all optional dependencies.
Import the specific probe you need:

    from castana.probes.http import HttpProbe
    from castana.probes.redis import RedisProbe
    from castana.probes.sql import PostgresProbe, SQLDriverType
    from castana.probes.system import DiskProbe, MemoryProbe
    from castana.probes.base import BaseProbe

Or use the convenience imports (may raise ImportError if deps missing):

    from castana.probes import HttpProbe  # requires: pip install castana[http]
"""

from castana.probes.base import BaseProbe, FunctionProbe

# Lazy imports - these are defined as functions that import on first access
# This allows `from castana.probes import X` to work while deferring the actual import

def __getattr__(name: str):
    """Lazy import probes to avoid loading optional dependencies."""
    
    if name == "DiskProbe":
        from castana.probes.system import DiskProbe
        return DiskProbe
    
    if name == "MemoryProbe":
        from castana.probes.system import MemoryProbe
        return MemoryProbe
    
    if name == "RedisProbe":
        from castana.probes.redis import RedisProbe
        return RedisProbe
    
    if name == "PostgresProbe":
        from castana.probes.sql import PostgresProbe
        return PostgresProbe
    
    if name == "SQLDriverType":
        from castana.probes.sql import SQLDriverType
        return SQLDriverType
    
    if name == "HttpProbe":
        from castana.probes.http import HttpProbe
        return HttpProbe
    
    raise AttributeError(f"module 'castana.probes' has no attribute {name!r}")


__all__ = [
    "BaseProbe",
    "FunctionProbe",
    "DiskProbe",
    "MemoryProbe",
    "RedisProbe",
    "PostgresProbe",
    "SQLDriverType",
    "HttpProbe",
]

def __dir__():
    return __all__
