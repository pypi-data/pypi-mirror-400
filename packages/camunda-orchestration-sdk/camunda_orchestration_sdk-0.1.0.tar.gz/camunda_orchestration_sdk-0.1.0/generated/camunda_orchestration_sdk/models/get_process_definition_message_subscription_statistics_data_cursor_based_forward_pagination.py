from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar(
    "T",
    bound="GetProcessDefinitionMessageSubscriptionStatisticsDataCursorBasedForwardPagination",
)


@_attrs_define
class GetProcessDefinitionMessageSubscriptionStatisticsDataCursorBasedForwardPagination:
    """
    Attributes:
        after (str): Use the `endCursor` value from the previous response to fetch the next page of results. Example:
            WzIyNTE3OTk4MTM2ODcxMDJd.
        limit (int | Unset): The maximum number of items to return in one request. Default: 100.
    """

    after: EndCursor
    limit: int | Unset = 100
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        after = self.after

        limit = self.limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "after": after,
            }
        )
        if limit is not UNSET:
            field_dict["limit"] = limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        after = lift_end_cursor(d.pop("after"))

        limit = d.pop("limit", UNSET)

        get_process_definition_message_subscription_statistics_data_cursor_based_forward_pagination = cls(
            after=after,
            limit=limit,
        )

        get_process_definition_message_subscription_statistics_data_cursor_based_forward_pagination.additional_properties = d
        return get_process_definition_message_subscription_statistics_data_cursor_based_forward_pagination

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
