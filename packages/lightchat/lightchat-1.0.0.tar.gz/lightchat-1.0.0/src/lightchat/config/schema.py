# # src/lightchat/config/schema.py

# from typing import Optional, Dict, Any
# from dataclasses import dataclass, field
# from lightchat.exceptions import ConfigurationError
# from lightchat.security.policy import SecurityPolicy

# @dataclass
# class ConfigSchema:
#     """
#     Configuration schema for LightChat
#     """
#     max_processes: int = 10
#     cpu_limit: float = 50.0
#     memory_limit_mb: int = 256
#     timeout_sec: int = 300
#     security_policy: SecurityPolicy = field(default_factory=SecurityPolicy)
#     ipc_queue_size: int = 100

#     def validate(self) -> None:
#         """
#         Validate configuration fields
#         """
#         if not (1 <= self.max_processes <= 1000):
#             raise ConfigurationError(f"max_processes must be 1-1000, got {self.max_processes}")
#         if not (1.0 <= self.cpu_limit <= 100.0):
#             raise ConfigurationError(f"cpu_limit must be 1-100, got {self.cpu_limit}")
#         if self.memory_limit_mb <= 0:
#             raise ConfigurationError(f"memory_limit_mb must be positive, got {self.memory_limit_mb}")
#         if self.timeout_sec <= 0:
#             raise ConfigurationError(f"timeout_sec must be positive, got {self.timeout_sec}")
#         if not isinstance(self.security_policy, SecurityPolicy):
#             raise ConfigurationError("security_policy must be a SecurityPolicy instance")
#         if self.ipc_queue_size <= 0:
#             raise ConfigurationError(f"ipc_queue_size must be positive, got {self.ipc_queue_size}")
#         # Validate policy itself
#         self.security_policy.validate()
