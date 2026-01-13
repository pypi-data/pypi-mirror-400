import time
from typing import Dict, Any, Union, Optional, Set

from castana.probes.base import BaseProbe
from castana.exceptions import WarnCondition

class HttpProbe(BaseProbe):
    def __init__(
        self,
        url: str,
        name: str = "http",
        timeout: float = 10.0,
        method: str = "GET",
        expected_status: Union[int, Set[int], range] = range(200, 300),
        headers: Optional[Dict[str, str]] = None,
        warn_latency_ms: Optional[float] = None,
        critical: bool = True,
        retry_attempts: int = 0,
        retry_delay: float = 0.0,
    ):
        super().__init__(
            name,
            timeout,
            component_type="http",
            critical=critical,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
        )
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.warn_latency_ms = warn_latency_ms

        if isinstance(expected_status, int):
            self.expected_status = {expected_status}
        elif isinstance(expected_status, range):
            self.expected_status = set(expected_status)
        else:
            self.expected_status = expected_status

        self._ensure_httpx()

    def _ensure_httpx(self):
        try:
            import httpx
            self._httpx = httpx
        except ImportError:
            raise ImportError("HttpProbe requires 'httpx'. Install it via: pip install castana[http]")

    async def check(self) -> Dict[str, Any]:
        async with self._httpx.AsyncClient(timeout=None) as client:
            start = time.perf_counter()
            response = await client.request(
                self.method,
                self.url,
                headers=self.headers
            )
            latency_ms = (time.perf_counter() - start) * 1000

        if response.status_code not in self.expected_status:
            raise ConnectionError(
                f"Unexpected status code: {response.status_code} (Expected: {self.expected_status})"
            )

        if self.warn_latency_ms and latency_ms > self.warn_latency_ms:
            raise WarnCondition(
                f"Slow response: {latency_ms:.0f}ms > {self.warn_latency_ms:.0f}ms"
            )

        return {
            "status_code": response.status_code,
            "request_ms": round(latency_ms, 2)
        }
