# # src/lightchat/runtime/state.py

# from typing import Dict, List
# from lightchat.constants import ProcessState
# from lightchat.exceptions import LightChatError


# VALID_TRANSITIONS: Dict[ProcessState, List[ProcessState]] = {
#     ProcessState.CREATED: [ProcessState.INITIALIZING, ProcessState.TERMINATED],
#     ProcessState.INITIALIZING: [ProcessState.RUNNING, ProcessState.FAILED, ProcessState.TERMINATED],
#     ProcessState.RUNNING: [ProcessState.COMPLETED, ProcessState.FAILED, ProcessState.TERMINATED],
#     ProcessState.COMPLETED: [ProcessState.TERMINATED],
#     ProcessState.FAILED: [ProcessState.TERMINATED],
#     ProcessState.TERMINATED: [],
# }


# def is_valid_transition(current: ProcessState, next_state: ProcessState) -> bool:
#     return next_state in VALID_TRANSITIONS.get(current, [])


# def assert_transition(current: ProcessState, next_state: ProcessState) -> None:
#     if not is_valid_transition(current, next_state):
#         raise LightChatError(
#             f"Invalid state transition: {current.name} → {next_state.name}"
#         )
