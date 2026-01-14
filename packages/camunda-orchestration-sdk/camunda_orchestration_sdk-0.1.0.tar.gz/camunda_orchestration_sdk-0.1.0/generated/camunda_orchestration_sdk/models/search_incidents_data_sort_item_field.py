from enum import Enum


class SearchIncidentsDataSortItemField(str, Enum):
    CREATIONTIME = "creationTime"
    ELEMENTID = "elementId"
    ELEMENTINSTANCEKEY = "elementInstanceKey"
    ERRORMESSAGE = "errorMessage"
    ERRORTYPE = "errorType"
    INCIDENTKEY = "incidentKey"
    JOBKEY = "jobKey"
    PROCESSDEFINITIONID = "processDefinitionId"
    PROCESSDEFINITIONKEY = "processDefinitionKey"
    PROCESSINSTANCEKEY = "processInstanceKey"
    STATE = "state"
    TENANTID = "tenantId"

    def __str__(self) -> str:
        return str(self.value)
