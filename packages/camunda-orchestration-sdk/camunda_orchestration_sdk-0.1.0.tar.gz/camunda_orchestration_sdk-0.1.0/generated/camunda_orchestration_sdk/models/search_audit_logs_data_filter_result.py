from enum import Enum


class SearchAuditLogsDataFilterResult(str, Enum):
    FAIL = "FAIL"
    SUCCESS = "SUCCESS"

    def __str__(self) -> str:
        return str(self.value)
