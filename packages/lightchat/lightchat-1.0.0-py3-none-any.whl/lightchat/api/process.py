import psutil

from typing import Optional, Dict, Any, List, Union
from lightchat.runtime.runtime_core import LightChatProcess, ProcessState, SignalLevel
from lightchat.exceptions import LightChatError
from lightchat.resources.core import ResourceMonitor, ResourceLimits
from lightchat.config.core import ConfigSchema
from lightchat.observability.core import LightChatLogger


logger = LightChatLogger(__name__)


class ProcessHandle:
    """
    User-facing process abstraction.
    Wraps LightChatProcess safely with monitoring.
    """

    def __init__(
        self,
        name: str,
        command: Union[str, List[str]],
        config: Optional[ConfigSchema] = None,
    ):
        self.name = name
        # Ensure command is list
        self.command = [command] if isinstance(command, str) else command
        self.config = config
        self._process = LightChatProcess(name=name, command=self.command)
        self._monitor = ResourceMonitor(
            self._process,
            limits=ResourceLimits(
                cpu_percent=int(config.cpu_limit) if config and config.cpu_limit else None,
                memory_mb=config.memory_limit_mb if config and config.memory_limit_mb else None,
                execution_timeout_sec=config.timeout_sec if config and config.timeout_sec else None
            )
        )
        logger.info(f"ProcessHandle created for '{name}'")

    def start(self) -> None:
        """Start the process safely."""
        try:
            self._process.start()
            self._monitor.start()
            logger.info(f"Process '{self.name}' started")
        except LightChatError as e:
            logger.error(f"Failed to start process '{self.name}': {e}")
            raise

    def terminate(self, level: SignalLevel = SignalLevel.GRACEFUL) -> None:
        """Terminate the process safely with specified signal level."""
        try:
            self._process.terminate(level=level)
            logger.info(f"Process '{self.name}' terminated with level {level.name}")
        except LightChatError as e:
            logger.error(f"Failed to terminate process '{self.name}': {e}")
            raise

    def stop(self) -> None:
        """Convenience: graceful termination."""
        self.terminate(level=SignalLevel.GRACEFUL)

    def kill(self) -> None:
        """Convenience: hard kill."""
        self.terminate(level=SignalLevel.HARD_KILL)

    def status(self) -> str:
        """Return current state of the process."""
        return self._process.state.name

    def wait(self, timeout: Optional[float] = None) -> int:
        """Wait for process completion."""
        try:
            return self._process.wait(timeout=timeout)
        except LightChatError as e:
            logger.error(f"Process '{self.name}' failed during wait: {e}")
            raise

    def metrics(self) -> Dict[str, Any]:
        """Return latest resource metrics safely."""
        cpu = 0.0
        mem = 0.0

        if self._monitor._psutil_proc:
            try:
                if self._monitor._psutil_proc.is_running():
                    cpu = self._monitor._psutil_proc.cpu_percent(interval=0.1)
                    mem = self._monitor._psutil_proc.memory_info().rss / (1024 * 1024)
            except (psutil.NoSuchProcess, AttributeError):
                # Process exited, return 0 metrics
                cpu = 0.0
                mem = 0.0
            except Exception as e:
                logger.warning(f"Failed to get metrics for process '{self.name}': {e}")

        return {
            "cpu_usage": cpu,
            "memory_usage": mem,
            "state": self.status(),
        }
