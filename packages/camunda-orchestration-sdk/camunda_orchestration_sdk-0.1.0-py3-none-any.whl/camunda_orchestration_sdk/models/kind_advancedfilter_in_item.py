from enum import Enum


class KindAdvancedfilterInItem(str, Enum):
    AD_HOC_SUB_PROCESS = "AD_HOC_SUB_PROCESS"
    BPMN_ELEMENT = "BPMN_ELEMENT"
    EXECUTION_LISTENER = "EXECUTION_LISTENER"
    TASK_LISTENER = "TASK_LISTENER"

    def __str__(self) -> str:
        return str(self.value)
