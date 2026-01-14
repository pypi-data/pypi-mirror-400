from enum import Enum


class GetGlobalClusterVariableResponse200Scope(str, Enum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"

    def __str__(self) -> str:
        return str(self.value)
