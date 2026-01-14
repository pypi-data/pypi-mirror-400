from enum import Enum


class SearchBatchOperationsResponse200ItemsItemActorType(str, Enum):
    CLIENT = "CLIENT"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
