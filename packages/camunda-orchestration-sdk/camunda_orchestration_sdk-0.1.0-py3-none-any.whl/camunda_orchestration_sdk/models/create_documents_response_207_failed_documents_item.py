from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateDocumentsResponse207FailedDocumentsItem")


@_attrs_define
class CreateDocumentsResponse207FailedDocumentsItem:
    """
    Attributes:
        file_name (str | Unset): The name of the file that failed to upload.
        status (int | Unset): The HTTP status code of the failure.
        title (str | Unset): A short, human-readable summary of the problem type.
        detail (str | Unset): A human-readable explanation specific to this occurrence of the problem.
    """

    file_name: str | Unset = UNSET
    status: int | Unset = UNSET
    title: str | Unset = UNSET
    detail: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_name = self.file_name

        status = self.status

        title = self.title

        detail = self.detail

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file_name is not UNSET:
            field_dict["fileName"] = file_name
        if status is not UNSET:
            field_dict["status"] = status
        if title is not UNSET:
            field_dict["title"] = title
        if detail is not UNSET:
            field_dict["detail"] = detail

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file_name = d.pop("fileName", UNSET)

        status = d.pop("status", UNSET)

        title = d.pop("title", UNSET)

        detail = d.pop("detail", UNSET)

        create_documents_response_207_failed_documents_item = cls(
            file_name=file_name,
            status=status,
            title=title,
            detail=detail,
        )

        create_documents_response_207_failed_documents_item.additional_properties = d
        return create_documents_response_207_failed_documents_item

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
