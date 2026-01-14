# src/lightchat/ipc/core.py

import queue
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
import time
import threading
import logging

from lightchat.exceptions import IPCError

# --------------------------
# Logger Setup
# --------------------------
logger = logging.getLogger("LightChatIPC")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# --------------------------
# IPC Message Protocol
# --------------------------
@dataclass(frozen=True)
class IPCMessage:
    """
    Standardized IPC message format.
    """
    sender: str
    receiver: str
    payload: Dict[str, Any]
    msg_id: Optional[str] = None
    timestamp: Optional[float] = None

    def validate(self) -> None:
        """
        Validate the message structure.
        """
        if not self.sender or not isinstance(self.sender, str):
            raise IPCError("IPCMessage sender must be a non-empty string")
        if not self.receiver or not isinstance(self.receiver, str):
            raise IPCError("IPCMessage receiver must be a non-empty string")
        if not isinstance(self.payload, dict):
            raise IPCError("IPCMessage payload must be a dict")
        if self.msg_id is not None and not isinstance(self.msg_id, str):
            raise IPCError("IPCMessage msg_id must be a string if provided")
        if self.timestamp is not None and not isinstance(self.timestamp, (int, float)):
            raise IPCError("IPCMessage timestamp must be numeric if provided")


# --------------------------
# IPC Channel Interface
# --------------------------
class IPCChannel(ABC):
    """
    Abstract communication channel interface.
    """

    @abstractmethod
    def send(self, message: IPCMessage) -> None:
        """
        Send a message to another process.
        """
        pass

    @abstractmethod
    def receive(self, timeout: Optional[float] = None) -> IPCMessage:
        """
        Receive a message from the channel.
        If timeout is None, block indefinitely.
        """
        pass


# --------------------------
# Queue-based IPC Implementation
# --------------------------
class QueueChannel(IPCChannel):
    """
    Thread-safe queue-based IPC implementation with optional backpressure.
    """

    def __init__(self, max_size: Optional[int] = None):
        """
        Initialize an in-memory message queue.
        """
        self._queue = queue.Queue(maxsize=max_size or 0)
        self._lock = threading.Lock()

    def send(self, message: IPCMessage) -> None:
        """
        Put message into the queue.
        Blocks if queue is full (backpressure).
        """
        message.validate()
        with self._lock:
            try:
                self._queue.put(message, block=True, timeout=1)
                logger.debug(f"Message sent: {message}")
            except queue.Full:
                logger.warning(f"IPC queue is full. Backpressure applied. Message: {message}")
                raise IPCError("IPC queue is full. Backpressure applied.")

    def receive(self, timeout: Optional[float] = None) -> IPCMessage:
        """
        Retrieve message from the queue.
        """
        with self._lock:
            try:
                msg = self._queue.get(block=True, timeout=timeout)
                if not isinstance(msg, IPCMessage):
                    logger.error(f"Invalid message received from IPC queue: {msg}")
                    raise IPCError("Invalid message received from IPC queue")
                logger.debug(f"Message received: {msg}")
                return msg
            except queue.Empty:
                raise IPCError("No message available in IPC queue within timeout")
