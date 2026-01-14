from enum import Enum


class ListenereventtypeAdvancedfilterNeq(str, Enum):
    ASSIGNING = "ASSIGNING"
    CANCELING = "CANCELING"
    COMPLETING = "COMPLETING"
    CREATING = "CREATING"
    END = "END"
    START = "START"
    UNSPECIFIED = "UNSPECIFIED"
    UPDATING = "UPDATING"

    def __str__(self) -> str:
        return str(self.value)
