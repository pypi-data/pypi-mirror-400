from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PartitionidAdvancedfilter")


@_attrs_define
class PartitionidAdvancedfilter:
    """Advanced integer (int32) filter.

    Attributes:
        eq (int | Unset): Checks for equality with the provided value.
        neq (int | Unset): Checks for inequality with the provided value.
        exists (bool | Unset): Checks if the current property exists.
        gt (int | Unset): Greater than comparison with the provided value.
        gte (int | Unset): Greater than or equal comparison with the provided value.
        lt (int | Unset): Lower than comparison with the provided value.
        lte (int | Unset): Lower than or equal comparison with the provided value.
        in_ (list[int] | Unset): Checks if the property matches any of the provided values.
    """

    eq: int | Unset = UNSET
    neq: int | Unset = UNSET
    exists: bool | Unset = UNSET
    gt: int | Unset = UNSET
    gte: int | Unset = UNSET
    lt: int | Unset = UNSET
    lte: int | Unset = UNSET
    in_: list[int] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        eq = self.eq

        neq = self.neq

        exists = self.exists

        gt = self.gt

        gte = self.gte

        lt = self.lt

        lte = self.lte

        in_: list[int] | Unset = UNSET
        if not isinstance(self.in_, Unset):
            in_ = self.in_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if eq is not UNSET:
            field_dict["$eq"] = eq
        if neq is not UNSET:
            field_dict["$neq"] = neq
        if exists is not UNSET:
            field_dict["$exists"] = exists
        if gt is not UNSET:
            field_dict["$gt"] = gt
        if gte is not UNSET:
            field_dict["$gte"] = gte
        if lt is not UNSET:
            field_dict["$lt"] = lt
        if lte is not UNSET:
            field_dict["$lte"] = lte
        if in_ is not UNSET:
            field_dict["$in"] = in_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        eq = d.pop("$eq", UNSET)

        neq = d.pop("$neq", UNSET)

        exists = d.pop("$exists", UNSET)

        gt = d.pop("$gt", UNSET)

        gte = d.pop("$gte", UNSET)

        lt = d.pop("$lt", UNSET)

        lte = d.pop("$lte", UNSET)

        in_ = cast(list[int], d.pop("$in", UNSET))

        partitionid_advancedfilter = cls(
            eq=eq,
            neq=neq,
            exists=exists,
            gt=gt,
            gte=gte,
            lt=lt,
            lte=lte,
            in_=in_,
        )

        partitionid_advancedfilter.additional_properties = d
        return partitionid_advancedfilter

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
