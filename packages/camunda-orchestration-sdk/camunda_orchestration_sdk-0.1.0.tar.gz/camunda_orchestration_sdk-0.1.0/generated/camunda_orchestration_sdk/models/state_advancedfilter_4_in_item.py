from enum import Enum


class StateAdvancedfilter4InItem(str, Enum):
    ACTIVE = "ACTIVE"
    MIGRATED = "MIGRATED"
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"

    def __str__(self) -> str:
        return str(self.value)
