from enum import Enum


class SearchMappingRuleDataSortItemField(str, Enum):
    CLAIMNAME = "claimName"
    CLAIMVALUE = "claimValue"
    MAPPINGRULEID = "mappingRuleId"
    NAME = "name"

    def __str__(self) -> str:
        return str(self.value)
