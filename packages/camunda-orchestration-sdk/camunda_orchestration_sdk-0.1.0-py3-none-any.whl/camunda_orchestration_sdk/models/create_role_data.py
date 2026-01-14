from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateRoleData")


@_attrs_define
class CreateRoleData:
    """
    Attributes:
        role_id (str): The ID of the new role.
        name (str): The display name of the new role.
        description (str | Unset): The description of the new role.
    """

    role_id: str
    name: str
    description: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        role_id = self.role_id

        name = self.name

        description = self.description

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "roleId": role_id,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role_id = d.pop("roleId")

        name = d.pop("name")

        description = d.pop("description", UNSET)

        create_role_data = cls(
            role_id=role_id,
            name=name,
            description=description,
        )

        return create_role_data
