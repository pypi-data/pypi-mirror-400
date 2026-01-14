# # src/lightchat/ipc/queue.py

# import queue
# from typing import Optional
# from lightchat.ipc.channel import IPCChannel
# from lightchat.ipc.protocol import IPCMessage
# from lightchat.exceptions import IPCError


# class QueueChannel(IPCChannel):
#     """
#     Queue-based IPC implementation with optional backpressure.
#     """

#     def __init__(self, max_size: Optional[int] = None):
#         """
#         Initialize an in-memory message queue.
#         """
#         self._queue = queue.Queue(maxsize=max_size or 0)

#     def send(self, message: IPCMessage) -> None:
#         """
#         Put message into the queue.
#         Blocks if queue is full (backpressure).
#         """
#         message.validate()
#         try:
#             self._queue.put(message, block=True, timeout=1)
#         except queue.Full:
#             raise IPCError("IPC queue is full. Backpressure applied.")

#     def receive(self, timeout: float = None) -> IPCMessage:
#         """
#         Retrieve message from the queue.
#         """
#         try:
#             msg = self._queue.get(block=True, timeout=timeout)
#             if not isinstance(msg, IPCMessage):
#                 raise IPCError("Invalid message received")
#             return msg
#         except queue.Empty:
#             raise IPCError("No message available in IPC queue within timeout")
