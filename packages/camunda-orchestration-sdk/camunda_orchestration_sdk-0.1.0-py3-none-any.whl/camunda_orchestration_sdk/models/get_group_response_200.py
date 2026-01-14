from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetGroupResponse200")


@_attrs_define
class GetGroupResponse200:
    """Group search response item.

    Attributes:
        name (str | Unset): The group name.
        group_id (str | Unset): The group ID.
        description (str | Unset): The group description.
    """

    name: str | Unset = UNSET
    group_id: str | Unset = UNSET
    description: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        group_id = self.group_id

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if group_id is not UNSET:
            field_dict["groupId"] = group_id
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        group_id = d.pop("groupId", UNSET)

        description = d.pop("description", UNSET)

        get_group_response_200 = cls(
            name=name,
            group_id=group_id,
            description=description,
        )

        get_group_response_200.additional_properties = d
        return get_group_response_200

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
