from enum import Enum


class NodeDetailState(str, Enum):
    ALLOCATED = "ALLOCATED"
    DOWN = "DOWN"
    DRAINED = "DRAINED"
    DRAINING = "DRAINING"
    IDLE = "IDLE"
    MIXED = "MIXED"

    def __str__(self) -> str:
        return str(self.value)
