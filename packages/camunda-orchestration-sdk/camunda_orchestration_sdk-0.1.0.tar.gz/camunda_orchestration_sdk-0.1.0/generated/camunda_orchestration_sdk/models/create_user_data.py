from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateUserData")


@_attrs_define
class CreateUserData:
    """
    Attributes:
        password (str): The password of the user.
        username (str): The username of the user.
        name (str | Unset): The name of the user.
        email (str | Unset): The email of the user.
    """

    password: str
    username: Username
    name: str | Unset = UNSET
    email: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        password = self.password

        username = self.username

        name = self.name

        email = self.email

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "password": password,
                "username": username,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if email is not UNSET:
            field_dict["email"] = email

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        password = d.pop("password")

        username = lift_username(d.pop("username"))

        name = d.pop("name", UNSET)

        email = d.pop("email", UNSET)

        create_user_data = cls(
            password=password,
            username=username,
            name=name,
            email=email,
        )

        return create_user_data
