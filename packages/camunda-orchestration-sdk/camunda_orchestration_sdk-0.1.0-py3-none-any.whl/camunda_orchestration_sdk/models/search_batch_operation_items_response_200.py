from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_batch_operation_items_response_200_items_item import (
        SearchBatchOperationItemsResponse200ItemsItem,
    )
    from ..models.search_batch_operation_items_response_200_page import (
        SearchBatchOperationItemsResponse200Page,
    )


T = TypeVar("T", bound="SearchBatchOperationItemsResponse200")


@_attrs_define
class SearchBatchOperationItemsResponse200:
    """
    Attributes:
        page (SearchBatchOperationItemsResponse200Page): Pagination information about the search results. Example:
            {'totalItems': 1, 'hasMoreTotalItems': False}.
        items (list[SearchBatchOperationItemsResponse200ItemsItem] | Unset): The matching batch operation items.
    """

    page: SearchBatchOperationItemsResponse200Page
    items: list[SearchBatchOperationItemsResponse200ItemsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page = self.page.to_dict()

        items: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item = items_item_data.to_dict()
                items.append(items_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "page": page,
            }
        )
        if items is not UNSET:
            field_dict["items"] = items

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_batch_operation_items_response_200_items_item import (
            SearchBatchOperationItemsResponse200ItemsItem,
        )
        from ..models.search_batch_operation_items_response_200_page import (
            SearchBatchOperationItemsResponse200Page,
        )

        d = dict(src_dict)
        page = SearchBatchOperationItemsResponse200Page.from_dict(d.pop("page"))

        _items = d.pop("items", UNSET)
        items: list[SearchBatchOperationItemsResponse200ItemsItem] | Unset = UNSET
        if _items is not UNSET:
            items = []
            for items_item_data in _items:
                items_item = SearchBatchOperationItemsResponse200ItemsItem.from_dict(
                    items_item_data
                )

                items.append(items_item)

        search_batch_operation_items_response_200 = cls(
            page=page,
            items=items,
        )

        search_batch_operation_items_response_200.additional_properties = d
        return search_batch_operation_items_response_200

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
