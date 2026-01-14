from enum import Enum


class SearchRolesForTenantDataSortItemField(str, Enum):
    NAME = "name"
    ROLEID = "roleId"

    def __str__(self) -> str:
        return str(self.value)
