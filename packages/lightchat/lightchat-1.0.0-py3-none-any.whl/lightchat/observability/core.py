# src/lightchat/observability/core.py

import logging
import uuid
import time
import psutil
from contextvars import ContextVar
from typing import Optional, Dict, Any

from lightchat.runtime.runtime_core import LightChatProcess, ProcessState
from lightchat.resources.core import ResourceMonitor
from lightchat.exceptions import ResourceLimitError

# --------------------------
# Correlation ID Utilities
# --------------------------
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str:
    """
    Retrieve or generate a correlation ID for the current context.
    """
    cid = correlation_id.get()
    if cid is None:
        cid = str(uuid.uuid4())
        correlation_id.set(cid)
    return cid


# --------------------------
# Structured Logger
# --------------------------
class LightChatLogger:
    """
    Structured logger for LightChat processes.
    Safe for multi-process and cross-platform use.
    """

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

        if not self._logger.handlers:
            self._logger.setLevel(logging.INFO)

            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] [cid=%(correlation_id)s] %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

            self._logger.propagate = False

    def _log(self, level: int, msg: str, **kwargs):
        try:
            self._logger.log(
                level,
                msg,
                extra={"correlation_id": get_correlation_id()},
                **kwargs
            )
        except Exception:
            # Fail-safe: logging should not raise
            pass

    def debug(self, msg: str, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)

    def info(self, msg: str, **kwargs):
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)

    def critical(self, msg: str, **kwargs):
        self._log(logging.CRITICAL, msg, **kwargs)


# --------------------------
# Metrics Collector
# --------------------------
class MetricsCollector:
    """
    Collects runtime, resource, and failure metrics for LightChat processes.
    """

    def __init__(self):
        self._metrics: Dict[str, Dict[str, Any]] = {}

    def register_process(self, process: LightChatProcess, monitor: ResourceMonitor) -> None:
        """Initialize metrics tracking for a process."""
        if process.name in self._metrics:
            raise ValueError(f"Process '{process.name}' already registered.")

        self._metrics[process.name] = {
            "start_time": time.time(),
            "cpu_usage": [],
            "memory_usage": [],
            "status": process.state.name,
            "monitor": monitor
        }

    def update_metrics(self, process_name: str) -> None:
        """Update metrics safely; handles processes that exited."""
        proc_metrics = self._metrics.get(process_name)
        if not proc_metrics:
            return

        monitor: ResourceMonitor = proc_metrics.get("monitor")
        if not monitor or monitor._psutil_proc is None:
            proc_metrics["status"] = "terminated"
            return

        try:
            # Check resource limits; will raise ResourceLimitError if exceeded or process gone
            monitor.check()

            cpu = 0.0
            mem = 0.0

            if monitor._psutil_proc and monitor._psutil_proc.is_running():
                try:
                    cpu = monitor._psutil_proc.cpu_percent(interval=0.1)
                except psutil.NoSuchProcess:
                    cpu = 0.0

                try:
                    mem = monitor._psutil_proc.memory_info().rss / (1024 * 1024)  # MB
                except (psutil.NoSuchProcess, AttributeError):
                    mem = 0.0

            proc_metrics["cpu_usage"].append(cpu)
            proc_metrics["memory_usage"].append(mem)
            proc_metrics["status"] = monitor.process.state.name

        except ResourceLimitError:
            proc_metrics["status"] = "limit_exceeded"
            if monitor.process.state == ProcessState.RUNNING:
                monitor.process.terminate()

        except Exception:
            proc_metrics["status"] = "error"

    def get_metrics(self, process_name: str) -> Dict[str, Any]:
        """Retrieve collected metrics for a process safely."""
        return self._metrics.get(process_name, {}).copy()

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Retrieve metrics for all registered processes."""
        return {name: data.copy() for name, data in self._metrics.items()}
