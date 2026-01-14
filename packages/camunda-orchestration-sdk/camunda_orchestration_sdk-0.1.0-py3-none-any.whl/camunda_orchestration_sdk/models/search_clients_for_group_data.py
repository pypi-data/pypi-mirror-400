from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_clients_for_group_data_page import (
        SearchClientsForGroupDataPage,
    )
    from ..models.search_clients_for_group_data_sort_item import (
        SearchClientsForGroupDataSortItem,
    )


T = TypeVar("T", bound="SearchClientsForGroupData")


@_attrs_define
class SearchClientsForGroupData:
    """
    Attributes:
        sort (list[SearchClientsForGroupDataSortItem] | Unset): Sort field criteria.
        page (SearchClientsForGroupDataPage | Unset): Pagination criteria.
    """

    sort: list[SearchClientsForGroupDataSortItem] | Unset = UNSET
    page: SearchClientsForGroupDataPage | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

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
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sort is not UNSET:
            field_dict["sort"] = sort
        if page is not UNSET:
            field_dict["page"] = page

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_clients_for_group_data_page import (
            SearchClientsForGroupDataPage,
        )
        from ..models.search_clients_for_group_data_sort_item import (
            SearchClientsForGroupDataSortItem,
        )

        d = dict(src_dict)
        _sort = d.pop("sort", UNSET)
        sort: list[SearchClientsForGroupDataSortItem] | Unset = UNSET
        if _sort is not UNSET:
            sort = []
            for sort_item_data in _sort:
                sort_item = SearchClientsForGroupDataSortItem.from_dict(sort_item_data)

                sort.append(sort_item)

        _page = d.pop("page", UNSET)
        page: SearchClientsForGroupDataPage | Unset
        if isinstance(_page, Unset):
            page = UNSET
        else:
            page = SearchClientsForGroupDataPage.from_dict(_page)

        search_clients_for_group_data = cls(
            sort=sort,
            page=page,
        )

        search_clients_for_group_data.additional_properties = d
        return search_clients_for_group_data

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
