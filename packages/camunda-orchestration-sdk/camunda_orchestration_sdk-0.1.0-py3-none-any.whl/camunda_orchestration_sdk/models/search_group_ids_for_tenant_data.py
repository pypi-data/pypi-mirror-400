from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_group_ids_for_tenant_data_page import (
        SearchGroupIdsForTenantDataPage,
    )
    from ..models.search_group_ids_for_tenant_data_sort_item import (
        SearchGroupIdsForTenantDataSortItem,
    )


T = TypeVar("T", bound="SearchGroupIdsForTenantData")


@_attrs_define
class SearchGroupIdsForTenantData:
    """
    Attributes:
        sort (list[SearchGroupIdsForTenantDataSortItem] | Unset): Sort field criteria.
        page (SearchGroupIdsForTenantDataPage | Unset): Pagination criteria.
    """

    sort: list[SearchGroupIdsForTenantDataSortItem] | Unset = UNSET
    page: SearchGroupIdsForTenantDataPage | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        sort: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.sort, Unset):
            sort = []
            for sort_item_data in self.sort:
                sort_item = sort_item_data.to_dict()
                sort.append(sort_item)

        page: dict[str, Any] | Unset = UNSET
        if not isinstance(self.page, Unset):
            page = self.page.to_dict()

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if sort is not UNSET:
            field_dict["sort"] = sort
        if page is not UNSET:
            field_dict["page"] = page

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_group_ids_for_tenant_data_page import (
            SearchGroupIdsForTenantDataPage,
        )
        from ..models.search_group_ids_for_tenant_data_sort_item import (
            SearchGroupIdsForTenantDataSortItem,
        )

        d = dict(src_dict)
        _sort = d.pop("sort", UNSET)
        sort: list[SearchGroupIdsForTenantDataSortItem] | Unset = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = SearchGroupIdsForTenantDataSortItem.from_dict(
                    sort_item_data
                )

                sort.append(sort_item)

        _page = d.pop("page", UNSET)
        page: SearchGroupIdsForTenantDataPage | Unset
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = SearchGroupIdsForTenantDataPage.from_dict(_page)

        search_group_ids_for_tenant_data = cls(
            sort=sort,
            page=page,
        )

        return search_group_ids_for_tenant_data
