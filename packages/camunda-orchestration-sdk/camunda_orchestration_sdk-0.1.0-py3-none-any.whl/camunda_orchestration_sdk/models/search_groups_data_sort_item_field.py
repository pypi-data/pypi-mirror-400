from enum import Enum


class SearchGroupsDataSortItemField(str, Enum):
    GROUPID = "groupId"
    NAME = "name"

    def __str__(self) -> str:
        return str(self.value)
