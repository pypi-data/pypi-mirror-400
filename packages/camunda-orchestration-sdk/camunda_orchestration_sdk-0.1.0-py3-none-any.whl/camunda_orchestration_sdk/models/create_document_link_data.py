from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateDocumentLinkData")


@_attrs_define
class CreateDocumentLinkData:
    """
    Attributes:
        time_to_live (int | Unset): The time-to-live of the document link in ms. Default: 3600000.
    """

    time_to_live: int | Unset = 3600000
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        time_to_live = self.time_to_live

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if time_to_live is not UNSET:
            field_dict["timeToLive"] = time_to_live

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        time_to_live = d.pop("timeToLive", UNSET)

        create_document_link_data = cls(
            time_to_live=time_to_live,
        )

        create_document_link_data.additional_properties = d
        return create_document_link_data

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
