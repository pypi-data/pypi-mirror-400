# procmon/schema.py

SUPPORTED_SCHEMA_VERSION = "1.0"


REQUIRED_ROOT_FIELDS = {
    "schema_version",
    "id",
    "command",
    "monitor",
}

REQUIRED_MONITOR_FIELDS = {
    "sampling_interval_ms",
}


def validate_schema_version(version: str) -> None:
    if version != SUPPORTED_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported schema_version '{version}', "
            f"expected '{SUPPORTED_SCHEMA_VERSION}'"
        )


def validate_testcase_dict(tc: dict) -> None:
    missing = REQUIRED_ROOT_FIELDS - tc.keys()
    if missing:
        raise ValueError(f"Missing required fields: {sorted(missing)}")

    if not isinstance(tc["command"], list) or not tc["command"]:
        raise ValueError("'command' must be a non-empty array")

    monitor = tc["monitor"]
    if not isinstance(monitor, dict):
        raise ValueError("'monitor' must be an object")

    missing_monitor = REQUIRED_MONITOR_FIELDS - monitor.keys()
    if missing_monitor:
        raise ValueError(
            f"Missing monitor fields: {sorted(missing_monitor)}"
        )

    interval = monitor["sampling_interval_ms"]
    if not isinstance(interval, int) or interval < 50:
        raise ValueError("'sampling_interval_ms' must be int >= 50")

    timeout = monitor.get("timeout_sec")
    if timeout is not None and (not isinstance(timeout, int) or timeout <= 0):
        raise ValueError("'timeout_sec' must be positive int")

    include_children = monitor.get("include_children")
    if include_children is not None and not isinstance(include_children, bool):
        raise ValueError("'include_children' must be boolean")
