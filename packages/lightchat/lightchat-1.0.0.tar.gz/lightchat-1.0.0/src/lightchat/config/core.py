# src/lightchat/config/core.py

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from lightchat.security.core import SecurityPolicy
from lightchat.exceptions import ConfigurationError

# --------------------------
# Default Configuration Constants
# --------------------------
DEFAULT_MAX_PROCESSES = 10
DEFAULT_CPU_LIMIT = 50.0         # % CPU per process
DEFAULT_MEMORY_LIMIT_MB = 256    # MB per process
DEFAULT_TIMEOUT_SEC = 300        # max execution time per process
DEFAULT_IPC_QUEUE_SIZE = 100

# Default security policy: deny everything unless explicitly allowed
DEFAULT_POLICY = SecurityPolicy(
    allow_files=[],
    deny_files=["*"],  
    allow_network=False,
    deny_network=True,
    allowed_env_vars=["PATH", "HOME", "USER", "TMPDIR"]
)

# --------------------------
# Configuration Schema
# --------------------------
@dataclass
class ConfigSchema:
    """
    Configuration schema for LightChat
    """
    max_processes: int = DEFAULT_MAX_PROCESSES
    cpu_limit: float = DEFAULT_CPU_LIMIT
    memory_limit_mb: int = DEFAULT_MEMORY_LIMIT_MB
    timeout_sec: int = DEFAULT_TIMEOUT_SEC
    security_policy: SecurityPolicy = field(default_factory=lambda: DEFAULT_POLICY)
    ipc_queue_size: int = DEFAULT_IPC_QUEUE_SIZE

    def validate(self) -> None:
        """
        Validate configuration fields.
        """
        if not (1 <= self.max_processes <= 1000):
            raise ConfigurationError(f"max_processes must be 1-1000, got {self.max_processes}")
        if not (1.0 <= self.cpu_limit <= 100.0):
            raise ConfigurationError(f"cpu_limit must be 1-100, got {self.cpu_limit}")
        if self.memory_limit_mb <= 0:
            raise ConfigurationError(f"memory_limit_mb must be positive, got {self.memory_limit_mb}")
        if self.timeout_sec <= 0:
            raise ConfigurationError(f"timeout_sec must be positive, got {self.timeout_sec}")
        if not isinstance(self.security_policy, SecurityPolicy):
            raise ConfigurationError("security_policy must be a SecurityPolicy instance")
        if self.ipc_queue_size <= 0:
            raise ConfigurationError(f"ipc_queue_size must be positive, got {self.ipc_queue_size}")
        # Validate policy itself
        self.security_policy.validate()

# --------------------------
# Configuration Loader
# --------------------------
class ConfigLoader:
    """
    Loads and validates LightChat configuration.
    Can read from environment variables or overrides dict.
    """

    def __init__(self, overrides: Optional[Dict[str, Any]] = None):
        self.overrides = overrides or {}
        self._config = self._load()

    def _env(self, key: str, default):
        """
        Helper: read from environment, then overrides, then default.
        """
        # Environment variables take priority over overrides
        env_val = os.getenv(key)
        if env_val is not None:
            return env_val
        return self.overrides.get(key.lower(), default)

    def _load(self) -> ConfigSchema:
        """
        Construct and validate configuration object.
        """
        try:
            cfg = ConfigSchema(
                max_processes=int(self._env("LIGHTCHAT_MAX_PROCESSES", DEFAULT_MAX_PROCESSES)),
                cpu_limit=float(self._env("LIGHTCHAT_CPU_LIMIT", DEFAULT_CPU_LIMIT)),
                memory_limit_mb=int(self._env("LIGHTCHAT_MEMORY_LIMIT_MB", DEFAULT_MEMORY_LIMIT_MB)),
                timeout_sec=int(self._env("LIGHTCHAT_TIMEOUT_SEC", DEFAULT_TIMEOUT_SEC)),
                security_policy=self.overrides.get("security_policy", DEFAULT_POLICY),
                ipc_queue_size=int(self._env("LIGHTCHAT_IPC_QUEUE_SIZE", DEFAULT_IPC_QUEUE_SIZE)),
            )
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration value: {e}")

        cfg.validate()
        return cfg

    def get(self) -> ConfigSchema:
        """
        Retrieve the final validated configuration.
        """
        return self._config
