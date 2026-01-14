from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.search_group_ids_for_tenant_data_sort_item_field import (
    SearchGroupIdsForTenantDataSortItemField,
)
from ..models.search_group_ids_for_tenant_data_sort_item_order import (
    SearchGroupIdsForTenantDataSortItemOrder,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchGroupIdsForTenantDataSortItem")


@_attrs_define
class SearchGroupIdsForTenantDataSortItem:
    """
    Attributes:
        field (SearchGroupIdsForTenantDataSortItemField): The field to sort by.
        order (SearchGroupIdsForTenantDataSortItemOrder | Unset): The order in which to sort the related field. Default:
            SearchGroupIdsForTenantDataSortItemOrder.ASC.
    """

    field: SearchGroupIdsForTenantDataSortItemField
    order: SearchGroupIdsForTenantDataSortItemOrder | Unset = (
        SearchGroupIdsForTenantDataSortItemOrder.ASC
    )

    def to_dict(self) -> dict[str, Any]:
        field = self.field.value

        order: str | Unset = UNSET
        if not isinstance(self.order, Unset):
            order = self.order.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "field": field,
            }
        )
        if order is not UNSET:
            field_dict["order"] = order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field = SearchGroupIdsForTenantDataSortItemField(d.pop("field"))

        _order = d.pop("order", UNSET)
        order: SearchGroupIdsForTenantDataSortItemOrder | Unset
        if isinstance(_order, Unset):
            order = UNSET
        else:
            order = SearchGroupIdsForTenantDataSortItemOrder(_order)

        search_group_ids_for_tenant_data_sort_item = cls(
            field=field,
            order=order,
        )

        return search_group_ids_for_tenant_data_sort_item
