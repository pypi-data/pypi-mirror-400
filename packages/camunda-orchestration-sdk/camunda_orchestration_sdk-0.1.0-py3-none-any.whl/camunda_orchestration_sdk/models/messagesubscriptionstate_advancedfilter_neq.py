from enum import Enum


class MessagesubscriptionstateAdvancedfilterNeq(str, Enum):
    CORRELATED = "CORRELATED"
    CREATED = "CREATED"
    DELETED = "DELETED"
    MIGRATED = "MIGRATED"

    def __str__(self) -> str:
        return str(self.value)
