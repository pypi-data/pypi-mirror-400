from enum import Enum


class SearchJobsDataSortItemField(str, Enum):
    DEADLINE = "deadline"
    DENIEDREASON = "deniedReason"
    ELEMENTID = "elementId"
    ELEMENTINSTANCEKEY = "elementInstanceKey"
    ENDTIME = "endTime"
    ERRORCODE = "errorCode"
    ERRORMESSAGE = "errorMessage"
    HASFAILEDWITHRETRIESLEFT = "hasFailedWithRetriesLeft"
    ISDENIED = "isDenied"
    JOBKEY = "jobKey"
    KIND = "kind"
    LISTENEREVENTTYPE = "listenerEventType"
    PROCESSDEFINITIONID = "processDefinitionId"
    PROCESSDEFINITIONKEY = "processDefinitionKey"
    PROCESSINSTANCEKEY = "processInstanceKey"
    RETRIES = "retries"
    STATE = "state"
    TENANTID = "tenantId"
    TYPE = "type"
    WORKER = "worker"

    def __str__(self) -> str:
        return str(self.value)
