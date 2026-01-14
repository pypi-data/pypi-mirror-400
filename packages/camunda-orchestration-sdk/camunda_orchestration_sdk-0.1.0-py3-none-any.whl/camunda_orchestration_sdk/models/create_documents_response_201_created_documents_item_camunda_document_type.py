from enum import Enum


class CreateDocumentsResponse201CreatedDocumentsItemCamundaDocumentType(str, Enum):
    CAMUNDA = "camunda"

    def __str__(self) -> str:
        return str(self.value)
