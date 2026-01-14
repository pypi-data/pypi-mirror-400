from enum import Enum


class SearchDecisionInstancesDataFilterDecisionDefinitionType(str, Enum):
    DECISION_TABLE = "DECISION_TABLE"
    LITERAL_EXPRESSION = "LITERAL_EXPRESSION"
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return str(self.value)
