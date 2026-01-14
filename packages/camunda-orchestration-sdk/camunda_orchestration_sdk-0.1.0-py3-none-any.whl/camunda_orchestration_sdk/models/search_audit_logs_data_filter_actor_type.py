from enum import Enum


class SearchAuditLogsDataFilterActorType(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    CLIENT = "CLIENT"
    UNKNOWN = "UNKNOWN"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
