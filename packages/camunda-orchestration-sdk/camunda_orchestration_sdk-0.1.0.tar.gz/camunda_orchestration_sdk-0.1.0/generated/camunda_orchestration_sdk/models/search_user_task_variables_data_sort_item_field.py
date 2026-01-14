from enum import Enum


class SearchUserTaskVariablesDataSortItemField(str, Enum):
    NAME = "name"
    PROCESSINSTANCEKEY = "processInstanceKey"
    SCOPEKEY = "scopeKey"
    TENANTID = "tenantId"
    VALUE = "value"
    VARIABLEKEY = "variableKey"

    def __str__(self) -> str:
        return str(self.value)
