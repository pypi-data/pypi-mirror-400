import asyncio
from typing import Any, Optional
from enum import Enum, auto

from castana.probes.base import BaseProbe


class SQLDriverType(Enum):
    ASYNCPG = auto()
    PSYCOPG_ASYNC = auto()
    PSYCOPG_SYNC = auto()
    SQLALCHEMY_ASYNC = auto()
    SQLALCHEMY_SYNC = auto()
    UNKNOWN = auto()


class PostgresProbe(BaseProbe):
    def __init__(
        self,
        conn: Any,
        name: str = "postgres",
        timeout: float = 5.0,
        query: str = "SELECT 1",
        driver: Optional[SQLDriverType] = None,
        critical: bool = True,
        retry_attempts: int = 0,
        retry_delay: float = 0.0,
    ):
        super().__init__(
            name,
            timeout,
            component_type="datastore",
            critical=critical,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
        )
        self.conn = conn
        self.query = query

        if driver is not None:
            self.driver_type = driver
        else:
            self.driver_type = self._detect_driver(conn)

        if self.driver_type == SQLDriverType.UNKNOWN:
            raise ValueError(
                f"Could not detect driver for connection type: {type(conn).__module__}.{type(conn).__name__}. "
                f"Pass `driver=SQLDriverType.XXX` explicitly."
            )

    def _detect_driver(self, conn: Any) -> SQLDriverType:
        try:
            import asyncpg
            if isinstance(conn, (asyncpg.Pool, asyncpg.Connection)):
                return SQLDriverType.ASYNCPG
        except ImportError:
            pass

        try:
            from sqlalchemy.ext.asyncio import AsyncEngine
            if isinstance(conn, AsyncEngine):
                return SQLDriverType.SQLALCHEMY_ASYNC
        except ImportError:
            pass

        try:
            from sqlalchemy.engine import Engine
            if isinstance(conn, Engine):
                return SQLDriverType.SQLALCHEMY_SYNC
        except ImportError:
            pass

        try:
            from psycopg import AsyncConnection
            if isinstance(conn, AsyncConnection):
                return SQLDriverType.PSYCOPG_ASYNC
        except ImportError:
            pass

        try:
            from psycopg import Connection
            if isinstance(conn, Connection):
                return SQLDriverType.PSYCOPG_SYNC
        except ImportError:
            pass

        try:
            from psycopg_pool import ConnectionPool, AsyncConnectionPool
            if isinstance(conn, AsyncConnectionPool):
                return SQLDriverType.PSYCOPG_ASYNC
            if isinstance(conn, ConnectionPool):
                return SQLDriverType.PSYCOPG_SYNC
        except ImportError:
            pass

        try:
            import psycopg2
            if isinstance(conn, psycopg2.extensions.connection):
                return SQLDriverType.PSYCOPG_SYNC
        except ImportError:
            pass

        try:
            from psycopg2 import pool as psycopg2_pool
            if isinstance(conn, (psycopg2_pool.ThreadedConnectionPool,
                                 psycopg2_pool.SimpleConnectionPool)):
                return SQLDriverType.PSYCOPG_SYNC
        except ImportError:
            pass

        return SQLDriverType.UNKNOWN

    async def check(self) -> Any:
        if self.driver_type in _ASYNC_HANDLERS:
            handler = _ASYNC_HANDLERS[self.driver_type]
            return await handler(self.conn, self.query)

        if self.driver_type in _SYNC_HANDLERS:
            handler = _SYNC_HANDLERS[self.driver_type]
            return await asyncio.to_thread(handler, self.conn, self.query)

        raise ValueError(f"No handler for driver type: {self.driver_type}")


async def _check_asyncpg(conn: Any, query: str) -> Any:
    return await conn.fetchval(query)


async def _check_sqlalchemy_async(conn: Any, query: str) -> Any:
    from sqlalchemy import text
    async with conn.connect() as connection:
        result = await connection.execute(text(query))
        return result.scalar()


async def _check_psycopg_async(conn: Any, query: str) -> Any:
    try:
        from psycopg_pool import AsyncConnectionPool
        if isinstance(conn, AsyncConnectionPool):
            async with conn.connection() as c:
                cur = await c.execute(query)
                row = await cur.fetchone()
                return row[0] if row else None
    except ImportError:
        pass

    cur = await conn.execute(query)
    row = await cur.fetchone()
    return row[0] if row else None


def _check_sqlalchemy_sync(conn: Any, query: str) -> Any:
    from sqlalchemy import text
    with conn.connect() as connection:
        return connection.execute(text(query)).scalar()


def _check_psycopg_sync(conn: Any, query: str) -> Any:
    try:
        from psycopg_pool import ConnectionPool
        if isinstance(conn, ConnectionPool):
            with conn.connection() as c:
                with c.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchone()
                    return row[0] if row else None
    except ImportError:
        pass

    if hasattr(conn, "getconn"):
        c = conn.getconn()
        try:
            with c.cursor() as cur:
                cur.execute(query)
                row = cur.fetchone()
                return row[0] if row else None
        finally:
            conn.putconn(c)
    else:
        with conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()
            return row[0] if row else None


_ASYNC_HANDLERS = {
    SQLDriverType.ASYNCPG: _check_asyncpg,
    SQLDriverType.SQLALCHEMY_ASYNC: _check_sqlalchemy_async,
    SQLDriverType.PSYCOPG_ASYNC: _check_psycopg_async,
}

_SYNC_HANDLERS = {
    SQLDriverType.SQLALCHEMY_SYNC: _check_sqlalchemy_sync,
    SQLDriverType.PSYCOPG_SYNC: _check_psycopg_sync,
}
