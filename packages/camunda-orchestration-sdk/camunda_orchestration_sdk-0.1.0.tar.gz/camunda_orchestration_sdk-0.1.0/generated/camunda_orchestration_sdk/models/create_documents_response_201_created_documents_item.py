from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.create_documents_response_201_created_documents_item_camunda_document_type import (
    CreateDocumentsResponse201CreatedDocumentsItemCamundaDocumentType,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_documents_response_201_created_documents_item_metadata import (
        CreateDocumentsResponse201CreatedDocumentsItemMetadata,
    )


T = TypeVar("T", bound="CreateDocumentsResponse201CreatedDocumentsItem")


@_attrs_define
class CreateDocumentsResponse201CreatedDocumentsItem:
    """
    Attributes:
        camunda_document_type (CreateDocumentsResponse201CreatedDocumentsItemCamundaDocumentType | Unset): Document
            discriminator. Always set to "camunda".
        store_id (str | Unset): The ID of the document store.
        document_id (str | Unset): The ID of the document.
        content_hash (str | Unset): The hash of the document.
        metadata (CreateDocumentsResponse201CreatedDocumentsItemMetadata | Unset): Information about the document.
    """

    camunda_document_type: (
        CreateDocumentsResponse201CreatedDocumentsItemCamundaDocumentType | Unset
    ) = UNSET
    store_id: str | Unset = UNSET
    document_id: DocumentId | Unset = UNSET
    content_hash: str | Unset = UNSET
    metadata: CreateDocumentsResponse201CreatedDocumentsItemMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        camunda_document_type: str | Unset = UNSET
        if not isinstance(self.camunda_document_type, Unset):
            camunda_document_type = self.camunda_document_type.value

        store_id = self.store_id

        document_id = self.document_id

        content_hash = self.content_hash

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if camunda_document_type is not UNSET:
            field_dict["camunda.document.type"] = camunda_document_type
        if store_id is not UNSET:
            field_dict["storeId"] = store_id
        if document_id is not UNSET:
            field_dict["documentId"] = document_id
        if content_hash is not UNSET:
            field_dict["contentHash"] = content_hash
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_documents_response_201_created_documents_item_metadata import (
            CreateDocumentsResponse201CreatedDocumentsItemMetadata,
        )

        d = dict(src_dict)
        _camunda_document_type = d.pop("camunda.document.type", UNSET)
        camunda_document_type: (
            CreateDocumentsResponse201CreatedDocumentsItemCamundaDocumentType | Unset
        )
        if isinstance(_camunda_document_type, Unset):
            camunda_document_type = UNSET
        else:
            camunda_document_type = (
                CreateDocumentsResponse201CreatedDocumentsItemCamundaDocumentType(
                    _camunda_document_type
                )
            )

        store_id = d.pop("storeId", UNSET)

        document_id = lift_document_id(_val) if (_val := d.pop("documentId", UNSET)) is not UNSET else UNSET

        content_hash = d.pop("contentHash", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: CreateDocumentsResponse201CreatedDocumentsItemMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CreateDocumentsResponse201CreatedDocumentsItemMetadata.from_dict(
                _metadata
            )

        create_documents_response_201_created_documents_item = cls(
            camunda_document_type=camunda_document_type,
            store_id=store_id,
            document_id=document_id,
            content_hash=content_hash,
            metadata=metadata,
        )

        create_documents_response_201_created_documents_item.additional_properties = d
        return create_documents_response_201_created_documents_item

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
