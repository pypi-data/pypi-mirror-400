# src/lightchat/security/core.py

import os
from dataclasses import dataclass, field
from typing import List, Optional
from contextlib import contextmanager
import threading
import logging

from lightchat.runtime.runtime_core import LightChatProcess
from lightchat.exceptions import SecurityPolicyError

# --------------------------
# Logger Setup
# --------------------------
logger = logging.getLogger("LightChatSecurity")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# --------------------------
# Security Policy
# --------------------------
@dataclass(frozen=True)
class SecurityPolicy:
    """
    Defines security rules for LightChat process execution.
    """
    allow_files: List[str] = field(default_factory=list)
    deny_files: List[str] = field(default_factory=list)
    allow_network: bool = False
    deny_network: bool = True
    allowed_env_vars: Optional[List[str]] = None  # None = only default safe vars

    def validate(self) -> None:
        """
        Validate the security policy for conflicts.
        """
        # Conflicting file rules
        conflicts = set(self.allow_files) & set(self.deny_files)
        if conflicts:
            raise SecurityPolicyError(f"Files cannot be both allowed and denied: {conflicts}")

        # Conflicting network rules
        if self.allow_network and self.deny_network:
            raise SecurityPolicyError("Cannot allow and deny network simultaneously.")

        # Environment variables validation
        if self.allowed_env_vars is not None:
            if not all(isinstance(var, str) for var in self.allowed_env_vars):
                raise SecurityPolicyError("All allowed_env_vars must be strings.")


# --------------------------
# Permissions Enforcer
# --------------------------
class PermissionsEnforcer:
    """
    Enforces security policies on filesystem, network, and environment.
    """

    def __init__(self, policy: SecurityPolicy):
        self.policy = policy
        self.policy.validate()
        self._lock = threading.Lock()

    # ------------------------
    # Filesystem enforcement
    # ------------------------
    def check_file_access(self, path: str) -> None:
        """
        Ensure the file access is allowed by policy.
        """
        path_obj = os.path.abspath(path)

        with self._lock:
            # Deny check
            for denied in self.policy.deny_files:
                if path_obj.endswith(denied):
                    raise SecurityPolicyError(f"Access to file denied by policy: {path_obj}")

            # Allow check (if allow list exists)
            if self.policy.allow_files and not any(path_obj.endswith(f) for f in self.policy.allow_files):
                raise SecurityPolicyError(f"Access to file not explicitly allowed by policy: {path_obj}")

    # ------------------------
    # Environment enforcement
    # ------------------------
    def sanitize_env(self, env: dict) -> dict:
        """
        Filter environment variables according to policy.
        """
        with self._lock:
            if self.policy.allowed_env_vars is None:
                # Return only default safe env (minimal)
                safe_keys = ["PATH", "HOME", "USER", "TMPDIR"]
                return {k: v for k, v in env.items() if k in safe_keys}

            # Return only allowed vars
            return {k: v for k, v in env.items() if k in self.policy.allowed_env_vars}

    # ------------------------
    # Network enforcement
    # ------------------------
    def check_network_access(self) -> None:
        """
        Raise error if network access is denied.
        """
        with self._lock:
            if self.policy.deny_network:
                raise SecurityPolicyError("Network access denied by policy.")


# --------------------------
# Sandbox Execution
# --------------------------
class Sandbox:
    """
    Restricted execution context for a LightChatProcess.
    Applies security policies before runtime start.
    """

    def __init__(self, process: LightChatProcess, policy: SecurityPolicy):
        self.process = process
        self.policy = policy
        self.enforcer = PermissionsEnforcer(policy)
        self._lock = threading.Lock()

    def preflight(self) -> None:
        """
        Validate that process environment and access is secure.
        """
        with self._lock:
            # Sanitize environment variables
            self.process.env = self.enforcer.sanitize_env(self.process.env)
            logger.info(f"Environment sanitized for process '{self.process.name}'")

            # Check all files in command exist and are allowed
            for part in self.process.command:
                if isinstance(part, str) and os.path.exists(part):
                    self.enforcer.check_file_access(part)
                    logger.debug(f"File access allowed by policy: {part}")

            # Check network access
            if not self.policy.allow_network:
                self.enforcer.check_network_access()
                logger.debug(f"Network access checked for process '{self.process.name}'")

    @contextmanager
    def execute(self):
        """
        Context manager to run process in a sandbox.
        Preflight checks applied before starting.
        """
        self.preflight()
        try:
            logger.info(f"Executing process '{self.process.name}' in sandbox")
            yield self.process
        finally:
            # Cleanup hooks or temp file deletion could go here
            logger.info(f"Exiting sandbox for process '{self.process.name}'")
