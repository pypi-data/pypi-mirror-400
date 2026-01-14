from enum import Enum


class SearchClientsForGroupDataSortItemField(str, Enum):
    CLIENTID = "clientId"

    def __str__(self) -> str:
        return str(self.value)
