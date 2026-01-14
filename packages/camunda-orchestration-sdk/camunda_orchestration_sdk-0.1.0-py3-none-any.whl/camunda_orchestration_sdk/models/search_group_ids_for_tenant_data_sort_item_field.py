from enum import Enum


class SearchGroupIdsForTenantDataSortItemField(str, Enum):
    GROUPID = "groupId"

    def __str__(self) -> str:
        return str(self.value)
