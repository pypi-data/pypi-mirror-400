# src/lightchat/exceptions.py

from typing import Optional


class LightChatError(Exception):
    """Base class for all LightChat exceptions."""
    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "An unknown LightChat error occurred."
        super().__init__(message)


# Runtime Errors
class RuntimeExecutionError(LightChatError):
    """Raised when a runtime process fails unexpectedly."""
    pass


# Resource Limit Errors
class ResourceLimitError(LightChatError):
    """Raised when a process exceeds its allocated resource limits."""
    pass


# Security Policy Errors
class SecurityPolicyError(LightChatError):
    """Raised when a process violates a security policy."""
    pass


# Inter-Process Communication Errors
class IPCError(LightChatError):
    """Raised for IPC message protocol violations or queue failures."""
    pass


# Configuration Errors
class ConfigurationError(LightChatError):
    """Raised when configuration loading or validation fails."""
    pass
