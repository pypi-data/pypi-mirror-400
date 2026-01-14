# # src/lightchat/security/sandbox.py

# import os

# from types import SimpleNamespace
# from contextlib import contextmanager
# from .permissions import PermissionsEnforcer
# from lightchat.security.policy import SecurityPolicy
# from lightchat.runtime.process import LightChatProcess
# from lightchat.exceptions import SecurityPolicyError


# class Sandbox:
#     """
#     Restricted execution context for a LightChatProcess.
#     Applies security policies before runtime start.
#     """

#     def __init__(self, process: LightChatProcess, policy: SecurityPolicy):
#         self.process = process
#         self.policy = policy
#         self.enforcer = PermissionsEnforcer(policy)

#     def preflight(self) -> None:
#         """
#         Validate that process environment and access is secure.
#         """
#         # Sanitize environment
#         self.process.env = self.enforcer.sanitize_env(self.process.env)

#         # Check all files in command exist and allowed
#         for part in self.process.command:
#             if isinstance(part, str) and os.path.exists(part):
#                 self.enforcer.check_file_access(part)

#         # Check network access
#         if not self.policy.allow_network:
#             self.enforcer.check_network_access()

#     @contextmanager
#     def execute(self):
#         """
#         Context manager to run process in a sandbox.
#         Preflight checks applied before starting.
#         """
#         self.preflight()
#         try:
#             yield self.process
#         finally:
#             # Here you could implement cleanup hooks, temp file deletion, etc.
#             pass
