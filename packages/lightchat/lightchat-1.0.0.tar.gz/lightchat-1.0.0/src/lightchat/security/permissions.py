# # src/lightchat/security/permissions.py

# import os
# from pathlib import Path
# from typing import List
# from lightchat.security.policy import SecurityPolicy
# from lightchat.exceptions import SecurityPolicyError


# class PermissionsEnforcer:
#     """
#     Enforces security policies on filesystem, network, and environment.
#     """

#     def __init__(self, policy: SecurityPolicy):
#         self.policy = policy
#         self.policy.validate()

#     # ------------------------
#     # Filesystem enforcement
#     # ------------------------
#     def check_file_access(self, path: str) -> None:
#         """
#         Ensure the file access is allowed by policy.
#         """
#         path_obj = Path(path).resolve()

#         # Deny check
#         for denied in self.policy.deny_files:
#             if path_obj.match(denied):
#                 raise SecurityPolicyError(f"Access to file denied by policy: {path_obj}")

#         # Allow check (if allow list exists)
#         if self.policy.allow_files and not any(path_obj.match(f) for f in self.policy.allow_files):
#             raise SecurityPolicyError(f"Access to file not explicitly allowed by policy: {path_obj}")

#     # ------------------------
#     # Environment enforcement
#     # ------------------------
#     def sanitize_env(self, env: dict) -> dict:
#         """
#         Filter environment variables according to policy.
#         """
#         if self.policy.allowed_env_vars is None:
#             # Return only default safe env (minimal)
#             safe_keys = ["PATH", "HOME", "USER", "TMPDIR"]
#             return {k: v for k, v in env.items() if k in safe_keys}

#         # Return only allowed vars
#         return {k: v for k, v in env.items() if k in self.policy.allowed_env_vars}

#     # ------------------------
#     # Network enforcement
#     # ------------------------
#     def check_network_access(self) -> None:
#         """
#         Raise error if network access is denied.
#         """
#         if self.policy.deny_network:
#             raise SecurityPolicyError("Network access denied by policy.")
