from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="CreateMappingRuleData")


@_attrs_define
class CreateMappingRuleData:
    """
    Attributes:
        mapping_rule_id (str): The unique ID of the mapping rule.
        claim_name (str): The name of the claim to map.
        claim_value (str): The value of the claim to map.
        name (str): The name of the mapping rule.
    """

    mapping_rule_id: str
    claim_name: str
    claim_value: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        mapping_rule_id = self.mapping_rule_id

        claim_name = self.claim_name

        claim_value = self.claim_value

        name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "mappingRuleId": mapping_rule_id,
                "claimName": claim_name,
                "claimValue": claim_value,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        mapping_rule_id = d.pop("mappingRuleId")

        claim_name = d.pop("claimName")

        claim_value = d.pop("claimValue")

        name = d.pop("name")

        create_mapping_rule_data = cls(
            mapping_rule_id=mapping_rule_id,
            claim_name=claim_name,
            claim_value=claim_value,
            name=name,
        )

        return create_mapping_rule_data
