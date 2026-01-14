from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.search_jobs_data_sort_item_field import SearchJobsDataSortItemField
from ..models.search_jobs_data_sort_item_order import SearchJobsDataSortItemOrder
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchJobsDataSortItem")


@_attrs_define
class SearchJobsDataSortItem:
    """
    Attributes:
        field (SearchJobsDataSortItemField): The field to sort by.
        order (SearchJobsDataSortItemOrder | Unset): The order in which to sort the related field. Default:
            SearchJobsDataSortItemOrder.ASC.
    """

    field: SearchJobsDataSortItemField
    order: SearchJobsDataSortItemOrder | Unset = SearchJobsDataSortItemOrder.ASC
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field = self.field.value

        order: str | Unset = UNSET
        if not isinstance(self.order, Unset):
            order = self.order.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
            }
        )
        if order is not UNSET:
            field_dict["order"] = order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field = SearchJobsDataSortItemField(d.pop("field"))

        _order = d.pop("order", UNSET)
        order: SearchJobsDataSortItemOrder | Unset
        if isinstance(_order, Unset):
            order = UNSET
        else:
            order = SearchJobsDataSortItemOrder(_order)

        search_jobs_data_sort_item = cls(
            field=field,
            order=order,
        )

        search_jobs_data_sort_item.additional_properties = d
        return search_jobs_data_sort_item

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
