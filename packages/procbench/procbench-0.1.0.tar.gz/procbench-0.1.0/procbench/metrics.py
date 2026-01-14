# procmon/metrics.py

import psutil
from typing import Dict, Any


class ProcessMetrics:
    """
    Thin wrapper around psutil.Process.
    No control flow, no aggregation logic.
    """

    def __init__(self, pid: int):
        self.pid = pid
        self._proc = psutil.Process(pid)

        # Warm-up for cpu_percent (first call always returns 0.0)
        try:
            self._proc.cpu_percent(interval=None)
        except psutil.Error:
            pass

    def is_alive(self) -> bool:
        """
        Check whether process is still running and not zombie.
        """
        try:
            return (
                self._proc.is_running()
                and self._proc.status() != psutil.STATUS_ZOMBIE
            )
        except psutil.Error:
            return False

    def cpu_percent(self) -> float:
        """
        CPU usage since last call, percentage of total CPU.
        """
        try:
            return self._proc.cpu_percent(interval=None)
        except psutil.Error:
            return 0.0

    def memory(self) -> Dict[str, int]:
        """
        Memory usage.
        Returns RSS and VMS in bytes.
        """
        try:
            mem = self._proc.memory_info()
            return {
                "rss_bytes": mem.rss,
                "vms_bytes": mem.vms,
            }
        except psutil.Error:
            return {
                "rss_bytes": 0,
                "vms_bytes": 0,
            }

    def io_counters(self) -> Dict[str, int]:
        """
        Disk I/O counters (cumulative).
        """
        try:
            io = self._proc.io_counters()
            return {
                "read_bytes": io.read_bytes,
                "write_bytes": io.write_bytes,
            }
        except psutil.Error:
            return {
                "read_bytes": 0,
                "write_bytes": 0,
            }

    def snapshot(self) -> Dict[str, Any]:
        """
        Take a full metrics snapshot.
        Timestamp is intentionally NOT included here.
        """
        return {
            "cpu_percent": self.cpu_percent(),
            **self.memory(),
            "io": self.io_counters(),
        }
