from enum import Enum


class StateExactmatch4(str, Enum):
    ACTIVE = "ACTIVE"
    MIGRATED = "MIGRATED"
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"

    def __str__(self) -> str:
        return str(self.value)
