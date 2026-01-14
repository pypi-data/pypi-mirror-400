from enum import Enum


class SearchUserTasksDataSortItemField(str, Enum):
    COMPLETIONDATE = "completionDate"
    CREATIONDATE = "creationDate"
    DUEDATE = "dueDate"
    FOLLOWUPDATE = "followUpDate"
    NAME = "name"
    PRIORITY = "priority"

    def __str__(self) -> str:
        return str(self.value)
