# procmon/testcase.py

import json
from pathlib import Path
from typing import Dict, Any

from .schema import (
    validate_schema_version,
    validate_testcase_dict,
)
from .errors import (
    TestCaseLoadError,
    SchemaValidationError,
)


class TestCase:
    """
    Immutable representation of a validated test case.
    """

    def __init__(self, raw: Dict[str, Any]):
        self.schema_version: str = raw["schema_version"]
        self.id: str = raw["id"]
        self.name: str = raw.get("name", self.id)
        self.command: list[str] = raw["command"]
        self.cwd: str | None = raw.get("cwd")
        self.env: Dict[str, str] | None = raw.get("env")

        monitor = raw["monitor"]
        self.sampling_interval_ms: int = monitor["sampling_interval_ms"]
        self.include_children: bool = monitor.get("include_children", False)
        self.timeout_sec: int | None = monitor.get("timeout_sec")

    @classmethod
    def load_from_file(cls, path: str | Path) -> "TestCase":
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception as e:
            raise TestCaseLoadError(f"Failed to read test case '{path}': {e}")

        try:
            validate_schema_version(data.get("schema_version"))
            validate_testcase_dict(data)
        except Exception as e:
            raise SchemaValidationError(
                f"Schema validation failed for '{path}': {e}"
            )

        return cls(data)

    def to_dict(self) -> dict:
        """Normalized representation (useful for output JSON)."""
        return {
            "id": self.id,
            "name": self.name,
            "command": self.command,
            "cwd": self.cwd,
            "env": self.env,
            "monitor": {
                "sampling_interval_ms": self.sampling_interval_ms,
                "include_children": self.include_children,
                "timeout_sec": self.timeout_sec,
            },
        }
