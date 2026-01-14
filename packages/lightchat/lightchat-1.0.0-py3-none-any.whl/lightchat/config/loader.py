# # src/lightchat/config/loader.py

# import os
# from typing import Optional, Dict, Any
# from lightchat.config.schema import ConfigSchema
# from lightchat.config.defaults import (
#     DEFAULT_MAX_PROCESSES,
#     DEFAULT_CPU_LIMIT,
#     DEFAULT_MEMORY_LIMIT_MB,
#     DEFAULT_TIMEOUT_SEC,
#     DEFAULT_POLICY,
#     DEFAULT_IPC_QUEUE_SIZE
# )
# from lightchat.exceptions import ConfigurationError


# class ConfigLoader:
#     """
#     Loads and validates LightChat configuration.
#     """

#     def __init__(self, overrides: Optional[Dict[str, Any]] = None):
#         self.overrides = overrides or {}
#         self._config = self._load()

#     def _env(self, key: str, default):
#         return os.getenv(key, self.overrides.get(key.lower(), default))

#     def _load(self) -> ConfigSchema:
#         try:
#             cfg = ConfigSchema(
#                 max_processes=int(self._env("LIGHTCHAT_MAX_PROCESSES", DEFAULT_MAX_PROCESSES)),
#                 cpu_limit=float(self._env("LIGHTCHAT_CPU_LIMIT", DEFAULT_CPU_LIMIT)),
#                 memory_limit_mb=int(self._env("LIGHTCHAT_MEMORY_LIMIT_MB", DEFAULT_MEMORY_LIMIT_MB)),
#                 timeout_sec=int(self._env("LIGHTCHAT_TIMEOUT_SEC", DEFAULT_TIMEOUT_SEC)),
#                 security_policy=self.overrides.get("security_policy", DEFAULT_POLICY),
#                 ipc_queue_size=int(self._env("LIGHTCHAT_IPC_QUEUE_SIZE", DEFAULT_IPC_QUEUE_SIZE)),
#             )
#         except ValueError as e:
#             raise ConfigurationError(f"Invalid configuration value: {e}")

#         cfg.validate()
#         return cfg

#     def get(self) -> ConfigSchema:
#         return self._config
