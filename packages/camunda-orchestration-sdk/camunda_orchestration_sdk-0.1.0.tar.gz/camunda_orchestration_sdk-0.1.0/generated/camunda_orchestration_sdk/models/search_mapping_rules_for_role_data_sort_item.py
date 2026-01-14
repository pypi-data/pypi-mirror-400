from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.search_mapping_rules_for_role_data_sort_item_field import (
    SearchMappingRulesForRoleDataSortItemField,
)
from ..models.search_mapping_rules_for_role_data_sort_item_order import (
    SearchMappingRulesForRoleDataSortItemOrder,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchMappingRulesForRoleDataSortItem")


@_attrs_define
class SearchMappingRulesForRoleDataSortItem:
    """
    Attributes:
        field (SearchMappingRulesForRoleDataSortItemField): The field to sort by.
        order (SearchMappingRulesForRoleDataSortItemOrder | Unset): The order in which to sort the related field.
            Default: SearchMappingRulesForRoleDataSortItemOrder.ASC.
    """

    field: SearchMappingRulesForRoleDataSortItemField
    order: SearchMappingRulesForRoleDataSortItemOrder | Unset = (
        SearchMappingRulesForRoleDataSortItemOrder.ASC
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field = self.field.value

        order: str | Unset = UNSET
        if not isinstance(self.order, Unset):
            order = self.order.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
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
        field = SearchMappingRulesForRoleDataSortItemField(d.pop("field"))

        _order = d.pop("order", UNSET)
        order: SearchMappingRulesForRoleDataSortItemOrder | Unset
        if isinstance(_order, Unset):
            order = UNSET
        else:
            order = SearchMappingRulesForRoleDataSortItemOrder(_order)

        search_mapping_rules_for_role_data_sort_item = cls(
            field=field,
            order=order,
        )

        search_mapping_rules_for_role_data_sort_item.additional_properties = d
        return search_mapping_rules_for_role_data_sort_item

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
