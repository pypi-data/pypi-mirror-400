from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.state_advancedfilter_7_eq import StateAdvancedfilter7Eq
from ..models.state_advancedfilter_7_in_item import StateAdvancedfilter7InItem
from ..models.state_advancedfilter_7_neq import StateAdvancedfilter7Neq
from ..types import UNSET, Unset

T = TypeVar("T", bound="StateAdvancedfilter7")


@_attrs_define
class StateAdvancedfilter7:
    r"""Advanced UserTaskStateEnum filter.

    Attributes:
        eq (StateAdvancedfilter7Eq | Unset): Checks for equality with the provided value.
        neq (StateAdvancedfilter7Neq | Unset): Checks for inequality with the provided value.
        exists (bool | Unset): Checks if the current property exists.
        in_ (list[StateAdvancedfilter7InItem] | Unset): Checks if the property matches any of the provided values.
        like (str | Unset): Checks if the property matches the provided like value.

            Supported wildcard characters are:

            * `*`: matches zero, one, or multiple characters.
            * `?`: matches one, single character.

            Wildcard characters can be escaped with backslash, for instance: `\*`.
    """

    eq: StateAdvancedfilter7Eq | Unset = UNSET
    neq: StateAdvancedfilter7Neq | Unset = UNSET
    exists: bool | Unset = UNSET
    in_: list[StateAdvancedfilter7InItem] | Unset = UNSET
    like: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        eq: str | Unset = UNSET
        if not isinstance(self.eq, Unset):
            eq = self.eq.value

        neq: str | Unset = UNSET
        if not isinstance(self.neq, Unset):
            neq = self.neq.value

        exists = self.exists

        in_: list[str] | Unset = UNSET
        if not isinstance(self.in_, Unset):
            in_ = []
            for in_item_data in self.in_:
                in_item = in_item_data.value
                in_.append(in_item)

        like = self.like

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
        if like is not UNSET:
            field_dict["$like"] = like

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _eq = d.pop("$eq", UNSET)
        eq: StateAdvancedfilter7Eq | Unset
        if isinstance(_eq, Unset):
            eq = UNSET
        else:
            eq = StateAdvancedfilter7Eq(_eq)

        _neq = d.pop("$neq", UNSET)
        neq: StateAdvancedfilter7Neq | Unset
        if isinstance(_neq, Unset):
            neq = UNSET
        else:
            neq = StateAdvancedfilter7Neq(_neq)

        exists = d.pop("$exists", UNSET)

        _in_ = d.pop("$in", UNSET)
        in_: list[StateAdvancedfilter7InItem] | Unset = UNSET
        if _in_ is not UNSET:
            in_ = []
            for in_item_data in _in_:
                in_item = StateAdvancedfilter7InItem(in_item_data)

                in_.append(in_item)

        like = d.pop("$like", UNSET)

        state_advancedfilter_7 = cls(
            eq=eq,
            neq=neq,
            exists=exists,
            in_=in_,
            like=like,
        )

        state_advancedfilter_7.additional_properties = d
        return state_advancedfilter_7

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
