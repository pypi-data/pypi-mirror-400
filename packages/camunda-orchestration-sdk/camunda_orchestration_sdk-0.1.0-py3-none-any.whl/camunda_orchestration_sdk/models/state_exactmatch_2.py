from enum import Enum


class StateExactmatch2(str, Enum):
    EVALUATED = "EVALUATED"
    FAILED = "FAILED"
    UNSPECIFIED = "UNSPECIFIED"

    def __str__(self) -> str:
        return str(self.value)
