# # src/lightchat/ipc/channel.py

# from abc import ABC, abstractmethod
# from lightchat.ipc.protocol import IPCMessage
# from lightchat.exceptions import IPCError


# class IPCChannel(ABC):
#     """
#     Abstract communication channel interface.
#     """

#     @abstractmethod
#     def send(self, message: IPCMessage) -> None:
#         """
#         Send a message to another process.
#         """
#         pass

#     @abstractmethod
#     def receive(self, timeout: float = None) -> IPCMessage:
#         """
#         Receive a message from the channel.
#         If timeout is None, block indefinitely.
#         """
#         pass
