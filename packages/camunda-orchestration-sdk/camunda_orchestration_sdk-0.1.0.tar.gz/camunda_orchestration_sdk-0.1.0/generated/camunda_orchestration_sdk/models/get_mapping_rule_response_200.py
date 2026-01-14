from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetMappingRuleResponse200")


@_attrs_define
class GetMappingRuleResponse200:
    """
    Attributes:
        claim_name (str | Unset): The name of the claim to map.
        claim_value (str | Unset): The value of the claim to map.
        name (str | Unset): The name of the mapping rule.
        mapping_rule_id (str | Unset): The ID of the mapping rule.
    """

    claim_name: str | Unset = UNSET
    claim_value: str | Unset = UNSET
    name: str | Unset = UNSET
    mapping_rule_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        claim_name = self.claim_name

        claim_value = self.claim_value

        name = self.name

        mapping_rule_id = self.mapping_rule_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if claim_name is not UNSET:
            field_dict["claimName"] = claim_name
        if claim_value is not UNSET:
            field_dict["claimValue"] = claim_value
        if name is not UNSET:
            field_dict["name"] = name
        if mapping_rule_id is not UNSET:
            field_dict["mappingRuleId"] = mapping_rule_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        claim_name = d.pop("claimName", UNSET)

        claim_value = d.pop("claimValue", UNSET)

        name = d.pop("name", UNSET)

        mapping_rule_id = d.pop("mappingRuleId", UNSET)

        get_mapping_rule_response_200 = cls(
            claim_name=claim_name,
            claim_value=claim_value,
            name=name,
            mapping_rule_id=mapping_rule_id,
        )

        get_mapping_rule_response_200.additional_properties = d
        return get_mapping_rule_response_200

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
