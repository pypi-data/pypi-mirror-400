# # src/lightchat/resources/monitor.py

# import psutil
# import time
# from typing import Optional
# from lightchat.resources.limits import ResourceLimits
# from lightchat.exceptions import ResourceLimitError
# from lightchat.runtime.process import LightChatProcess


# class ResourceMonitor:
#     """
#     Monitors a LightChatProcess for CPU, memory, and execution time.
#     """

#     def __init__(self, process: LightChatProcess, limits: Optional[ResourceLimits] = None):
#         self.process = process
#         self.limits = limits or ResourceLimits()
#         self._start_time: Optional[float] = None
#         self._psutil_proc: Optional[psutil.Process] = None

#     def start(self) -> None:
#         """Initialize monitoring."""
#         if self.process._proc is None:
#             raise ResourceLimitError("Process must be started before monitoring.")

#         self._psutil_proc = psutil.Process(self.process._proc.pid)
#         self._start_time = time.time()

#     def check(self) -> None:
#         """
#         Check current resource usage and raise ResourceLimitError if limits exceeded.
#         """
#         if self._psutil_proc is None:
#             raise ResourceLimitError("Monitor not started.")

#         # CPU usage percent
#         cpu = self._psutil_proc.cpu_percent(interval=0.1)
#         if cpu > self.limits.cpu_percent:
#             raise ResourceLimitError(f"CPU limit exceeded: {cpu:.2f}% > {self.limits.cpu_percent}%")

#         # Memory usage in MB
#         mem = self._psutil_proc.memory_info().rss / (1024 * 1024)
#         if mem > self.limits.memory_mb:
#             raise ResourceLimitError(f"Memory limit exceeded: {mem:.2f}MB > {self.limits.memory_mb}MB")

#         # Execution time
#         elapsed = time.time() - (self._start_time or time.time())
#         if elapsed > self.limits.execution_timeout_sec:
#             raise ResourceLimitError(
#                 f"Execution timeout exceeded: {elapsed:.2f}s > {self.limits.execution_timeout_sec}s"
#             )
