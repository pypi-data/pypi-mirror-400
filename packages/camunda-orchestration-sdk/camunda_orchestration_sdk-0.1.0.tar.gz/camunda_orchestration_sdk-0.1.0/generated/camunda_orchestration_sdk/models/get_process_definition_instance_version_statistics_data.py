from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_process_definition_instance_version_statistics_data_filter import (
        GetProcessDefinitionInstanceVersionStatisticsDataFilter,
    )
    from ..models.get_process_definition_instance_version_statistics_data_offset_based_pagination import (
        GetProcessDefinitionInstanceVersionStatisticsDataOffsetBasedPagination,
    )
    from ..models.get_process_definition_instance_version_statistics_data_sort_item import (
        GetProcessDefinitionInstanceVersionStatisticsDataSortItem,
    )


T = TypeVar("T", bound="GetProcessDefinitionInstanceVersionStatisticsData")


@_attrs_define
class GetProcessDefinitionInstanceVersionStatisticsData:
    """
    Attributes:
        page (GetProcessDefinitionInstanceVersionStatisticsDataOffsetBasedPagination | Unset): Pagination criteria.
        sort (list[GetProcessDefinitionInstanceVersionStatisticsDataSortItem] | Unset): Sort field criteria.
        filter_ (GetProcessDefinitionInstanceVersionStatisticsDataFilter | Unset): The process definition instance
            version statistics search filters.
    """

    page: (
        GetProcessDefinitionInstanceVersionStatisticsDataOffsetBasedPagination | Unset
    ) = UNSET
    sort: list[GetProcessDefinitionInstanceVersionStatisticsDataSortItem] | Unset = (
        UNSET
    )
    filter_: GetProcessDefinitionInstanceVersionStatisticsDataFilter | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page: dict[str, Any] | Unset = UNSET
        if not isinstance(self.page, Unset):
            page = self.page.to_dict()

        sort: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.sort, Unset):
            sort = []
            for sort_item_data in self.sort:
                sort_item = sort_item_data.to_dict()
                sort.append(sort_item)

        filter_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filter_, Unset):
            filter_ = self.filter_.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if page is not UNSET:
            field_dict["page"] = page
        if sort is not UNSET:
            field_dict["sort"] = sort
        if filter_ is not UNSET:
            field_dict["filter"] = filter_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_process_definition_instance_version_statistics_data_filter import (
            GetProcessDefinitionInstanceVersionStatisticsDataFilter,
        )
        from ..models.get_process_definition_instance_version_statistics_data_offset_based_pagination import (
            GetProcessDefinitionInstanceVersionStatisticsDataOffsetBasedPagination,
        )
        from ..models.get_process_definition_instance_version_statistics_data_sort_item import (
            GetProcessDefinitionInstanceVersionStatisticsDataSortItem,
        )

        d = dict(src_dict)
        _page = d.pop("page", UNSET)
        page: (
            GetProcessDefinitionInstanceVersionStatisticsDataOffsetBasedPagination
            | Unset
        )
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = GetProcessDefinitionInstanceVersionStatisticsDataOffsetBasedPagination.from_dict(
                _page
            )

        _sort = d.pop("sort", UNSET)
        sort: (
            list[GetProcessDefinitionInstanceVersionStatisticsDataSortItem] | Unset
        ) = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = (
                    GetProcessDefinitionInstanceVersionStatisticsDataSortItem.from_dict(
                        sort_item_data
                    )
                )

                sort.append(sort_item)

        _filter_ = d.pop("filter", UNSET)
        filter_: GetProcessDefinitionInstanceVersionStatisticsDataFilter | Unset
        if isinstance(_filter_, Unset):
            filter_ = UNSET
        else:
            filter_ = GetProcessDefinitionInstanceVersionStatisticsDataFilter.from_dict(
                _filter_
            )

        get_process_definition_instance_version_statistics_data = cls(
            page=page,
            sort=sort,
            filter_=filter_,
        )

        get_process_definition_instance_version_statistics_data.additional_properties = d
        return get_process_definition_instance_version_statistics_data

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
