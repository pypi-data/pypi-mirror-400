# # src/lightchat/observability/logging.py

# import logging
# import uuid
# from contextvars import ContextVar
# from typing import Optional

# correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


# def get_correlation_id() -> str:
#     cid = correlation_id.get()
#     if cid is None:
#         cid = str(uuid.uuid4())
#         correlation_id.set(cid)
#     return cid


# class LightChatLogger:
#     """
#     Structured logger for LightChat.
#     Safe for multi-process and cross-platform use.
#     """

#     def __init__(self, name: str):
#         self._logger = logging.getLogger(name)

#         if not self._logger.handlers:
#             self._logger.setLevel(logging.INFO)

#             handler = logging.StreamHandler()
#             formatter = logging.Formatter(
#                 "[%(asctime)s] [%(levelname)s] [%(name)s] [cid=%(correlation_id)s] %(message)s"
#             )
#             handler.setFormatter(formatter)
#             self._logger.addHandler(handler)

#             self._logger.propagate = False

#     def _log(self, level: int, msg: str, **kwargs):
#         self._logger.log(
#             level,
#             msg,
#             extra={"correlation_id": get_correlation_id()},
#             **kwargs
#         )

#     def debug(self, msg: str, **kwargs):
#         self._log(logging.DEBUG, msg, **kwargs)

#     def info(self, msg: str, **kwargs):
#         self._log(logging.INFO, msg, **kwargs)

#     def warning(self, msg: str, **kwargs):
#         self._log(logging.WARNING, msg, **kwargs)

#     def error(self, msg: str, **kwargs):
#         self._log(logging.ERROR, msg, **kwargs)

#     def critical(self, msg: str, **kwargs):
#         self._log(logging.CRITICAL, msg, **kwargs)
