from enum import Enum


class SearchBatchOperationItemsResponse200ItemsItemState(str, Enum):
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

    def __str__(self) -> str:
        return str(self.value)
