# # src/lightchat/resources/limits.py

# from dataclasses import dataclass
# from typing import Optional
# from lightchat.constants import DEFAULT_CPU_LIMIT_PERCENT, DEFAULT_MEMORY_LIMIT_MB, DEFAULT_EXECUTION_TIMEOUT_SEC


# @dataclass(frozen=True)
# class ResourceLimits:
#     """
#     Defines resource caps for a single process.
#     """
#     cpu_percent: int = DEFAULT_CPU_LIMIT_PERCENT        # Max CPU %
#     memory_mb: int = DEFAULT_MEMORY_LIMIT_MB           # Max memory in MB
#     execution_timeout_sec: int = DEFAULT_EXECUTION_TIMEOUT_SEC  # Max runtime in seconds

#     def validate(self) -> None:
#         """
#         Validate that limits are reasonable.
#         """
#         if not (0 < self.cpu_percent <= 100):
#             raise ValueError(f"cpu_percent must be 1-100, got {self.cpu_percent}")
#         if self.memory_mb <= 0:
#             raise ValueError(f"memory_mb must be >0, got {self.memory_mb}")
#         if self.execution_timeout_sec <= 0:
#             raise ValueError(f"execution_timeout_sec must be >0, got {self.execution_timeout_sec}")
