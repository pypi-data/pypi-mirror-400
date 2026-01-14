# # src/lightchat/security/policy.py

# from dataclasses import dataclass, field
# from typing import List, Optional
# from lightchat.exceptions import SecurityPolicyError


# @dataclass(frozen=True)
# class SecurityPolicy:
#     """
#     Defines security rules for LightChat process execution.
#     """
#     allow_files: List[str] = field(default_factory=list)
#     deny_files: List[str] = field(default_factory=list)
#     allow_network: bool = False
#     deny_network: bool = True
#     allowed_env_vars: Optional[List[str]] = None  # None = only default safe vars

#     def validate(self) -> None:
#         """
#         Validate the security policy.
#         """
#         # Conflicting rules
#         conflicts = set(self.allow_files) & set(self.deny_files)
#         if conflicts:
#             raise SecurityPolicyError(f"Files cannot be both allowed and denied: {conflicts}")

#         if self.allow_network and self.deny_network:
#             raise SecurityPolicyError("Cannot allow and deny network simultaneously.")

#         if self.allowed_env_vars is not None:
#             if not all(isinstance(var, str) for var in self.allowed_env_vars):
#                 raise SecurityPolicyError("All allowed_env_vars must be strings")
