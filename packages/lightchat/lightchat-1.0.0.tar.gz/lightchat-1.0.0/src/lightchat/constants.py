# src/lightchat/constants.py

from enum import Enum, auto


# ----------------------
# Process Lifecycle States
# ----------------------
class ProcessState(Enum):
    CREATED = auto()
    INITIALIZING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    TERMINATED = auto()


# ----------------------
# Signal Escalation Levels
# ----------------------
class SignalLevel(Enum):
    GRACEFUL = auto()
    FORCED = auto()
    HARD_KILL = auto()


# ----------------------
# Default Resource Limits
# ----------------------
DEFAULT_CPU_LIMIT_PERCENT = 80          # Max CPU percent per process
DEFAULT_MEMORY_LIMIT_MB = 512           # Max memory per process (MB)
DEFAULT_EXECUTION_TIMEOUT_SEC = 300    # Max runtime per process in seconds

# ----------------------
# Logging / Metrics Defaults
# ----------------------
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_METRICS_INTERVAL_SEC = 5
