from enum import Enum


class SearchMappingRulesForRoleDataSortItemField(str, Enum):
    CLAIMNAME = "claimName"
    CLAIMVALUE = "claimValue"
    MAPPINGRULEID = "mappingRuleId"
    NAME = "name"

    def __str__(self) -> str:
        return str(self.value)
