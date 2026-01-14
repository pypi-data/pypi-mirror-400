# procmon/output.py

import json
import platform
from pathlib import Path
from typing import List, Dict, Any


class OutputWriter:
    """
    Assemble and write final session output JSON.
    """

    def __init__(self, schema_version: str):
        self.schema_version = schema_version

    def build_session_metadata(
        self,
        start_time: float,
        end_time: float,
    ) -> Dict[str, Any]:
        return {
            "start_time": start_time,
            "end_time": end_time,
            "host": platform.platform(),
        }

    def build_testcase_result(
        self,
        testcase_meta: Dict[str, Any],
        process_info: Dict[str, Any],
        samples: List[Dict[str, Any]],
        summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "test_case": {
                "id": testcase_meta["id"],
                "name": testcase_meta.get("name", testcase_meta["id"]),
            },
            "process": {
                "pid": process_info.get("pid"),
                "start_time": process_info.get("start_time"),
                "end_time": process_info.get("end_time"),
                "exit_code": process_info.get("exit_code"),
            },
            "samples": samples,
            "summary": summary,
        }

    def write(
        self,
        output_path: str | Path,
        session_start: float,
        session_end: float,
        results: List[Dict[str, Any]],
    ) -> None:
        output = {
            "schema_version": self.schema_version,
            "session": self.build_session_metadata(
                start_time=session_start,
                end_time=session_end,
            ),
            "results": results,
        }

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(output, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
