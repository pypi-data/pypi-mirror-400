import pytest
import inspect
from unittest.mock import MagicMock
from castana.probes.sql import PostgresProbe, SQLDriverType
from castana.probes.redis import RedisProbe

# --- Mocks for SQL Drivers ---

class MockAsyncpgPool:
    """Mock asyncpg pool."""
    async def fetchval(self, query):
        return 1

class MockPsycopg2Pool:
    """Mock psycopg2 pool."""
    def __init__(self):
        self._conn = MockPsycopg2Connection()
    
    def getconn(self):
        return self._conn
    
    def putconn(self, conn):
        pass

class MockPsycopg2Connection:
    """Mock psycopg2 connection."""
    def cursor(self):
        cursor = MagicMock()
        cursor.__enter__ = MagicMock(return_value=cursor)
        cursor.__exit__ = MagicMock(return_value=False)
        cursor.fetchone.return_value = (1,)
        return cursor

# --- Mocks for Redis ---

class MockRedisSync:
    def ping(self):
        return True

class MockRedisAsync:
    async def ping(self):
        return True

# --- Tests ---

def test_postgres_explicit_asyncpg_driver():
    """PostgresProbe with explicit ASYNCPG driver."""
    pool = MockAsyncpgPool()
    probe = PostgresProbe(conn=pool, driver=SQLDriverType.ASYNCPG)
    assert probe.driver_type == SQLDriverType.ASYNCPG
    assert inspect.iscoroutinefunction(probe.check)

def test_postgres_explicit_psycopg_sync_driver():
    """PostgresProbe with explicit PSYCOPG_SYNC driver."""
    pool = MockPsycopg2Pool()
    probe = PostgresProbe(conn=pool, driver=SQLDriverType.PSYCOPG_SYNC)
    assert probe.driver_type == SQLDriverType.PSYCOPG_SYNC

def test_postgres_unknown_driver_raises_error():
    """Unrecognized connection types raise error."""
    unknown_conn = object()
    with pytest.raises(ValueError) as exc_info:
        PostgresProbe(conn=unknown_conn)
    assert "Could not detect driver" in str(exc_info.value)
    assert "Pass `driver=SQLDriverType.XXX` explicitly" in str(exc_info.value)

def test_redis_detects_async_client():
    client = MockRedisAsync()
    probe = RedisProbe(client=client)
    assert probe.is_async_client is True

def test_redis_detects_sync_client():
    client = MockRedisSync()
    probe = RedisProbe(client=client)
    assert probe.is_async_client is False