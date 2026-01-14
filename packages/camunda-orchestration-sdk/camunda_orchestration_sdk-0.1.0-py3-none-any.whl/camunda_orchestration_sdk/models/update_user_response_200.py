from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateUserResponse200")


@_attrs_define
class UpdateUserResponse200:
    """
    Attributes:
        username (str | Unset): The unique name of a user. Example: swillis.
        name (str | Unset): The name of the user.
        email (str | Unset): The email of the user.
    """

    username: Username | Unset = UNSET
    name: str | Unset = UNSET
    email: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        name = self.name

        email = self.email

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if name is not UNSET:
            field_dict["name"] = name
        if email is not UNSET:
            field_dict["email"] = email

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = lift_username(_val) if (_val := d.pop("username", UNSET)) is not UNSET else UNSET

        name = d.pop("name", UNSET)

        email = d.pop("email", UNSET)

        update_user_response_200 = cls(
            username=username,
            name=name,
            email=email,
        )

        update_user_response_200.additional_properties = d
        return update_user_response_200

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
