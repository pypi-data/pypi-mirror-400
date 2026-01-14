from enum import Enum


class CreateDocumentResponse201CamundaDocumentType(str, Enum):
    CAMUNDA = "camunda"

    def __str__(self) -> str:
        return str(self.value)
