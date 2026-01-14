from enum import Enum


class StateAdvancedfilterEq(str, Enum):
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    def __str__(self) -> str:
        return str(self.value)
