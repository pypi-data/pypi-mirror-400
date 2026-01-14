from enum import Enum


class SearchProcessDefinitionsDataSortItemField(str, Enum):
    NAME = "name"
    PROCESSDEFINITIONID = "processDefinitionId"
    PROCESSDEFINITIONKEY = "processDefinitionKey"
    RESOURCENAME = "resourceName"
    TENANTID = "tenantId"
    VERSION = "version"
    VERSIONTAG = "versionTag"

    def __str__(self) -> str:
        return str(self.value)
