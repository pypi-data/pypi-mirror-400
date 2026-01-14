from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateRoleResponse200")


@_attrs_define
class UpdateRoleResponse200:
    """
    Attributes:
        name (str | Unset): The display name of the updated role.
        description (str | Unset): The description of the updated role.
        role_id (str | Unset): The ID of the updated role.
    """

    name: str | Unset = UNSET
    description: str | Unset = UNSET
    role_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        role_id = self.role_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if role_id is not UNSET:
            field_dict["roleId"] = role_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        role_id = d.pop("roleId", UNSET)

        update_role_response_200 = cls(
            name=name,
            description=description,
            role_id=role_id,
        )

        update_role_response_200.additional_properties = d
        return update_role_response_200

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
