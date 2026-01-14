from enum import Enum


class SearchUsersForGroupDataSortItemField(str, Enum):
    USERNAME = "username"

    def __str__(self) -> str:
        return str(self.value)
