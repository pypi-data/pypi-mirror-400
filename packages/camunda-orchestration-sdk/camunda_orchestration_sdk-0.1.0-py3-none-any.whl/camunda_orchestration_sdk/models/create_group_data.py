from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateGroupData")


@_attrs_define
class CreateGroupData:
    """
    Attributes:
        group_id (str): The ID of the new group.
        name (str): The display name of the new group.
        description (str | Unset): The description of the new group.
    """

    group_id: str
    name: str
    description: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        group_id = self.group_id

        name = self.name

        description = self.description

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "groupId": group_id,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        group_id = d.pop("groupId")

        name = d.pop("name")

        description = d.pop("description", UNSET)

        create_group_data = cls(
            group_id=group_id,
            name=name,
            description=description,
        )

        return create_group_data
