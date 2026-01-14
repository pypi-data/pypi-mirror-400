from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_element_instances_data_filter import (
        SearchElementInstancesDataFilter,
    )
    from ..models.search_element_instances_data_page import (
        SearchElementInstancesDataPage,
    )
    from ..models.search_element_instances_data_sort_item import (
        SearchElementInstancesDataSortItem,
    )


T = TypeVar("T", bound="SearchElementInstancesData")


@_attrs_define
class SearchElementInstancesData:
    """Element instance search request.

    Attributes:
        sort (list[SearchElementInstancesDataSortItem] | Unset): Sort field criteria.
        filter_ (SearchElementInstancesDataFilter | Unset): The element instance search filters.
        page (SearchElementInstancesDataPage | Unset): Pagination criteria.
    """

    sort: list[SearchElementInstancesDataSortItem] | Unset = UNSET
    filter_: SearchElementInstancesDataFilter | Unset = UNSET
    page: SearchElementInstancesDataPage | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        sort: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.sort, Unset):
            sort = []
            for sort_item_data in self.sort:
                sort_item = sort_item_data.to_dict()
                sort.append(sort_item)

        filter_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filter_, Unset):
            filter_ = self.filter_.to_dict()

        page: dict[str, Any] | Unset = UNSET
        if not isinstance(self.page, Unset):
            page = self.page.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if sort is not UNSET:
            field_dict["sort"] = sort
        if filter_ is not UNSET:
            field_dict["filter"] = filter_
        if page is not UNSET:
            field_dict["page"] = page

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_element_instances_data_filter import (
            SearchElementInstancesDataFilter,
        )
        from ..models.search_element_instances_data_page import (
            SearchElementInstancesDataPage,
        )
        from ..models.search_element_instances_data_sort_item import (
            SearchElementInstancesDataSortItem,
        )

        d = dict(src_dict)
        _sort = d.pop("sort", UNSET)
        sort: list[SearchElementInstancesDataSortItem] | Unset = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = SearchElementInstancesDataSortItem.from_dict(sort_item_data)

                sort.append(sort_item)

        _filter_ = d.pop("filter", UNSET)
        filter_: SearchElementInstancesDataFilter | Unset
        if isinstance(_filter_, Unset):
            filter_ = UNSET
        else:
            filter_ = SearchElementInstancesDataFilter.from_dict(_filter_)

        _page = d.pop("page", UNSET)
        page: SearchElementInstancesDataPage | Unset
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = SearchElementInstancesDataPage.from_dict(_page)

        search_element_instances_data = cls(
            sort=sort,
            filter_=filter_,
            page=page,
        )

        return search_element_instances_data
