from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_process_instance_statistics_by_definition_data_filter import (
        GetProcessInstanceStatisticsByDefinitionDataFilter,
    )
    from ..models.get_process_instance_statistics_by_definition_data_offset_based_pagination import (
        GetProcessInstanceStatisticsByDefinitionDataOffsetBasedPagination,
    )
    from ..models.get_process_instance_statistics_by_definition_data_sort_item import (
        GetProcessInstanceStatisticsByDefinitionDataSortItem,
    )


T = TypeVar("T", bound="GetProcessInstanceStatisticsByDefinitionData")


@_attrs_define
class GetProcessInstanceStatisticsByDefinitionData:
    """
    Attributes:
        filter_ (GetProcessInstanceStatisticsByDefinitionDataFilter): Filter criteria for the aggregated process
            instance statistics.
        page (GetProcessInstanceStatisticsByDefinitionDataOffsetBasedPagination | Unset): Pagination parameters for the
            aggregated process instance statistics.
        sort (list[GetProcessInstanceStatisticsByDefinitionDataSortItem] | Unset): Sorting criteria for process instance
            statistics grouped by process definition.
    """

    filter_: GetProcessInstanceStatisticsByDefinitionDataFilter
    page: GetProcessInstanceStatisticsByDefinitionDataOffsetBasedPagination | Unset = (
        UNSET
    )
    sort: list[GetProcessInstanceStatisticsByDefinitionDataSortItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        filter_ = self.filter_.to_dict()

        page: dict[str, Any] | Unset = UNSET
        if not isinstance(self.page, Unset):
            page = self.page.to_dict()

        sort: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.sort, Unset):
            sort = []
            for sort_item_data in self.sort:
                sort_item = sort_item_data.to_dict()
                sort.append(sort_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "filter": filter_,
            }
        )
        if page is not UNSET:
            field_dict["page"] = page
        if sort is not UNSET:
            field_dict["sort"] = sort

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_process_instance_statistics_by_definition_data_filter import (
            GetProcessInstanceStatisticsByDefinitionDataFilter,
        )
        from ..models.get_process_instance_statistics_by_definition_data_offset_based_pagination import (
            GetProcessInstanceStatisticsByDefinitionDataOffsetBasedPagination,
        )
        from ..models.get_process_instance_statistics_by_definition_data_sort_item import (
            GetProcessInstanceStatisticsByDefinitionDataSortItem,
        )

        d = dict(src_dict)
        filter_ = GetProcessInstanceStatisticsByDefinitionDataFilter.from_dict(
            d.pop("filter")
        )

        _page = d.pop("page", UNSET)
        page: GetProcessInstanceStatisticsByDefinitionDataOffsetBasedPagination | Unset
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = GetProcessInstanceStatisticsByDefinitionDataOffsetBasedPagination.from_dict(
                _page
            )

        _sort = d.pop("sort", UNSET)
        sort: list[GetProcessInstanceStatisticsByDefinitionDataSortItem] | Unset = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = (
                    GetProcessInstanceStatisticsByDefinitionDataSortItem.from_dict(
                        sort_item_data
                    )
                )

                sort.append(sort_item)

        get_process_instance_statistics_by_definition_data = cls(
            filter_=filter_,
            page=page,
            sort=sort,
        )

        get_process_instance_statistics_by_definition_data.additional_properties = d
        return get_process_instance_statistics_by_definition_data

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
