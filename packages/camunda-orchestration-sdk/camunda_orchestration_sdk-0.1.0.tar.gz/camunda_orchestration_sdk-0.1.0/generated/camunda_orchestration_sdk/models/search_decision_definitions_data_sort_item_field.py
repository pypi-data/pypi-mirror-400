from enum import Enum


class SearchDecisionDefinitionsDataSortItemField(str, Enum):
    DECISIONDEFINITIONID = "decisionDefinitionId"
    DECISIONDEFINITIONKEY = "decisionDefinitionKey"
    DECISIONREQUIREMENTSID = "decisionRequirementsId"
    DECISIONREQUIREMENTSKEY = "decisionRequirementsKey"
    DECISIONREQUIREMENTSNAME = "decisionRequirementsName"
    DECISIONREQUIREMENTSVERSION = "decisionRequirementsVersion"
    NAME = "name"
    TENANTID = "tenantId"
    VERSION = "version"

    def __str__(self) -> str:
        return str(self.value)
