from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchRolesResponse200ItemsItem")


@_attrs_define
class SearchRolesResponse200ItemsItem:
    """Role search response item.

    Attributes:
        name (str | Unset): The role name.
        role_id (str | Unset): The role id.
        description (str | Unset): The description of the role.
    """

    name: str | Unset = UNSET
    role_id: str | Unset = UNSET
    description: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        role_id = self.role_id

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if role_id is not UNSET:
            field_dict["roleId"] = role_id
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        role_id = d.pop("roleId", UNSET)

        description = d.pop("description", UNSET)

        search_roles_response_200_items_item = cls(
            name=name,
            role_id=role_id,
            description=description,
        )

        search_roles_response_200_items_item.additional_properties = d
        return search_roles_response_200_items_item

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
