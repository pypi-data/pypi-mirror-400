# procmon/runner.py

import subprocess
import time
import os
from typing import Optional, Dict, Any

from .errors import SpawnError


class ProcessRunner:
    """
    Responsible for spawning and controlling process lifetime.
    Does NOT perform monitoring.
    """

    def __init__(
        self,
        command: list[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        self.command = command
        self.cwd = cwd
        self.env = env

        self._proc: Optional[subprocess.Popen] = None
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None

    @property
    def pid(self) -> Optional[int]:
        return self._proc.pid if self._proc else None

    @property
    def start_time(self) -> Optional[float]:
        return self._start_time

    @property
    def end_time(self) -> Optional[float]:
        return self._end_time

    def start(self) -> None:
        """
        Spawn the process.
        """
        if self._proc is not None:
            raise RuntimeError("Process already started")

        try:
            merged_env = os.environ.copy()
            if self.env:
                merged_env.update(self.env)

            self._proc = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                env=merged_env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
            )

            self._start_time = time.time()

        except Exception as e:
            raise SpawnError(f"Failed to start process: {e}")

    def wait(self, timeout: Optional[int] = None) -> bool:
        """
        Wait for process termination.
        Returns True if process exited normally,
        False if timeout occurred.
        """
        if self._proc is None:
            raise RuntimeError("Process not started")

        try:
            self._proc.wait(timeout=timeout)
            self._end_time = time.time()
            return True
        except subprocess.TimeoutExpired:
            return False

    def terminate(self) -> None:
        """
        Forcefully terminate the process.
        """
        if self._proc is None:
            return

        try:
            self._proc.terminate()
            self._proc.wait(timeout=5)
        except Exception:
            try:
                self._proc.kill()
            except Exception:
                pass
        finally:
            self._end_time = time.time()

    def poll(self) -> Optional[int]:
        """
        Non-blocking check.
        Returns exit code if finished, else None.
        """
        if self._proc is None:
            return None
        return self._proc.poll()

    def exit_code(self) -> Optional[int]:
        """
        Return process exit code if available.
        """
        if self._proc is None:
            return None
        return self._proc.returncode

    def info(self) -> Dict[str, Any]:
        """
        Process execution metadata.
        """
        return {
            "pid": self.pid,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "exit_code": self.exit_code(),
        }
