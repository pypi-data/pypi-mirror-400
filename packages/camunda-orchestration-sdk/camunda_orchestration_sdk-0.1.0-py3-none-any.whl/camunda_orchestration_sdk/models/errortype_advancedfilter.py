from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.errortype_advancedfilter_in_item import ErrortypeAdvancedfilterInItem
from ..models.errortype_advancedfilter_not_in_item import (
    ErrortypeAdvancedfilterNotInItem,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.errortype_advancedfilter_eq import ErrortypeAdvancedfilterEq
    from ..models.errortype_advancedfilter_neq import ErrortypeAdvancedfilterNeq


T = TypeVar("T", bound="ErrortypeAdvancedfilter")


@_attrs_define
class ErrortypeAdvancedfilter:
    r"""Advanced IncidentErrorTypeEnum filter

    Attributes:
        eq (ErrortypeAdvancedfilterEq | Unset): Checks for equality with the provided value.
        neq (ErrortypeAdvancedfilterNeq | Unset): Checks for inequality with the provided value.
        exists (bool | Unset): Checks if the current property exists.
        in_ (list[ErrortypeAdvancedfilterInItem] | Unset): Checks if the property matches any of the provided values.
        not_in (list[ErrortypeAdvancedfilterNotInItem] | Unset): Checks if the property does not match any of the
            provided values.
        like (str | Unset): Checks if the property matches the provided like value.

            Supported wildcard characters are:

            * `*`: matches zero, one, or multiple characters.
            * `?`: matches one, single character.

            Wildcard characters can be escaped with backslash, for instance: `\*`.
    """

    eq: ErrortypeAdvancedfilterEq | Unset = UNSET
    neq: ErrortypeAdvancedfilterNeq | Unset = UNSET
    exists: bool | Unset = UNSET
    in_: list[ErrortypeAdvancedfilterInItem] | Unset = UNSET
    not_in: list[ErrortypeAdvancedfilterNotInItem] | Unset = UNSET
    like: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        eq: dict[str, Any] | Unset = UNSET
        if not isinstance(self.eq, Unset):
            eq = self.eq.to_dict()

        neq: dict[str, Any] | Unset = UNSET
        if not isinstance(self.neq, Unset):
            neq = self.neq.to_dict()

        exists = self.exists

        in_: list[str] | Unset = UNSET
        if not isinstance(self.in_, Unset):
            in_ = []
            for in_item_data in self.in_:
                in_item = in_item_data.value
                in_.append(in_item)

        not_in: list[str] | Unset = UNSET
        if not isinstance(self.not_in, Unset):
            not_in = []
            for not_in_item_data in self.not_in:
                not_in_item = not_in_item_data.value
                not_in.append(not_in_item)

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
        if not_in is not UNSET:
            field_dict["$notIn"] = not_in
        if like is not UNSET:
            field_dict["$like"] = like

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.errortype_advancedfilter_eq import ErrortypeAdvancedfilterEq
        from ..models.errortype_advancedfilter_neq import ErrortypeAdvancedfilterNeq

        d = dict(src_dict)
        _eq = d.pop("$eq", UNSET)
        eq: ErrortypeAdvancedfilterEq | Unset
        if isinstance(_eq, Unset):
            eq = UNSET
        else:
            eq = ErrortypeAdvancedfilterEq.from_dict(_eq)

        _neq = d.pop("$neq", UNSET)
        neq: ErrortypeAdvancedfilterNeq | Unset
        if isinstance(_neq, Unset):
            neq = UNSET
        else:
            neq = ErrortypeAdvancedfilterNeq.from_dict(_neq)

        exists = d.pop("$exists", UNSET)

        _in_ = d.pop("$in", UNSET)
        in_: list[ErrortypeAdvancedfilterInItem] | Unset = UNSET
        if _in_ is not UNSET:
            in_ = []
            for in_item_data in _in_:
                in_item = ErrortypeAdvancedfilterInItem(in_item_data)

                in_.append(in_item)

        _not_in = d.pop("$notIn", UNSET)
        not_in: list[ErrortypeAdvancedfilterNotInItem] | Unset = UNSET
        if _not_in is not UNSET:
            not_in = []
            for not_in_item_data in _not_in:
                not_in_item = ErrortypeAdvancedfilterNotInItem(not_in_item_data)

                not_in.append(not_in_item)

        like = d.pop("$like", UNSET)

        errortype_advancedfilter = cls(
            eq=eq,
            neq=neq,
            exists=exists,
            in_=in_,
            not_in=not_in,
            like=like,
        )

        errortype_advancedfilter.additional_properties = d
        return errortype_advancedfilter

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
