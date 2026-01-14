from enum import Enum


class SearchBatchOperationsResponse200ItemsItemErrorsItemType(str, Enum):
    QUERY_FAILED = "QUERY_FAILED"
    RESULT_BUFFER_SIZE_EXCEEDED = "RESULT_BUFFER_SIZE_EXCEEDED"

    def __str__(self) -> str:
        return str(self.value)
