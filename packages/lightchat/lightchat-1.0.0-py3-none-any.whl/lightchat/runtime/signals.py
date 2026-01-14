# # src/lightchat/runtime/signals.py

# import signal
# import sys
# from lightchat.constants import SignalLevel
# from lightchat.exceptions import LightChatError


# class LightChatSignalError(LightChatError):
#     """Signal handling error."""
#     pass


# # Base mappings (portable)
# SYSTEM_SIGNALS = {
#     SignalLevel.GRACEFUL: signal.SIGTERM,
#     SignalLevel.FORCED: signal.SIGINT,
# }

# # HARD_KILL is platform-specific
# if sys.platform.startswith("win"):
#     # Windows has NO SIGKILL → handled via Popen.kill()
#     SYSTEM_SIGNALS[SignalLevel.HARD_KILL] = None
# else:
#     SYSTEM_SIGNALS[SignalLevel.HARD_KILL] = signal.SIGKILL


# def get_signal(level: SignalLevel):
#     """
#     Return the system signal for a given SignalLevel.
#     Returns None for Windows HARD_KILL (caller must handle).
#     """
#     if level not in SYSTEM_SIGNALS:
#         raise LightChatSignalError(f"Unsupported signal level: {level}")
#     return SYSTEM_SIGNALS[level]
