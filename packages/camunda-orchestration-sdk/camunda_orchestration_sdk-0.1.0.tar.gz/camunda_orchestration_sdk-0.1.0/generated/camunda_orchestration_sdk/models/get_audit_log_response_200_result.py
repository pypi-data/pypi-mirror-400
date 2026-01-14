from enum import Enum


class GetAuditLogResponse200Result(str, Enum):
    FAIL = "FAIL"
    SUCCESS = "SUCCESS"

    def __str__(self) -> str:
        return str(self.value)
