# procmon/monitor.py

import time
from typing import List, Dict, Any, Optional

from .metrics import ProcessMetrics
from .errors import MonitorRuntimeError


class ProcessMonitor:
    """
    Sampling loop for a single process.
    Responsible for:
      - periodic sampling
      - stop conditions
      - timestamping samples
    """

    def __init__(
        self,
        pid: int,
        sampling_interval_ms: int,
        timeout_sec: Optional[int] = None,
        include_children: bool = False,
    ):
        self.pid = pid
        self.sampling_interval_sec = sampling_interval_ms / 1000.0
        self.timeout_sec = timeout_sec
        self.include_children = include_children  # reserved, not implemented yet

        self._metrics = ProcessMetrics(pid)
        self._samples: List[Dict[str, Any]] = []

        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
        self._status: str = "running"

    @property
    def samples(self) -> List[Dict[str, Any]]:
        return self._samples

    @property
    def start_time(self) -> Optional[float]:
        return self._start_time

    @property
    def end_time(self) -> Optional[float]:
        return self._end_time

    @property
    def status(self) -> str:
        return self._status

    def run(self) -> None:
        """
        Start monitoring loop.
        Blocking call.
        """
        self._start_time = time.time()
        deadline = (
            self._start_time + self.timeout_sec
            if self.timeout_sec is not None
            else None
        )

        # Initial warm-up sleep to make first cpu_percent meaningful
        time.sleep(self.sampling_interval_sec)

        try:
            while True:
                now = time.time()

                # Timeout check
                if deadline is not None and now >= deadline:
                    self._status = "timeout"
                    break

                # Liveness check
                if not self._metrics.is_alive():
                    self._status = "completed"
                    break

                snapshot = self._metrics.snapshot()
                snapshot["ts"] = now
                self._samples.append(snapshot)

                time.sleep(self.sampling_interval_sec)

        except Exception as e:
            self._status = "runtime_error"
            raise MonitorRuntimeError(f"Monitoring failed for pid {self.pid}: {e}")

        finally:
            self._end_time = time.time()

    def result(self) -> Dict[str, Any]:
        """
        Return raw monitoring result.
        Summary is computed elsewhere.
        """
        return {
            "pid": self.pid,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "status": self._status,
            "samples": self._samples,
        }
