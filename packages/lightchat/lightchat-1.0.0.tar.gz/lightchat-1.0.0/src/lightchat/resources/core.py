# src/lightchat/resources/core.py

import time
import threading
from dataclasses import dataclass
from typing import Optional, Dict
import psutil
import logging

from lightchat.runtime.runtime_core import LightChatProcess
from lightchat.exceptions import ResourceLimitError
from lightchat.constants import (
    DEFAULT_CPU_LIMIT_PERCENT,
    DEFAULT_MEMORY_LIMIT_MB,
    DEFAULT_EXECUTION_TIMEOUT_SEC,
    ProcessState
)

# --------------------------
# Logger Setup
# --------------------------
logger = logging.getLogger("LightChatResources")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# --------------------------
# Resource Limits
# --------------------------
@dataclass(frozen=True)
class ResourceLimits:
    """
    Defines resource caps for a single process.
    """
    cpu_percent: int = DEFAULT_CPU_LIMIT_PERCENT
    memory_mb: int = DEFAULT_MEMORY_LIMIT_MB
    execution_timeout_sec: int = DEFAULT_EXECUTION_TIMEOUT_SEC

    def validate(self) -> None:
        if not (0 < self.cpu_percent <= 100):
            raise ValueError(f"cpu_percent must be 1-100, got {self.cpu_percent}")
        if self.memory_mb <= 0:
            raise ValueError(f"memory_mb must be >0, got {self.memory_mb}")
        if self.execution_timeout_sec <= 0:
            raise ValueError(f"execution_timeout_sec must be >0, got {self.execution_timeout_sec}")


# --------------------------
# Resource Monitor
# --------------------------
class ResourceMonitor:
    """
    Monitors a LightChatProcess for CPU, memory, and execution time.
    Safe for short-lived processes.
    """

    def __init__(self, process: LightChatProcess, limits: Optional[ResourceLimits] = None):
        self.process = process
        self.limits = limits or ResourceLimits()
        self._start_time: Optional[float] = None
        self._psutil_proc: Optional[psutil.Process] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Initialize monitoring. Process must be started."""
        if self.process._proc is None:
            raise ResourceLimitError("Process must be started before monitoring.")

        with self._lock:
            try:
                self._psutil_proc = psutil.Process(self.process._proc.pid)
                self._start_time = time.time()
                logger.info(f"Resource monitor started for process '{self.process.name}'")
            except psutil.NoSuchProcess:
                self._psutil_proc = None
                logger.warning(f"Process '{self.process.name}' exited before monitoring could start.")
            except Exception as e:
                raise ResourceLimitError(f"Failed to start resource monitor: {e}") from e

    def check(self) -> None:
        """Check current resource usage; safe if process has exited."""
        with self._lock:
            if self._psutil_proc is None:
                # Already exited
                return

            try:
                if not self._psutil_proc.is_running():
                    logger.info(f"Process '{self.process.name}' is no longer running.")
                    self._psutil_proc = None
                    return

                # CPU usage percent (non-blocking)
                cpu = self._psutil_proc.cpu_percent(interval=0.1)
                if cpu > self.limits.cpu_percent:
                    raise ResourceLimitError(
                        f"CPU limit exceeded: {cpu:.2f}% > {self.limits.cpu_percent}%"
                    )

                # Memory usage in MB
                mem = self._psutil_proc.memory_info().rss / (1024 * 1024)
                if mem > self.limits.memory_mb:
                    raise ResourceLimitError(
                        f"Memory limit exceeded: {mem:.2f}MB > {self.limits.memory_mb}MB"
                    )

                # Execution time
                elapsed = time.time() - (self._start_time or time.time())
                if elapsed > self.limits.execution_timeout_sec:
                    raise ResourceLimitError(
                        f"Execution timeout exceeded: {elapsed:.2f}s > {self.limits.execution_timeout_sec}s"
                    )

            except psutil.NoSuchProcess:
                self._psutil_proc = None
                logger.info(f"Process '{self.process.name}' has exited during resource check.")
            except Exception as e:
                raise ResourceLimitError(f"Resource monitoring failed for '{self.process.name}': {e}") from e


# --------------------------
# Quota Manager
# --------------------------
class QuotaManager:
    """
    Tracks resource quotas for multiple processes and enforces limits.
    """

    def __init__(self):
        self._monitors: Dict[str, ResourceMonitor] = {}
        self._lock = threading.Lock()

    def register(
        self, process: LightChatProcess, limits: Optional[ResourceLimits] = None
    ) -> None:
        """Register a process with optional limits."""
        with self._lock:
            if process.name in self._monitors:
                raise ResourceLimitError(
                    f"Process '{process.name}' already registered in quota manager."
                )

            monitor = ResourceMonitor(process, limits)
            monitor.start()
            self._monitors[process.name] = monitor
            logger.info(f"Process '{process.name}' registered with quota manager")

    def enforce(self) -> None:
        """Enforce quotas: terminate processes exceeding limits."""
        with self._lock:
            for name, monitor in self._monitors.items():
                try:
                    monitor.check()
                except ResourceLimitError as e:
                    process = monitor.process
                    logger.warning(f"Quota violation detected for process '{name}': {e}")
                    if process.state == ProcessState.RUNNING:
                        try:
                            process.terminate()
                            logger.info(f"Process '{name}' terminated due to quota violation")
                        except Exception as term_e:
                            logger.error(f"Failed to terminate process '{name}': {term_e}")
