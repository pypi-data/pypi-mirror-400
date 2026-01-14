from enum import Enum


class SearchTenantsDataSortItemField(str, Enum):
    KEY = "key"
    NAME = "name"
    TENANTID = "tenantId"

    def __str__(self) -> str:
        return str(self.value)
