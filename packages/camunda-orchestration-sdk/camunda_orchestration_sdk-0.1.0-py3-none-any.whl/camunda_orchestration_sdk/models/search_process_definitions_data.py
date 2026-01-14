from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_process_definitions_data_filter import (
        SearchProcessDefinitionsDataFilter,
    )
    from ..models.search_process_definitions_data_page import (
        SearchProcessDefinitionsDataPage,
    )
    from ..models.search_process_definitions_data_sort_item import (
        SearchProcessDefinitionsDataSortItem,
    )


T = TypeVar("T", bound="SearchProcessDefinitionsData")


@_attrs_define
class SearchProcessDefinitionsData:
    """
    Attributes:
        sort (list[SearchProcessDefinitionsDataSortItem] | Unset): Sort field criteria.
        filter_ (SearchProcessDefinitionsDataFilter | Unset): The process definition search filters.
        page (SearchProcessDefinitionsDataPage | Unset): Pagination criteria.
    """

    sort: list[SearchProcessDefinitionsDataSortItem] | Unset = UNSET
    filter_: SearchProcessDefinitionsDataFilter | Unset = UNSET
    page: SearchProcessDefinitionsDataPage | Unset = UNSET

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
        from ..models.search_process_definitions_data_filter import (
            SearchProcessDefinitionsDataFilter,
        )
        from ..models.search_process_definitions_data_page import (
            SearchProcessDefinitionsDataPage,
        )
        from ..models.search_process_definitions_data_sort_item import (
            SearchProcessDefinitionsDataSortItem,
        )

        d = dict(src_dict)
        _sort = d.pop("sort", UNSET)
        sort: list[SearchProcessDefinitionsDataSortItem] | Unset = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = SearchProcessDefinitionsDataSortItem.from_dict(
                    sort_item_data
                )

                sort.append(sort_item)

        _filter_ = d.pop("filter", UNSET)
        filter_: SearchProcessDefinitionsDataFilter | Unset
        if isinstance(_filter_, Unset):
            filter_ = UNSET
        else:
            filter_ = SearchProcessDefinitionsDataFilter.from_dict(_filter_)

        _page = d.pop("page", UNSET)
        page: SearchProcessDefinitionsDataPage | Unset
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = SearchProcessDefinitionsDataPage.from_dict(_page)

        search_process_definitions_data = cls(
            sort=sort,
            filter_=filter_,
            page=page,
        )

        return search_process_definitions_data
