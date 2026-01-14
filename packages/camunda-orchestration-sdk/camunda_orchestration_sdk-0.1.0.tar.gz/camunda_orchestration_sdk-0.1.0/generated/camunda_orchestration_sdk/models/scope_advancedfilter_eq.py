from enum import Enum


class ScopeAdvancedfilterEq(str, Enum):
    GLOBAL = "GLOBAL"
    TENANT = "TENANT"

    def __str__(self) -> str:
        return str(self.value)
