from enum import Enum


class StopReason(str, Enum):
    END_TURN = "end_turn"
    TOOL_USE = "tool_use"
