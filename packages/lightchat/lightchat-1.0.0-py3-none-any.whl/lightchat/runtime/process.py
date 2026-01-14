# # src/lightchat/runtime/process.py

# import subprocess
# import os
# import sys
# from typing import Optional, List, Dict

# from lightchat.constants import ProcessState, SignalLevel
# from lightchat.exceptions import RuntimeExecutionError
# from .state import assert_transition
# from .signals import get_signal


# class LightChatProcess:
#     """
#     Encapsulates a managed OS process with strict lifecycle control.
#     """

#     def __init__(
#         self,
#         command: List[str],
#         env: Optional[Dict[str, str]] = None,
#         cwd: Optional[str] = None,
#         name: Optional[str] = None,
#     ):
#         self.command = command
#         self.env = env or os.environ.copy()
#         self.cwd = cwd
#         self.name = name or "LightChatProcess"
#         self.state = ProcessState.CREATED
#         self._proc: Optional[subprocess.Popen] = None

#     def start(self) -> None:
#         assert_transition(self.state, ProcessState.INITIALIZING)
#         self.state = ProcessState.INITIALIZING

#         try:
#             self._proc = subprocess.Popen(
#                 self.command,
#                 env=self.env,
#                 cwd=self.cwd,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 text=True,
#             )
#             self.state = ProcessState.RUNNING
#         except Exception as e:
#             self.state = ProcessState.FAILED
#             raise RuntimeExecutionError(f"Failed to start process: {e}") from e

#     def terminate(self, level: SignalLevel = SignalLevel.GRACEFUL) -> None:
#         if not self._proc or self.state in {ProcessState.COMPLETED, ProcessState.TERMINATED}:
#             return

#         try:
#             sig = get_signal(level)

#             if sig is None:
#                 # Windows HARD_KILL
#                 self._proc.kill()
#             else:
#                 self._proc.send_signal(sig)

#         except Exception as e:
#             raise RuntimeExecutionError(f"Failed to terminate process: {e}") from e
#         finally:
#             self.state = ProcessState.TERMINATED

#     def wait(self, timeout: Optional[float] = None) -> int:
#         if not self._proc:
#             raise RuntimeExecutionError("Process not started.")

#         try:
#             retcode = self._proc.wait(timeout=timeout)
#             self.state = (
#                 ProcessState.COMPLETED if retcode == 0 else ProcessState.FAILED
#             )
#             return retcode

#         except subprocess.TimeoutExpired:
#             self.terminate(level=SignalLevel.HARD_KILL)
#             self.state = ProcessState.FAILED
#             raise RuntimeExecutionError("Process timed out and was forcefully terminated.")
