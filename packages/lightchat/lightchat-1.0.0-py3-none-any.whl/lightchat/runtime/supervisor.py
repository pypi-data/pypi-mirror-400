# # src/lightchat/runtime/supervisor.py

# from typing import Dict
# from lightchat.constants import ProcessState, SignalLevel
# from lightchat.exceptions import RuntimeExecutionError
# from .process import LightChatProcess


# class Supervisor:
#     """
#     Supervises multiple LightChatProcess instances.
#     """

#     def __init__(self):
#         self._processes: Dict[str, LightChatProcess] = {}

#     def register(self, proc: LightChatProcess) -> None:
#         if proc.name in self._processes:
#             raise RuntimeExecutionError(
#                 f"Process with name '{proc.name}' already registered."
#             )
#         self._processes[proc.name] = proc

#     def unregister(self, proc_name: str) -> None:
#         self._processes.pop(proc_name, None)

#     def start_all(self) -> None:
#         for proc in self._processes.values():
#             proc.start()

#     def terminate_all(self, level: SignalLevel = SignalLevel.GRACEFUL) -> None:
#         for proc in self._processes.values():
#             proc.terminate(level=level)

#     def monitor(self) -> Dict[str, ProcessState]:
#         return {name: proc.state for name, proc in self._processes.items()}

#     def restart_failed(self) -> None:
#         for proc in self._processes.values():
#             if proc.state == ProcessState.FAILED:
#                 try:
#                     proc.terminate(level=SignalLevel.HARD_KILL)
#                     proc.start()
#                 except RuntimeExecutionError:
#                     pass
