from enum import Enum


class CategoryAdvancedfilterNeq(str, Enum):
    ADMIN = "ADMIN"
    DEPLOYED_RESOURCES = "DEPLOYED_RESOURCES"
    USER_TASKS = "USER_TASKS"

    def __str__(self) -> str:
        return str(self.value)
