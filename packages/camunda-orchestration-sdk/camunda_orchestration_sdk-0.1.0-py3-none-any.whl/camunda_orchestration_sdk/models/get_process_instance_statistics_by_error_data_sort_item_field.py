from enum import Enum


class GetProcessInstanceStatisticsByErrorDataSortItemField(str, Enum):
    ACTIVEINSTANCESWITHERRORCOUNT = "activeInstancesWithErrorCount"
    ERRORMESSAGE = "errorMessage"

    def __str__(self) -> str:
        return str(self.value)
