from enum import Enum


class SearchAuditLogsDataSortItemField(str, Enum):
    ACTORID = "actorId"
    ACTORTYPE = "actorType"
    ANNOTATION = "annotation"
    AUDITLOGKEY = "auditLogKey"
    BATCHOPERATIONKEY = "batchOperationKey"
    BATCHOPERATIONTYPE = "batchOperationType"
    CATEGORY = "category"
    DECISIONDEFINITIONID = "decisionDefinitionId"
    DECISIONDEFINITIONKEY = "decisionDefinitionKey"
    DECISIONEVALUATIONKEY = "decisionEvaluationKey"
    DECISIONREQUIREMENTSID = "decisionRequirementsId"
    DECISIONREQUIREMENTSKEY = "decisionRequirementsKey"
    ELEMENTINSTANCEKEY = "elementInstanceKey"
    ENTITYKEY = "entityKey"
    ENTITYTYPE = "entityType"
    JOBKEY = "jobKey"
    OPERATIONTYPE = "operationType"
    PROCESSDEFINITIONID = "processDefinitionId"
    PROCESSDEFINITIONKEY = "processDefinitionKey"
    PROCESSINSTANCEKEY = "processInstanceKey"
    RESULT = "result"
    TENANTID = "tenantId"
    TIMESTAMP = "timestamp"
    USERTASKKEY = "userTaskKey"

    def __str__(self) -> str:
        return str(self.value)
