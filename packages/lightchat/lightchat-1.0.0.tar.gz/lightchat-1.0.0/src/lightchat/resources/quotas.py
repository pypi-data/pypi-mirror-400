# # src/lightchat/resources/quotas.py

# from typing import Dict, Optional
# from lightchat.resources.monitor import ResourceMonitor
# from lightchat.runtime.process import LightChatProcess
# from lightchat.exceptions import ResourceLimitError
# from lightchat.constants import ProcessState


# class QuotaManager:
#     """
#     Tracks resource quotas for multiple processes and enforces limits.
#     """

#     def __init__(self):
#         self._monitors: Dict[str, ResourceMonitor] = {}

#     def register(self, process: LightChatProcess, monitor: Optional[ResourceMonitor] = None) -> None:
#         """Register a process and its monitor."""
#         if process.name in self._monitors:
#             raise ResourceLimitError(f"Process '{process.name}' already registered in quota manager.")

#         if monitor is None:
#             monitor = ResourceMonitor(process)
#         monitor.start()
#         self._monitors[process.name] = monitor

#     def enforce(self) -> None:
#         """
#         Enforce quotas: terminate processes exceeding limits.
#         """
#         for name, monitor in self._monitors.items():
#             try:
#                 monitor.check()
#             except ResourceLimitError:
#                 process = monitor.process
#                 if process.state == ProcessState.RUNNING:
#                     process.terminate()
