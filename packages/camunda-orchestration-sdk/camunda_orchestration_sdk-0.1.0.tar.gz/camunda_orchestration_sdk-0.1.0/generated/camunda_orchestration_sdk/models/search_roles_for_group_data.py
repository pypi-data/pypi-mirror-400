from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_roles_for_group_data_filter import (
        SearchRolesForGroupDataFilter,
    )
    from ..models.search_roles_for_group_data_page import SearchRolesForGroupDataPage
    from ..models.search_roles_for_group_data_sort_item import (
        SearchRolesForGroupDataSortItem,
    )


T = TypeVar("T", bound="SearchRolesForGroupData")


@_attrs_define
class SearchRolesForGroupData:
    """Role search request.

    Attributes:
        sort (list[SearchRolesForGroupDataSortItem] | Unset): Sort field criteria.
        filter_ (SearchRolesForGroupDataFilter | Unset): The role search filters.
        page (SearchRolesForGroupDataPage | Unset): Pagination criteria.
    """

    sort: list[SearchRolesForGroupDataSortItem] | Unset = UNSET
    filter_: SearchRolesForGroupDataFilter | Unset = UNSET
    page: SearchRolesForGroupDataPage | Unset = UNSET

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
        from ..models.search_roles_for_group_data_filter import (
            SearchRolesForGroupDataFilter,
        )
        from ..models.search_roles_for_group_data_page import (
            SearchRolesForGroupDataPage,
        )
        from ..models.search_roles_for_group_data_sort_item import (
            SearchRolesForGroupDataSortItem,
        )

        d = dict(src_dict)
        _sort = d.pop("sort", UNSET)
        sort: list[SearchRolesForGroupDataSortItem] | Unset = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = SearchRolesForGroupDataSortItem.from_dict(sort_item_data)

                sort.append(sort_item)

        _filter_ = d.pop("filter", UNSET)
        filter_: SearchRolesForGroupDataFilter | Unset
        if isinstance(_filter_, Unset):
            filter_ = UNSET
        else:
            filter_ = SearchRolesForGroupDataFilter.from_dict(_filter_)

        _page = d.pop("page", UNSET)
        page: SearchRolesForGroupDataPage | Unset
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = SearchRolesForGroupDataPage.from_dict(_page)

        search_roles_for_group_data = cls(
            sort=sort,
            filter_=filter_,
            page=page,
        )

        return search_roles_for_group_data
