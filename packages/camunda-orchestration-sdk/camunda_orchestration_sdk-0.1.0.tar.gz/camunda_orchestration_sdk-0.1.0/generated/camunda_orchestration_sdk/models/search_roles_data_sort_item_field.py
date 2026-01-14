from enum import Enum


class SearchRolesDataSortItemField(str, Enum):
    NAME = "name"
    ROLEID = "roleId"

    def __str__(self) -> str:
        return str(self.value)
