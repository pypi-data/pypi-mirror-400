from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PageCursorBasedbackwardpagination")


@_attrs_define
class PageCursorBasedbackwardpagination:
    """
    Attributes:
        before (str): Use the `startCursor` value from the previous response to fetch the previous page of results.
            Example: WzIyNTE3OTk4MTM2ODcxMDJd.
        limit (int | Unset): The maximum number of items to return in one request. Default: 100.
    """

    before: StartCursor
    limit: int | Unset = 100
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        before = self.before

        limit = self.limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "before": before,
            }
        )
        if limit is not UNSET:
            field_dict["limit"] = limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        before = lift_start_cursor(d.pop("before"))

        limit = d.pop("limit", UNSET)

        page_cursor_basedbackwardpagination = cls(
            before=before,
            limit=limit,
        )

        page_cursor_basedbackwardpagination.additional_properties = d
        return page_cursor_basedbackwardpagination

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
