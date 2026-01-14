from enum import Enum


class GetProcessInstanceStatisticsByDefinitionDataSortItemField(str, Enum):
    ACTIVEINSTANCESWITHERRORCOUNT = "activeInstancesWithErrorCount"
    PROCESSDEFINITIONID = "processDefinitionId"
    PROCESSDEFINITIONKEY = "processDefinitionKey"
    PROCESSDEFINITIONNAME = "processDefinitionName"
    PROCESSDEFINITIONVERSION = "processDefinitionVersion"
    TENANTID = "tenantId"

    def __str__(self) -> str:
        return str(self.value)
