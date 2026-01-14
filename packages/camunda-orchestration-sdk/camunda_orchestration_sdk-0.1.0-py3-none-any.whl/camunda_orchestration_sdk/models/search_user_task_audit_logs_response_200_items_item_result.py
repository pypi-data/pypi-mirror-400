from enum import Enum


class SearchUserTaskAuditLogsResponse200ItemsItemResult(str, Enum):
    FAIL = "FAIL"
    SUCCESS = "SUCCESS"

    def __str__(self) -> str:
        return str(self.value)
