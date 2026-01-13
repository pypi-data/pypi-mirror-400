import inspect
from typing import Any

from castana.probes.base import BaseProbe


class RedisProbe(BaseProbe):
    def __new__(
        cls,
        client: Any,
        name: str = "redis",
        timeout: float = 3.0,
        critical: bool = True,
        retry_attempts: int = 0,
        retry_delay: float = 0.0,
    ):
        is_async = inspect.iscoroutinefunction(client.ping)
        if is_async:
            instance = super().__new__(_AsyncRedisProbe)
        else:
            instance = super().__new__(_SyncRedisProbe)
        return instance

    def __init__(
        self,
        client: Any,
        name: str = "redis",
        timeout: float = 3.0,
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
        self.client = client
        self.is_async_client = inspect.iscoroutinefunction(client.ping)


class _AsyncRedisProbe(RedisProbe):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    async def check(self) -> str:
        if not await self.client.ping():
            raise ConnectionError("Redis ping failed (returned False)")
        return "PONG"


class _SyncRedisProbe(RedisProbe):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def check(self) -> str:
        if not self.client.ping():
            raise ConnectionError("Redis ping failed (returned False)")
        return "PONG"
