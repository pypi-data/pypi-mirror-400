from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_user_task_variables_data_filter import (
        SearchUserTaskVariablesDataFilter,
    )
    from ..models.search_user_task_variables_data_page import (
        SearchUserTaskVariablesDataPage,
    )
    from ..models.search_user_task_variables_data_sort_item import (
        SearchUserTaskVariablesDataSortItem,
    )


T = TypeVar("T", bound="SearchUserTaskVariablesData")


@_attrs_define
class SearchUserTaskVariablesData:
    """User task search query request.

    Attributes:
        sort (list[SearchUserTaskVariablesDataSortItem] | Unset): Sort field criteria.
        filter_ (SearchUserTaskVariablesDataFilter | Unset): The user task variable search filters.
        page (SearchUserTaskVariablesDataPage | Unset): Pagination criteria.
    """

    sort: list[SearchUserTaskVariablesDataSortItem] | Unset = UNSET
    filter_: SearchUserTaskVariablesDataFilter | Unset = UNSET
    page: SearchUserTaskVariablesDataPage | Unset = UNSET

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
        from ..models.search_user_task_variables_data_filter import (
            SearchUserTaskVariablesDataFilter,
        )
        from ..models.search_user_task_variables_data_page import (
            SearchUserTaskVariablesDataPage,
        )
        from ..models.search_user_task_variables_data_sort_item import (
            SearchUserTaskVariablesDataSortItem,
        )

        d = dict(src_dict)
        _sort = d.pop("sort", UNSET)
        sort: list[SearchUserTaskVariablesDataSortItem] | Unset = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = SearchUserTaskVariablesDataSortItem.from_dict(
                    sort_item_data
                )

                sort.append(sort_item)

        _filter_ = d.pop("filter", UNSET)
        filter_: SearchUserTaskVariablesDataFilter | Unset
        if isinstance(_filter_, Unset):
            filter_ = UNSET
        else:
            filter_ = SearchUserTaskVariablesDataFilter.from_dict(_filter_)

        _page = d.pop("page", UNSET)
        page: SearchUserTaskVariablesDataPage | Unset
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = SearchUserTaskVariablesDataPage.from_dict(_page)

        search_user_task_variables_data = cls(
            sort=sort,
            filter_=filter_,
            page=page,
        )

        return search_user_task_variables_data
