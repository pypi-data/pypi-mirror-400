from enum import Enum


class SearchUsersDataSortItemField(str, Enum):
    EMAIL = "email"
    NAME = "name"
    USERNAME = "username"

    def __str__(self) -> str:
        return str(self.value)
