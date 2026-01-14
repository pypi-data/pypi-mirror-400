from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_documents_response_201_created_documents_item import (
        CreateDocumentsResponse201CreatedDocumentsItem,
    )
    from ..models.create_documents_response_201_failed_documents_item import (
        CreateDocumentsResponse201FailedDocumentsItem,
    )


T = TypeVar("T", bound="CreateDocumentsResponse201")


@_attrs_define
class CreateDocumentsResponse201:
    """
    Attributes:
        failed_documents (list[CreateDocumentsResponse201FailedDocumentsItem] | Unset): Documents that were successfully
            created.
        created_documents (list[CreateDocumentsResponse201CreatedDocumentsItem] | Unset): Documents that failed
            creation.
    """

    failed_documents: list[CreateDocumentsResponse201FailedDocumentsItem] | Unset = (
        UNSET
    )
    created_documents: list[CreateDocumentsResponse201CreatedDocumentsItem] | Unset = (
        UNSET
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        failed_documents: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.failed_documents, Unset):
            failed_documents = []
            for failed_documents_item_data in self.failed_documents:
                failed_documents_item = failed_documents_item_data.to_dict()
                failed_documents.append(failed_documents_item)

        created_documents: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.created_documents, Unset):
            created_documents = []
            for created_documents_item_data in self.created_documents:
                created_documents_item = created_documents_item_data.to_dict()
                created_documents.append(created_documents_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if failed_documents is not UNSET:
            field_dict["failedDocuments"] = failed_documents
        if created_documents is not UNSET:
            field_dict["createdDocuments"] = created_documents

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_documents_response_201_created_documents_item import (
            CreateDocumentsResponse201CreatedDocumentsItem,
        )
        from ..models.create_documents_response_201_failed_documents_item import (
            CreateDocumentsResponse201FailedDocumentsItem,
        )

        d = dict(src_dict)
        _failed_documents = d.pop("failedDocuments", UNSET)
        failed_documents: (
            list[CreateDocumentsResponse201FailedDocumentsItem] | Unset
        ) = UNSET
        if _failed_documents is not UNSET:
            failed_documents = []
            for failed_documents_item_data in _failed_documents:
                failed_documents_item = (
                    CreateDocumentsResponse201FailedDocumentsItem.from_dict(
                        failed_documents_item_data
                    )
                )

                failed_documents.append(failed_documents_item)

        _created_documents = d.pop("createdDocuments", UNSET)
        created_documents: (
            list[CreateDocumentsResponse201CreatedDocumentsItem] | Unset
        ) = UNSET
        if _created_documents is not UNSET:
            created_documents = []
            for created_documents_item_data in _created_documents:
                created_documents_item = (
                    CreateDocumentsResponse201CreatedDocumentsItem.from_dict(
                        created_documents_item_data
                    )
                )

                created_documents.append(created_documents_item)

        create_documents_response_201 = cls(
            failed_documents=failed_documents,
            created_documents=created_documents,
        )

        create_documents_response_201.additional_properties = d
        return create_documents_response_201

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
