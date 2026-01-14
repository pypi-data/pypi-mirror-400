from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="TimestampAdvancedfilter")


@_attrs_define
class TimestampAdvancedfilter:
    """Advanced date-time filter.

    Attributes:
        eq (datetime.datetime | Unset): Checks for equality with the provided value.
        neq (datetime.datetime | Unset): Checks for inequality with the provided value.
        exists (bool | Unset): Checks if the current property exists.
        gt (datetime.datetime | Unset): Greater than comparison with the provided value.
        gte (datetime.datetime | Unset): Greater than or equal comparison with the provided value.
        lt (datetime.datetime | Unset): Lower than comparison with the provided value.
        lte (datetime.datetime | Unset): Lower than or equal comparison with the provided value.
        in_ (list[datetime.datetime] | Unset): Checks if the property matches any of the provided values.
    """

    eq: datetime.datetime | Unset = UNSET
    neq: datetime.datetime | Unset = UNSET
    exists: bool | Unset = UNSET
    gt: datetime.datetime | Unset = UNSET
    gte: datetime.datetime | Unset = UNSET
    lt: datetime.datetime | Unset = UNSET
    lte: datetime.datetime | Unset = UNSET
    in_: list[datetime.datetime] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        eq: str | Unset = UNSET
        if not isinstance(self.eq, Unset):
            eq = self.eq.isoformat()

        neq: str | Unset = UNSET
        if not isinstance(self.neq, Unset):
            neq = self.neq.isoformat()

        exists = self.exists

        gt: str | Unset = UNSET
        if not isinstance(self.gt, Unset):
            gt = self.gt.isoformat()

        gte: str | Unset = UNSET
        if not isinstance(self.gte, Unset):
            gte = self.gte.isoformat()

        lt: str | Unset = UNSET
        if not isinstance(self.lt, Unset):
            lt = self.lt.isoformat()

        lte: str | Unset = UNSET
        if not isinstance(self.lte, Unset):
            lte = self.lte.isoformat()

        in_: list[str] | Unset = UNSET
        if not isinstance(self.in_, Unset):
            in_ = []
            for in_item_data in self.in_:
                in_item = in_item_data.isoformat()
                in_.append(in_item)

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
        _eq = d.pop("$eq", UNSET)
        eq: datetime.datetime | Unset
        if isinstance(_eq, Unset):
            eq = UNSET
        else:
            eq = isoparse(_eq)

        _neq = d.pop("$neq", UNSET)
        neq: datetime.datetime | Unset
        if isinstance(_neq, Unset):
            neq = UNSET
        else:
            neq = isoparse(_neq)

        exists = d.pop("$exists", UNSET)

        _gt = d.pop("$gt", UNSET)
        gt: datetime.datetime | Unset
        if isinstance(_gt, Unset):
            gt = UNSET
        else:
            gt = isoparse(_gt)

        _gte = d.pop("$gte", UNSET)
        gte: datetime.datetime | Unset
        if isinstance(_gte, Unset):
            gte = UNSET
        else:
            gte = isoparse(_gte)

        _lt = d.pop("$lt", UNSET)
        lt: datetime.datetime | Unset
        if isinstance(_lt, Unset):
            lt = UNSET
        else:
            lt = isoparse(_lt)

        _lte = d.pop("$lte", UNSET)
        lte: datetime.datetime | Unset
        if isinstance(_lte, Unset):
            lte = UNSET
        else:
            lte = isoparse(_lte)

        _in_ = d.pop("$in", UNSET)
        in_: list[datetime.datetime] | Unset = UNSET
        if _in_ is not UNSET:
            in_ = []
            for in_item_data in _in_:
                in_item = isoparse(in_item_data)

                in_.append(in_item)

        timestamp_advancedfilter = cls(
            eq=eq,
            neq=neq,
            exists=exists,
            gt=gt,
            gte=gte,
            lt=lt,
            lte=lte,
            in_=in_,
        )

        timestamp_advancedfilter.additional_properties = d
        return timestamp_advancedfilter

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
