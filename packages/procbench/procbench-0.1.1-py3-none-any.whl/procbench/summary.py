# procmon/summary.py

from typing import List, Dict, Any


def summarize_samples(
    samples: List[Dict[str, Any]],
    start_time: float | None,
    end_time: float | None,
    exit_code: int | None,
    status: str,
) -> Dict[str, Any]:
    """
    Aggregate raw samples into summary metrics.
    """

    if not samples:
        return {
            "runtime_sec": (
                (end_time - start_time)
                if start_time is not None and end_time is not None
                else 0.0
            ),
            "cpu": {"avg": 0.0, "max": 0.0},
            "memory": {"max_rss_bytes": 0},
            "io": {"read_bytes": 0, "write_bytes": 0},
            "exit_code": exit_code,
            "status": status,
        }

    cpu_values = [s["cpu_percent"] for s in samples]
    rss_values = [s["rss_bytes"] for s in samples]

    first_io = samples[0]["io"]
    last_io = samples[-1]["io"]

    runtime_sec = (
        (end_time - start_time)
        if start_time is not None and end_time is not None
        else samples[-1]["ts"] - samples[0]["ts"]
    )

    return {
        "runtime_sec": runtime_sec,
        "cpu": {
            "avg": sum(cpu_values) / len(cpu_values),
            "max": max(cpu_values),
        },
        "memory": {
            "max_rss_bytes": max(rss_values),
        },
        "io": {
            "read_bytes": max(0, last_io["read_bytes"] - first_io["read_bytes"]),
            "write_bytes": max(0, last_io["write_bytes"] - first_io["write_bytes"]),
        },
        "exit_code": exit_code,
        "status": status,
    }
