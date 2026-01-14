from enum import Enum


class GetProcessDefinitionInstanceVersionStatisticsDataSortItemField(str, Enum):
    ACTIVEINSTANCESWITHINCIDENTCOUNT = "activeInstancesWithIncidentCount"
    ACTIVEINSTANCESWITHOUTINCIDENTCOUNT = "activeInstancesWithoutIncidentCount"
    PROCESSDEFINITIONID = "processDefinitionId"
    PROCESSDEFINITIONKEY = "processDefinitionKey"
    PROCESSDEFINITIONNAME = "processDefinitionName"
    PROCESSDEFINITIONVERSION = "processDefinitionVersion"

    def __str__(self) -> str:
        return str(self.value)
