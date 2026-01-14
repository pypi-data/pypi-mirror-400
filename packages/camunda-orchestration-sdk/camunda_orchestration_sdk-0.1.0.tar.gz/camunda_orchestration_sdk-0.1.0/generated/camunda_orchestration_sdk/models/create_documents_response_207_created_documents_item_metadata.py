from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_documents_response_207_created_documents_item_metadata_custom_properties import (
        CreateDocumentsResponse207CreatedDocumentsItemMetadataCustomProperties,
    )


T = TypeVar("T", bound="CreateDocumentsResponse207CreatedDocumentsItemMetadata")


@_attrs_define
class CreateDocumentsResponse207CreatedDocumentsItemMetadata:
    """Information about the document.

    Attributes:
        content_type (str | Unset): The content type of the document.
        file_name (str | Unset): The name of the file.
        expires_at (datetime.datetime | Unset): The date and time when the document expires.
        size (int | Unset): The size of the document in bytes.
        process_definition_id (str | Unset): The ID of the process definition that created the document. Example: new-
            account-onboarding-workflow.
        process_instance_key (str | Unset): The key of the process instance that created the document. Example:
            2251799813690746.
        custom_properties (CreateDocumentsResponse207CreatedDocumentsItemMetadataCustomProperties | Unset): Custom
            properties of the document.
    """

    content_type: str | Unset = UNSET
    file_name: str | Unset = UNSET
    expires_at: datetime.datetime | Unset = UNSET
    size: int | Unset = UNSET
    process_definition_id: ProcessDefinitionId | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    custom_properties: (
        CreateDocumentsResponse207CreatedDocumentsItemMetadataCustomProperties | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content_type = self.content_type

        file_name = self.file_name

        expires_at: str | Unset = UNSET
        if not isinstance(self.expires_at, Unset):
            expires_at = self.expires_at.isoformat()

        size = self.size

        process_definition_id = self.process_definition_id

        process_instance_key = self.process_instance_key

        custom_properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.custom_properties, Unset):
            custom_properties = self.custom_properties.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content_type is not UNSET:
            field_dict["contentType"] = content_type
        if file_name is not UNSET:
            field_dict["fileName"] = file_name
        if expires_at is not UNSET:
            field_dict["expiresAt"] = expires_at
        if size is not UNSET:
            field_dict["size"] = size
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if custom_properties is not UNSET:
            field_dict["customProperties"] = custom_properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_documents_response_207_created_documents_item_metadata_custom_properties import (
            CreateDocumentsResponse207CreatedDocumentsItemMetadataCustomProperties,
        )

        d = dict(src_dict)
        content_type = d.pop("contentType", UNSET)

        file_name = d.pop("fileName", UNSET)

        _expires_at = d.pop("expiresAt", UNSET)
        expires_at: datetime.datetime | Unset
        if isinstance(_expires_at, Unset):
            expires_at = UNSET
        else:
            expires_at = isoparse(_expires_at)

        size = d.pop("size", UNSET)

        process_definition_id = lift_process_definition_id(_val) if (_val := d.pop("processDefinitionId", UNSET)) is not UNSET else UNSET

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        _custom_properties = d.pop("customProperties", UNSET)
        custom_properties: (
            CreateDocumentsResponse207CreatedDocumentsItemMetadataCustomProperties
            | Unset
        )
        if isinstance(_custom_properties, Unset):
            custom_properties = UNSET
        else:
            custom_properties = CreateDocumentsResponse207CreatedDocumentsItemMetadataCustomProperties.from_dict(
                _custom_properties
            )

        create_documents_response_207_created_documents_item_metadata = cls(
            content_type=content_type,
            file_name=file_name,
            expires_at=expires_at,
            size=size,
            process_definition_id=process_definition_id,
            process_instance_key=process_instance_key,
            custom_properties=custom_properties,
        )

        create_documents_response_207_created_documents_item_metadata.additional_properties = d
        return create_documents_response_207_created_documents_item_metadata

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
