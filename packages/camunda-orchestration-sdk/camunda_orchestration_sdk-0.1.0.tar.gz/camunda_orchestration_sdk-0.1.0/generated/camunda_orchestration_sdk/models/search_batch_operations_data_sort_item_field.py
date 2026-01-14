from enum import Enum


class SearchBatchOperationsDataSortItemField(str, Enum):
    ACTORID = "actorId"
    ACTORTYPE = "actorType"
    BATCHOPERATIONKEY = "batchOperationKey"
    ENDDATE = "endDate"
    OPERATIONTYPE = "operationType"
    STARTDATE = "startDate"
    STATE = "state"

    def __str__(self) -> str:
        return str(self.value)
