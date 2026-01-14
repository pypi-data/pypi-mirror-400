from enum import Enum


class OperationtypeAdvancedfilterEq(str, Enum):
    ASSIGN = "ASSIGN"
    CANCEL = "CANCEL"
    COMPLETE = "COMPLETE"
    CREATE = "CREATE"
    DELETE = "DELETE"
    EVALUATE = "EVALUATE"
    MIGRATE = "MIGRATE"
    MODIFY = "MODIFY"
    RESOLVE = "RESOLVE"
    RESUME = "RESUME"
    SUSPEND = "SUSPEND"
    UNASSIGN = "UNASSIGN"
    UNKNOWN = "UNKNOWN"
    UPDATE = "UPDATE"

    def __str__(self) -> str:
        return str(self.value)
