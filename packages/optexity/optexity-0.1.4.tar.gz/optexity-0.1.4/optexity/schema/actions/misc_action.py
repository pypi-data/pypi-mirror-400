from pydantic import BaseModel


class PythonScriptAction(BaseModel):
    execution_code: str


## State Jump Actions
class StateJumpAction(BaseModel):
    next_state_index: int


# class RestartAction(StateJumpAction):
#     next_state_index: 0


# class StopAction(StateJumpAction):
#     next_state_index: -1
