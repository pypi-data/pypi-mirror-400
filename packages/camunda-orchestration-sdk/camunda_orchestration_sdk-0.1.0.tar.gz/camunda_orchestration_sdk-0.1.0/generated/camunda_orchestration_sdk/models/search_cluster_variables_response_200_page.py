from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchClusterVariablesResponse200Page")


@_attrs_define
class SearchClusterVariablesResponse200Page:
    """Pagination information about the search results.

    Example:
        {'totalItems': 1, 'hasMoreTotalItems': False}

    Attributes:
        total_items (int): Total items matching the criteria.
        has_more_total_items (bool | Unset): Indicates whether there are more items matching the criteria beyond the
            returned items.
            This is useful for determining if additional requests are needed to retrieve all results.
        start_cursor (str | Unset): The cursor value for getting the previous page of results. Use this in the `before`
            field of an ensuing request. Example: WzIyNTE3OTk4MTM2ODcxMDJd.
        end_cursor (str | Unset): The cursor value for getting the next page of results. Use this in the `after` field
            of an ensuing request. Example: WzIyNTE3OTk4MTM2ODcxMDJd.
    """

    total_items: int
    has_more_total_items: bool | Unset = UNSET
    start_cursor: StartCursor | Unset = UNSET
    end_cursor: EndCursor | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_items = self.total_items

        has_more_total_items = self.has_more_total_items

        start_cursor = self.start_cursor

        end_cursor = self.end_cursor

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "totalItems": total_items,
            }
        )
        if has_more_total_items is not UNSET:
            field_dict["hasMoreTotalItems"] = has_more_total_items
        if start_cursor is not UNSET:
            field_dict["startCursor"] = start_cursor
        if end_cursor is not UNSET:
            field_dict["endCursor"] = end_cursor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total_items = d.pop("totalItems")

        has_more_total_items = d.pop("hasMoreTotalItems", UNSET)

        start_cursor = lift_start_cursor(_val) if (_val := d.pop("startCursor", UNSET)) is not UNSET else UNSET

        end_cursor = lift_end_cursor(_val) if (_val := d.pop("endCursor", UNSET)) is not UNSET else UNSET

        search_cluster_variables_response_200_page = cls(
            total_items=total_items,
            has_more_total_items=has_more_total_items,
            start_cursor=start_cursor,
            end_cursor=end_cursor,
        )

        search_cluster_variables_response_200_page.additional_properties = d
        return search_cluster_variables_response_200_page

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
