from enum import Enum


class SearchClusterVariablesDataSortItemField(str, Enum):
    NAME = "name"
    SCOPE = "scope"
    TENANTID = "tenantId"
    VALUE = "value"

    def __str__(self) -> str:
        return str(self.value)
