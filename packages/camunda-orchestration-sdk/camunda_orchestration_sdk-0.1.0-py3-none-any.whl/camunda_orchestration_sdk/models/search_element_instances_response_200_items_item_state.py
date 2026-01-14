from enum import Enum


class SearchElementInstancesResponse200ItemsItemState(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"

    def __str__(self) -> str:
        return str(self.value)
