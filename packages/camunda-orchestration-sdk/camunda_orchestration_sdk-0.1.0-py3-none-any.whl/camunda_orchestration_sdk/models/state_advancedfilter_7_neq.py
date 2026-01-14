from enum import Enum


class StateAdvancedfilter7Neq(str, Enum):
    ASSIGNING = "ASSIGNING"
    CANCELED = "CANCELED"
    CANCELING = "CANCELING"
    COMPLETED = "COMPLETED"
    COMPLETING = "COMPLETING"
    CREATED = "CREATED"
    CREATING = "CREATING"
    FAILED = "FAILED"
    UPDATING = "UPDATING"

    def __str__(self) -> str:
        return str(self.value)
