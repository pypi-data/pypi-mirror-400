from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar(
    "T", bound="GetDecisionInstanceResponse200MatchedRulesItemEvaluatedOutputsItem"
)


@_attrs_define
class GetDecisionInstanceResponse200MatchedRulesItemEvaluatedOutputsItem:
    """The evaluated decision outputs.

    Attributes:
        output_id (str | Unset):
        output_name (str | Unset):
        output_value (str | Unset):
        rule_id (str | Unset):
        rule_index (int | Unset):
    """

    output_id: str | Unset = UNSET
    output_name: str | Unset = UNSET
    output_value: str | Unset = UNSET
    rule_id: str | Unset = UNSET
    rule_index: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output_id = self.output_id

        output_name = self.output_name

        output_value = self.output_value

        rule_id = self.rule_id

        rule_index = self.rule_index

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if output_id is not UNSET:
            field_dict["outputId"] = output_id
        if output_name is not UNSET:
            field_dict["outputName"] = output_name
        if output_value is not UNSET:
            field_dict["outputValue"] = output_value
        if rule_id is not UNSET:
            field_dict["ruleId"] = rule_id
        if rule_index is not UNSET:
            field_dict["ruleIndex"] = rule_index

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        output_id = d.pop("outputId", UNSET)

        output_name = d.pop("outputName", UNSET)

        output_value = d.pop("outputValue", UNSET)

        rule_id = d.pop("ruleId", UNSET)

        rule_index = d.pop("ruleIndex", UNSET)

        get_decision_instance_response_200_matched_rules_item_evaluated_outputs_item = (
            cls(
                output_id=output_id,
                output_name=output_name,
                output_value=output_value,
                rule_id=rule_id,
                rule_index=rule_index,
            )
        )

        get_decision_instance_response_200_matched_rules_item_evaluated_outputs_item.additional_properties = d
        return (
            get_decision_instance_response_200_matched_rules_item_evaluated_outputs_item
        )

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
