from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetProcessInstanceStatisticsByDefinitionDataFilter")


@_attrs_define
class GetProcessInstanceStatisticsByDefinitionDataFilter:
    """Filter criteria for the aggregated process instance statistics.

    Attributes:
        error_hash_code (int): The error hash code of the incidents to filter the process instance statistics by.
    """

    error_hash_code: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error_hash_code = self.error_hash_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "errorHashCode": error_hash_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        error_hash_code = d.pop("errorHashCode")

        get_process_instance_statistics_by_definition_data_filter = cls(
            error_hash_code=error_hash_code,
        )

        get_process_instance_statistics_by_definition_data_filter.additional_properties = d
        return get_process_instance_statistics_by_definition_data_filter

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
