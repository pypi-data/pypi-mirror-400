from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UpdateMappingRuleData")


@_attrs_define
class UpdateMappingRuleData:
    """
    Attributes:
        claim_name (str): The name of the claim to map.
        claim_value (str): The value of the claim to map.
        name (str): The name of the mapping rule.
    """

    claim_name: str
    claim_value: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        claim_name = self.claim_name

        claim_value = self.claim_value

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "claimName": claim_name,
                "claimValue": claim_value,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        claim_name = d.pop("claimName")

        claim_value = d.pop("claimValue")

        name = d.pop("name")

        update_mapping_rule_data = cls(
            claim_name=claim_name,
            claim_value=claim_value,
            name=name,
        )

        update_mapping_rule_data.additional_properties = d
        return update_mapping_rule_data

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
