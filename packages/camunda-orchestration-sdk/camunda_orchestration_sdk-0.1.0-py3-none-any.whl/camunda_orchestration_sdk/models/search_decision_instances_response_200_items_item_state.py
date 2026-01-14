from enum import Enum


class SearchDecisionInstancesResponse200ItemsItemState(str, Enum):
    EVALUATED = "EVALUATED"
    FAILED = "FAILED"
    UNSPECIFIED = "UNSPECIFIED"

    def __str__(self) -> str:
        return str(self.value)
