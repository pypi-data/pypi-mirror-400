from enum import Enum


class SearchBatchOperationsDataFilterActorType(str, Enum):
    CLIENT = "CLIENT"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
