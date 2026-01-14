# # src/lightchat/config/defaults.py

# from lightchat.security.policy import SecurityPolicy

# # ------------------------
# # Default runtime settings
# # ------------------------
# DEFAULT_MAX_PROCESSES = 10
# DEFAULT_CPU_LIMIT = 50.0      # % CPU per process
# DEFAULT_MEMORY_LIMIT_MB = 256 # MB per process
# DEFAULT_TIMEOUT_SEC = 300     # max execution time per process

# # ------------------------
# # Default security policy
# # ------------------------
# DEFAULT_POLICY = SecurityPolicy(
#     allow_files=[],
#     deny_files=["*"],  # Deny everything by default
#     allow_network=False,
#     deny_network=True,
#     allowed_env_vars=["PATH", "HOME", "USER", "TMPDIR"]
# )

# # ------------------------
# # Default IPC
# # ------------------------
# DEFAULT_IPC_QUEUE_SIZE = 100
