from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProcessinstancekeyAdvancedfilter")


@_attrs_define
class ProcessinstancekeyAdvancedfilter:
    """Advanced ProcessInstanceKey filter.

    Attributes:
        eq (str | Unset): Checks for equality with the provided value. Example: 2251799813690746.
        neq (str | Unset): Checks for inequality with the provided value. Example: 2251799813690746.
        exists (bool | Unset): Checks if the current property exists.
        in_ (list[str] | Unset): Checks if the property matches any of the provided values.
        not_in (list[str] | Unset): Checks if the property matches none of the provided values.
    """

    eq: str | Unset = UNSET
    neq: str | Unset = UNSET
    exists: bool | Unset = UNSET
    in_: list[str] | Unset = UNSET
    not_in: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        eq = self.eq

        neq = self.neq

        exists = self.exists

        in_: list[str] | Unset = UNSET
        if not isinstance(self.in_, Unset):
            in_ = self.in_

        not_in: list[str] | Unset = UNSET
        if not isinstance(self.not_in, Unset):
            not_in = self.not_in

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if eq is not UNSET:
            field_dict["$eq"] = eq
        if neq is not UNSET:
            field_dict["$neq"] = neq
        if exists is not UNSET:
            field_dict["$exists"] = exists
        if in_ is not UNSET:
            field_dict["$in"] = in_
        if not_in is not UNSET:
            field_dict["$notIn"] = not_in

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        eq = d.pop("$eq", UNSET)

        neq = d.pop("$neq", UNSET)

        exists = d.pop("$exists", UNSET)

        in_ = cast(list[str], d.pop("$in", UNSET))

        not_in = cast(list[str], d.pop("$notIn", UNSET))

        processinstancekey_advancedfilter = cls(
            eq=eq,
            neq=neq,
            exists=exists,
            in_=in_,
            not_in=not_in,
        )

        processinstancekey_advancedfilter.additional_properties = d
        return processinstancekey_advancedfilter

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
