from enum import Enum


class SearchDecisionInstancesDataSortItemField(str, Enum):
    DECISIONDEFINITIONID = "decisionDefinitionId"
    DECISIONDEFINITIONKEY = "decisionDefinitionKey"
    DECISIONDEFINITIONNAME = "decisionDefinitionName"
    DECISIONDEFINITIONTYPE = "decisionDefinitionType"
    DECISIONDEFINITIONVERSION = "decisionDefinitionVersion"
    DECISIONEVALUATIONINSTANCEKEY = "decisionEvaluationInstanceKey"
    DECISIONEVALUATIONKEY = "decisionEvaluationKey"
    ELEMENTINSTANCEKEY = "elementInstanceKey"
    EVALUATIONDATE = "evaluationDate"
    EVALUATIONFAILURE = "evaluationFailure"
    PROCESSDEFINITIONKEY = "processDefinitionKey"
    PROCESSINSTANCEKEY = "processInstanceKey"
    ROOTDECISIONDEFINITIONKEY = "rootDecisionDefinitionKey"
    STATE = "state"
    TENANTID = "tenantId"

    def __str__(self) -> str:
        return str(self.value)
