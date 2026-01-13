from typing import List, Dict, Any
from castana.domain import ProbeResult, HealthStatus


def aggregate_results(
    results: List[ProbeResult],
    version: str = "1.0.0",
    redact_sensitive: bool = False,
) -> Dict[str, Any]:
    global_status = HealthStatus.PASS
    checks = {}

    sorted_results = sorted(results, key=lambda r: r.name)  # stable ordering

    for res in sorted_results:
        check_data: Dict[str, Any] = {
            "status": res.status,
        }

        if res.component_type:
            check_data["componentType"] = res.component_type
        if res.observed_value is not None:
            check_data["observedValue"] = res.observed_value
        if res.time:
            check_data["time"] = res.time

        if res.metadata and not redact_sensitive:
            check_data["metadata"] = dict(res.metadata)

        if res.output:
            check_data["output"] = res.output
        if res.observed_unit:
            check_data["observedUnit"] = res.observed_unit

        checks[res.name] = [check_data]

        if res.status == HealthStatus.FAIL and res.critical:
            global_status = HealthStatus.FAIL
        elif res.status == HealthStatus.WARN and global_status != HealthStatus.FAIL:
            global_status = HealthStatus.WARN

    result: Dict[str, Any] = {
        "status": global_status,
        "checks": checks,
    }

    if not redact_sensitive:
        result["version"] = version

    return result
