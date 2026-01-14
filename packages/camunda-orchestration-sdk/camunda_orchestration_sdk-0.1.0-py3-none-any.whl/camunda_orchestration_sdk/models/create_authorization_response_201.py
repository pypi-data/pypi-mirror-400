from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateAuthorizationResponse201")


@_attrs_define
class CreateAuthorizationResponse201:
    """
    Attributes:
        authorization_key (str | Unset): The key of the created authorization. Example: 2251799813684332.
    """

    authorization_key: AuthorizationKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authorization_key = self.authorization_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if authorization_key is not UNSET:
            field_dict["authorizationKey"] = authorization_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        authorization_key = lift_authorization_key(_val) if (_val := d.pop("authorizationKey", UNSET)) is not UNSET else UNSET

        create_authorization_response_201 = cls(
            authorization_key=authorization_key,
        )

        create_authorization_response_201.additional_properties = d
        return create_authorization_response_201

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
