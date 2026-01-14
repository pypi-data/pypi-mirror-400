from enum import Enum


class GetTenantClusterVariableResponse200Scope(str, Enum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"

    def __str__(self) -> str:
        return str(self.value)
