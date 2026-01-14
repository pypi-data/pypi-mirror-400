from enum import Enum


class SearchBatchOperationItemsDataSortItemField(str, Enum):
    BATCHOPERATIONKEY = "batchOperationKey"
    ITEMKEY = "itemKey"
    PROCESSEDDATE = "processedDate"
    PROCESSINSTANCEKEY = "processInstanceKey"
    STATE = "state"

    def __str__(self) -> str:
        return str(self.value)
