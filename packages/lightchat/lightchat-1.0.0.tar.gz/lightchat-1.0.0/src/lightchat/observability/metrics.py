# # src/lightchat/observability/metrics.py

# import time
# from typing import Dict, Any
# from lightchat.runtime.process import LightChatProcess
# from lightchat.resources.monitor import ResourceMonitor

# class MetricsCollector:
#     """
#     Collects runtime, resource, and failure metrics.
#     """

#     def __init__(self):
#         # Metrics storage
#         self._metrics: Dict[str, Dict[str, Any]] = {}

#     def register_process(self, process: LightChatProcess, monitor: ResourceMonitor) -> None:
#         """
#         Initialize metrics tracking for a process.
#         """
#         self._metrics[process.name] = {
#             "start_time": time.time(),
#             "cpu_usage": [],
#             "memory_usage": [],
#             "status": process.state.name
#         }
#         # Optionally, attach monitor reference
#         self._metrics[process.name]["monitor"] = monitor

#     def update_metrics(self, process_name: str) -> None:
#         """
#         Sample resource usage from monitor.
#         """
#         proc_metrics = self._metrics.get(process_name)
#         if not proc_metrics:
#             return

#         monitor: ResourceMonitor = proc_metrics.get("monitor")
#         if not monitor:
#             return

#         try:
#             monitor.check()  # Will raise ResourceLimitError if exceeded
#             cpu = monitor._psutil_proc.cpu_percent(interval=0.1)
#             mem = monitor._psutil_proc.memory_info().rss / (1024 * 1024)
#             proc_metrics["cpu_usage"].append(cpu)
#             proc_metrics["memory_usage"].append(mem)
#             proc_metrics["status"] = monitor.process.state.name
#         except Exception as e:
#             proc_metrics["status"] = f"error:{type(e).__name__}"

#     def get_metrics(self, process_name: str) -> Dict[str, Any]:
#         """
#         Retrieve collected metrics for a process.
#         """
#         return self._metrics.get(process_name, {})
