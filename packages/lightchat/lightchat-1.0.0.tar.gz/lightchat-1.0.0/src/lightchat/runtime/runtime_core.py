# src/lightchat/runtime/runtime_core.py

import subprocess
import os
import sys
import threading
import logging
from typing import Optional, List, Dict
from lightchat.constants import ProcessState, SignalLevel, DEFAULT_EXECUTION_TIMEOUT_SEC
from lightchat.exceptions import RuntimeExecutionError, LightChatError

# --------------------------
# Logger Setup
# --------------------------
logger = logging.getLogger("LightChatRuntime")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# --------------------------
# State Management
# --------------------------
VALID_TRANSITIONS: Dict[ProcessState, List[ProcessState]] = {
    ProcessState.CREATED: [ProcessState.INITIALIZING, ProcessState.TERMINATED],
    ProcessState.INITIALIZING: [ProcessState.RUNNING, ProcessState.FAILED, ProcessState.TERMINATED],
    ProcessState.RUNNING: [ProcessState.COMPLETED, ProcessState.FAILED, ProcessState.TERMINATED],
    ProcessState.COMPLETED: [ProcessState.TERMINATED],
    ProcessState.FAILED: [ProcessState.TERMINATED],
    ProcessState.TERMINATED: [],
}


def is_valid_transition(current: ProcessState, next_state: ProcessState) -> bool:
    return next_state in VALID_TRANSITIONS.get(current, [])


def assert_transition(current: ProcessState, next_state: ProcessState) -> None:
    if not is_valid_transition(current, next_state):
        raise LightChatError(f"Invalid state transition: {current.name} → {next_state.name}")

# --------------------------
# Signal Handling
# --------------------------
class LightChatSignalError(LightChatError):
    """Signal handling error."""


try:
    import signal as _signal
except ImportError:
    _signal = None

SYSTEM_SIGNALS: Dict[SignalLevel, Optional[int]] = {
    SignalLevel.GRACEFUL: _signal.SIGTERM if _signal and hasattr(_signal, "SIGTERM") else None,
    SignalLevel.FORCED: _signal.SIGINT if _signal and hasattr(_signal, "SIGINT") else None,
}

if sys.platform.startswith("win"):
    # Windows HARD_KILL handled via Popen.kill()
    SYSTEM_SIGNALS[SignalLevel.HARD_KILL] = None
else:
    SYSTEM_SIGNALS[SignalLevel.HARD_KILL] = _signal.SIGKILL if _signal and hasattr(_signal, "SIGKILL") else None


def get_signal(level: SignalLevel) -> Optional[int]:
    if level not in SYSTEM_SIGNALS:
        raise LightChatSignalError(f"Unsupported signal level: {level}")
    return SYSTEM_SIGNALS[level]

# --------------------------
# LightChatProcess
# --------------------------
class LightChatProcess:
    """
    Encapsulates a managed OS process with strict lifecycle control.
    """

    def __init__(
        self,
        command: List[str],
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[str] = None,
        name: Optional[str] = None,
        timeout: Optional[float] = DEFAULT_EXECUTION_TIMEOUT_SEC,
    ):
        if not command:
            raise RuntimeExecutionError("Command cannot be empty.")
        self.command = command
        self.env = env or os.environ.copy()
        self.cwd = cwd
        self.name = name or f"LightChatProcess-{id(self)}"
        self.state = ProcessState.CREATED
        self._proc: Optional[subprocess.Popen] = None
        self.timeout = timeout
        self._stdout = ""
        self._stderr = ""
        self._lock = threading.Lock()

    @property
    def stdout(self) -> str:
        return self._stdout

    @property
    def stderr(self) -> str:
        return self._stderr

    def start(self) -> None:
        """Start the process."""
        with self._lock:
            assert_transition(self.state, ProcessState.INITIALIZING)
            self.state = ProcessState.INITIALIZING
            logger.info(f"Starting process '{self.name}': {self.command}")

            try:
                self._proc = subprocess.Popen(
                    self.command,
                    env=self.env,
                    cwd=self.cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                )

                self.state = ProcessState.RUNNING

                # Start thread to read stdout/stderr asynchronously
                threading.Thread(target=self._read_streams, daemon=True).start()

            except Exception as e:
                self.state = ProcessState.FAILED
                logger.error(f"Failed to start process '{self.name}': {e}")
                raise RuntimeExecutionError(f"Failed to start process '{self.name}': {e}") from e

    def _read_streams(self):
        """Capture stdout and stderr without blocking."""
        if not self._proc:
            return
        try:
            stdout_lines = []
            stderr_lines = []

            for line in self._proc.stdout or []:
                stdout_lines.append(line.rstrip())
            for line in self._proc.stderr or []:
                stderr_lines.append(line.rstrip())

            self._stdout = "\n".join(stdout_lines)
            self._stderr = "\n".join(stderr_lines)

        except Exception as e:
            logger.warning(f"Error reading streams for process '{self.name}': {e}")

    def terminate(self, level: SignalLevel = SignalLevel.GRACEFUL) -> None:
        """Terminate the process safely according to SignalLevel."""
        with self._lock:
            if not self._proc or self.state in {ProcessState.COMPLETED, ProcessState.TERMINATED}:
                logger.info(f"Process '{self.name}' already terminated or not started.")
                return

            sig = get_signal(level)
            try:
                if sig is None:
                    # Windows HARD_KILL
                    self._proc.kill()
                    logger.info(f"Process '{self.name}' killed (HARD_KILL).")
                else:
                    self._proc.send_signal(sig)
                    logger.info(f"Process '{self.name}' signaled with {level.name} ({sig}).")
            except Exception as e:
                logger.error(f"Failed to terminate process '{self.name}': {e}")
                raise RuntimeExecutionError(f"Failed to terminate process '{self.name}': {e}") from e
            finally:
                self.state = ProcessState.TERMINATED

    def wait(self, timeout: Optional[float] = None) -> int:
        """Wait for the process to complete."""
        if not self._proc:
            raise RuntimeExecutionError(f"Process '{self.name}' not started.")

        wait_timeout = timeout or self.timeout

        try:
            retcode = self._proc.wait(timeout=wait_timeout)
            self.state = ProcessState.COMPLETED if retcode == 0 else ProcessState.FAILED
            logger.info(f"Process '{self.name}' finished with code {retcode}")
            return retcode
        except subprocess.TimeoutExpired:
            logger.warning(f"Process '{self.name}' timed out after {wait_timeout}s, terminating HARD_KILL.")
            self.terminate(level=SignalLevel.HARD_KILL)
            self.state = ProcessState.FAILED
            raise RuntimeExecutionError(f"Process '{self.name}' timed out and was forcefully terminated.")

# --------------------------
# Supervisor
# --------------------------
class Supervisor:
    """
    Supervises multiple LightChatProcess instances.
    """

    def __init__(self):
        self._processes: Dict[str, LightChatProcess] = {}
        self._lock = threading.Lock()

    def register(self, proc: LightChatProcess) -> None:
        with self._lock:
            if proc.name in self._processes:
                raise RuntimeExecutionError(f"Process with name '{proc.name}' already registered.")
            self._processes[proc.name] = proc
            logger.info(f"Registered process '{proc.name}'")

    def unregister(self, proc_name: str) -> None:
        with self._lock:
            if proc_name in self._processes:
                self._processes.pop(proc_name)
                logger.info(f"Unregistered process '{proc_name}'")

    def start_all(self) -> None:
        with self._lock:
            for proc in self._processes.values():
                try:
                    proc.start()
                except RuntimeExecutionError:
                    logger.warning(f"Failed to start process '{proc.name}' during start_all.")

    def terminate_all(self, level: SignalLevel = SignalLevel.GRACEFUL) -> None:
        with self._lock:
            for proc in self._processes.values():
                try:
                    proc.terminate(level=level)
                except RuntimeExecutionError:
                    logger.warning(f"Failed to terminate process '{proc.name}' during terminate_all.")

    def monitor(self) -> Dict[str, ProcessState]:
        with self._lock:
            return {name: proc.state for name, proc in self._processes.items()}

    def restart_failed(self) -> None:
        with self._lock:
            for proc in self._processes.values():
                if proc.state == ProcessState.FAILED:
                    try:
                        proc.terminate(level=SignalLevel.HARD_KILL)
                        proc.start()
                        logger.info(f"Restarted failed process '{proc.name}'")
                    except RuntimeExecutionError:
                        logger.warning(f"Failed to restart process '{proc.name}'")
