from enum import Enum


class SearchUserTaskAuditLogsResponse200ItemsItemEntityType(str, Enum):
    AUTHORIZATION = "AUTHORIZATION"
    BATCH = "BATCH"
    DECISION = "DECISION"
    GROUP = "GROUP"
    INCIDENT = "INCIDENT"
    MAPPING_RULE = "MAPPING_RULE"
    PROCESS_INSTANCE = "PROCESS_INSTANCE"
    RESOURCE = "RESOURCE"
    ROLE = "ROLE"
    TENANT = "TENANT"
    USER = "USER"
    USER_TASK = "USER_TASK"
    VARIABLE = "VARIABLE"

    def __str__(self) -> str:
        return str(self.value)
