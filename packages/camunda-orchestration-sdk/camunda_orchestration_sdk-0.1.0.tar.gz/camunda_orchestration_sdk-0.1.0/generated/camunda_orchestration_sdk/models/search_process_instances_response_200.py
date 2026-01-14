from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.search_process_instances_response_200_items_item import (
        SearchProcessInstancesResponse200ItemsItem,
    )
    from ..models.search_process_instances_response_200_page import (
        SearchProcessInstancesResponse200Page,
    )


T = TypeVar("T", bound="SearchProcessInstancesResponse200")


@_attrs_define
class SearchProcessInstancesResponse200:
    """Process instance search response.

    Attributes:
        items (list[SearchProcessInstancesResponse200ItemsItem]): The matching process instances.
        page (SearchProcessInstancesResponse200Page): Pagination information about the search results. Example:
            {'totalItems': 1, 'hasMoreTotalItems': False}.
    """

    items: list[SearchProcessInstancesResponse200ItemsItem]
    page: SearchProcessInstancesResponse200Page
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        page = self.page.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "items": items,
                "page": page,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_process_instances_response_200_items_item import (
            SearchProcessInstancesResponse200ItemsItem,
        )
        from ..models.search_process_instances_response_200_page import (
            SearchProcessInstancesResponse200Page,
        )

        d = dict(src_dict)
        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = SearchProcessInstancesResponse200ItemsItem.from_dict(
                items_item_data
            )

            items.append(items_item)

        page = SearchProcessInstancesResponse200Page.from_dict(d.pop("page"))

        search_process_instances_response_200 = cls(
            items=items,
            page=page,
        )

        search_process_instances_response_200.additional_properties = d
        return search_process_instances_response_200

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
