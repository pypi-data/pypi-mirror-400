# # src/lightchat/ipc/protocol.py

# from typing import Any, Dict, Optional
# from dataclasses import dataclass, field
# from lightchat.exceptions import IPCError


# @dataclass(frozen=True)
# class IPCMessage:
#     """
#     Standardized IPC message format.
#     """
#     sender: str
#     receiver: str
#     payload: Dict[str, Any]
#     msg_id: Optional[str] = None
#     timestamp: Optional[float] = None

#     def validate(self) -> None:
#         """
#         Validate message structure.
#         """
#         if not self.sender or not isinstance(self.sender, str):
#             raise IPCError("IPCMessage sender must be a non-empty string")
#         if not self.receiver or not isinstance(self.receiver, str):
#             raise IPCError("IPCMessage receiver must be a non-empty string")
#         if not isinstance(self.payload, dict):
#             raise IPCError("IPCMessage payload must be a dict")
