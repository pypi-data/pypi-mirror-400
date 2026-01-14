from enum import Enum


class StateAdvancedfilter1Neq(str, Enum):
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"
    CREATED = "CREATED"
    FAILED = "FAILED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    SUSPENDED = "SUSPENDED"

    def __str__(self) -> str:
        return str(self.value)
