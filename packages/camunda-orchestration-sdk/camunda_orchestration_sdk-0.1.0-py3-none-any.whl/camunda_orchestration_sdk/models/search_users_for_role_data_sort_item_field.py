from enum import Enum


class SearchUsersForRoleDataSortItemField(str, Enum):
    USERNAME = "username"

    def __str__(self) -> str:
        return str(self.value)
