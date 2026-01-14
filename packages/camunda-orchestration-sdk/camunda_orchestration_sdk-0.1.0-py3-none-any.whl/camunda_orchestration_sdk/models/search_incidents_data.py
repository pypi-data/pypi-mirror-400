from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_incidents_data_filter import SearchIncidentsDataFilter
    from ..models.search_incidents_data_page import SearchIncidentsDataPage
    from ..models.search_incidents_data_sort_item import SearchIncidentsDataSortItem


T = TypeVar("T", bound="SearchIncidentsData")


@_attrs_define
class SearchIncidentsData:
    """
    Attributes:
        sort (list[SearchIncidentsDataSortItem] | Unset): Sort field criteria.
        filter_ (SearchIncidentsDataFilter | Unset): The incident search filters.
        page (SearchIncidentsDataPage | Unset): Pagination criteria.
    """

    sort: list[SearchIncidentsDataSortItem] | Unset = UNSET
    filter_: SearchIncidentsDataFilter | Unset = UNSET
    page: SearchIncidentsDataPage | Unset = UNSET

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
        from ..models.search_incidents_data_filter import SearchIncidentsDataFilter
        from ..models.search_incidents_data_page import SearchIncidentsDataPage
        from ..models.search_incidents_data_sort_item import SearchIncidentsDataSortItem

        d = dict(src_dict)
        _sort = d.pop("sort", UNSET)
        sort: list[SearchIncidentsDataSortItem] | Unset = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = SearchIncidentsDataSortItem.from_dict(sort_item_data)

                sort.append(sort_item)

        _filter_ = d.pop("filter", UNSET)
        filter_: SearchIncidentsDataFilter | Unset
        if isinstance(_filter_, Unset):
            filter_ = UNSET
        else:
            filter_ = SearchIncidentsDataFilter.from_dict(_filter_)

        _page = d.pop("page", UNSET)
        page: SearchIncidentsDataPage | Unset
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = SearchIncidentsDataPage.from_dict(_page)

        search_incidents_data = cls(
            sort=sort,
            filter_=filter_,
            page=page,
        )

        return search_incidents_data
