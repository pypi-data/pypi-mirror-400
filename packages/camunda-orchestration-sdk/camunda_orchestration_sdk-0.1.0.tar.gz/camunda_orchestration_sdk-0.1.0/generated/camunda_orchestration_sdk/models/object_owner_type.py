from enum import Enum


class ObjectOwnerType(str, Enum):
    CLIENT = "CLIENT"
    GROUP = "GROUP"
    MAPPING_RULE = "MAPPING_RULE"
    ROLE = "ROLE"
    UNSPECIFIED = "UNSPECIFIED"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
