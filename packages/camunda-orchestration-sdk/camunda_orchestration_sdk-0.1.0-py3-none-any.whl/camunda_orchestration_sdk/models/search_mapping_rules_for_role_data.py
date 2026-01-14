from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_mapping_rules_for_role_data_filter import (
        SearchMappingRulesForRoleDataFilter,
    )
    from ..models.search_mapping_rules_for_role_data_page import (
        SearchMappingRulesForRoleDataPage,
    )
    from ..models.search_mapping_rules_for_role_data_sort_item import (
        SearchMappingRulesForRoleDataSortItem,
    )


T = TypeVar("T", bound="SearchMappingRulesForRoleData")


@_attrs_define
class SearchMappingRulesForRoleData:
    """
    Attributes:
        sort (list[SearchMappingRulesForRoleDataSortItem] | Unset): Sort field criteria.
        filter_ (SearchMappingRulesForRoleDataFilter | Unset): The mapping rule search filters.
        page (SearchMappingRulesForRoleDataPage | Unset): Pagination criteria.
    """

    sort: list[SearchMappingRulesForRoleDataSortItem] | Unset = UNSET
    filter_: SearchMappingRulesForRoleDataFilter | Unset = UNSET
    page: SearchMappingRulesForRoleDataPage | Unset = UNSET

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
        from ..models.search_mapping_rules_for_role_data_filter import (
            SearchMappingRulesForRoleDataFilter,
        )
        from ..models.search_mapping_rules_for_role_data_page import (
            SearchMappingRulesForRoleDataPage,
        )
        from ..models.search_mapping_rules_for_role_data_sort_item import (
            SearchMappingRulesForRoleDataSortItem,
        )

        d = dict(src_dict)
        _sort = d.pop("sort", UNSET)
        sort: list[SearchMappingRulesForRoleDataSortItem] | Unset = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = SearchMappingRulesForRoleDataSortItem.from_dict(
                    sort_item_data
                )

                sort.append(sort_item)

        _filter_ = d.pop("filter", UNSET)
        filter_: SearchMappingRulesForRoleDataFilter | Unset
        if isinstance(_filter_, Unset):
            filter_ = UNSET
        else:
            filter_ = SearchMappingRulesForRoleDataFilter.from_dict(_filter_)

        _page = d.pop("page", UNSET)
        page: SearchMappingRulesForRoleDataPage | Unset
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = SearchMappingRulesForRoleDataPage.from_dict(_page)

        search_mapping_rules_for_role_data = cls(
            sort=sort,
            filter_=filter_,
            page=page,
        )

        return search_mapping_rules_for_role_data
