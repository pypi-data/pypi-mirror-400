from enum import Enum
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Optional, Dict, Any, Union, Mapping


class HealthStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    # TODO: consider adding UNKNOWN status for probes that didn't run

@dataclass(frozen=True)
class ProbeResult:
    status: HealthStatus
    name: str
    component_type: Optional[str] = None
    observed_value: Union[str, int, float, None] = None
    observed_unit: Optional[str] = None
    output: Optional[str] = None
    time: str = ""
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    critical: bool = True

    @property
    def is_healthy(self) -> bool:
        return self.status in (HealthStatus.PASS, HealthStatus.WARN)
