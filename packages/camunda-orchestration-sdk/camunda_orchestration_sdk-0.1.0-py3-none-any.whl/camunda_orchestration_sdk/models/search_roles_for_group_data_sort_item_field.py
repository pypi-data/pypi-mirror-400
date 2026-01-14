from enum import Enum


class SearchRolesForGroupDataSortItemField(str, Enum):
    NAME = "name"
    ROLEID = "roleId"

    def __str__(self) -> str:
        return str(self.value)
