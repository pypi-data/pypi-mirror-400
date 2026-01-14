from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.search_audit_logs_data_sort_item_field import (
    SearchAuditLogsDataSortItemField,
)
from ..models.search_audit_logs_data_sort_item_order import (
    SearchAuditLogsDataSortItemOrder,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchAuditLogsDataSortItem")


@_attrs_define
class SearchAuditLogsDataSortItem:
    """
    Attributes:
        field (SearchAuditLogsDataSortItemField): The field to sort by.
        order (SearchAuditLogsDataSortItemOrder | Unset): The order in which to sort the related field. Default:
            SearchAuditLogsDataSortItemOrder.ASC.
    """

    field: SearchAuditLogsDataSortItemField
    order: SearchAuditLogsDataSortItemOrder | Unset = (
        SearchAuditLogsDataSortItemOrder.ASC
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
        field = SearchAuditLogsDataSortItemField(d.pop("field"))

        _order = d.pop("order", UNSET)
        order: SearchAuditLogsDataSortItemOrder | Unset
        if isinstance(_order, Unset):
            order = UNSET
        else:
            order = SearchAuditLogsDataSortItemOrder(_order)

        search_audit_logs_data_sort_item = cls(
            field=field,
            order=order,
        )

        return search_audit_logs_data_sort_item
