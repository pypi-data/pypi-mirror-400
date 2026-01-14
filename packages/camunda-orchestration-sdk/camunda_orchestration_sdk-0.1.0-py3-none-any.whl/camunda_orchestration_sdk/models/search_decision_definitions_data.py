from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_decision_definitions_data_filter import (
        SearchDecisionDefinitionsDataFilter,
    )
    from ..models.search_decision_definitions_data_page import (
        SearchDecisionDefinitionsDataPage,
    )
    from ..models.search_decision_definitions_data_sort_item import (
        SearchDecisionDefinitionsDataSortItem,
    )


T = TypeVar("T", bound="SearchDecisionDefinitionsData")


@_attrs_define
class SearchDecisionDefinitionsData:
    """
    Attributes:
        sort (list[SearchDecisionDefinitionsDataSortItem] | Unset): Sort field criteria.
        filter_ (SearchDecisionDefinitionsDataFilter | Unset): The decision definition search filters.
        page (SearchDecisionDefinitionsDataPage | Unset): Pagination criteria.
    """

    sort: list[SearchDecisionDefinitionsDataSortItem] | Unset = UNSET
    filter_: SearchDecisionDefinitionsDataFilter | Unset = UNSET
    page: SearchDecisionDefinitionsDataPage | Unset = UNSET

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
        from ..models.search_decision_definitions_data_filter import (
            SearchDecisionDefinitionsDataFilter,
        )
        from ..models.search_decision_definitions_data_page import (
            SearchDecisionDefinitionsDataPage,
        )
        from ..models.search_decision_definitions_data_sort_item import (
            SearchDecisionDefinitionsDataSortItem,
        )

        d = dict(src_dict)
        _sort = d.pop("sort", UNSET)
        sort: list[SearchDecisionDefinitionsDataSortItem] | Unset = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = SearchDecisionDefinitionsDataSortItem.from_dict(
                    sort_item_data
                )

                sort.append(sort_item)

        _filter_ = d.pop("filter", UNSET)
        filter_: SearchDecisionDefinitionsDataFilter | Unset
        if isinstance(_filter_, Unset):
            filter_ = UNSET
        else:
            filter_ = SearchDecisionDefinitionsDataFilter.from_dict(_filter_)

        _page = d.pop("page", UNSET)
        page: SearchDecisionDefinitionsDataPage | Unset
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = SearchDecisionDefinitionsDataPage.from_dict(_page)

        search_decision_definitions_data = cls(
            sort=sort,
            filter_=filter_,
            page=page,
        )

        return search_decision_definitions_data
