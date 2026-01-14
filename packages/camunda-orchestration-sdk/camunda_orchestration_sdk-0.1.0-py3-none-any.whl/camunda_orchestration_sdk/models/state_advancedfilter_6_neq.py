from enum import Enum


class StateAdvancedfilter6Neq(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"

    def __str__(self) -> str:
        return str(self.value)
