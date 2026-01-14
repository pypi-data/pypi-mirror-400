from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_process_instance_statistics_by_error_data_offset_based_pagination import (
        GetProcessInstanceStatisticsByErrorDataOffsetBasedPagination,
    )
    from ..models.get_process_instance_statistics_by_error_data_sort_item import (
        GetProcessInstanceStatisticsByErrorDataSortItem,
    )


T = TypeVar("T", bound="GetProcessInstanceStatisticsByErrorData")


@_attrs_define
class GetProcessInstanceStatisticsByErrorData:
    """
    Attributes:
        page (GetProcessInstanceStatisticsByErrorDataOffsetBasedPagination | Unset): Pagination parameters for process
            instance statistics grouped by incident error.
        sort (list[GetProcessInstanceStatisticsByErrorDataSortItem] | Unset): Sorting criteria for process instance
            statistics grouped by incident error.
    """

    page: GetProcessInstanceStatisticsByErrorDataOffsetBasedPagination | Unset = UNSET
    sort: list[GetProcessInstanceStatisticsByErrorDataSortItem] | Unset = UNSET

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

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if page is not UNSET:
            field_dict["page"] = page
        if sort is not UNSET:
            field_dict["sort"] = sort

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_process_instance_statistics_by_error_data_offset_based_pagination import (
            GetProcessInstanceStatisticsByErrorDataOffsetBasedPagination,
        )
        from ..models.get_process_instance_statistics_by_error_data_sort_item import (
            GetProcessInstanceStatisticsByErrorDataSortItem,
        )

        d = dict(src_dict)
        _page = d.pop("page", UNSET)
        page: GetProcessInstanceStatisticsByErrorDataOffsetBasedPagination | Unset
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = (
                GetProcessInstanceStatisticsByErrorDataOffsetBasedPagination.from_dict(
                    _page
                )
            )

        _sort = d.pop("sort", UNSET)
        sort: list[GetProcessInstanceStatisticsByErrorDataSortItem] | Unset = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = GetProcessInstanceStatisticsByErrorDataSortItem.from_dict(
                    sort_item_data
                )

                sort.append(sort_item)

        get_process_instance_statistics_by_error_data = cls(
            page=page,
            sort=sort,
        )

        return get_process_instance_statistics_by_error_data
