from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.evaluate_decision_response_200_evaluated_decisions_item_matched_rules_item_evaluated_outputs_item import (
        EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItemEvaluatedOutputsItem,
    )


T = TypeVar(
    "T", bound="EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItem"
)


@_attrs_define
class EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItem:
    """A decision rule that matched within this decision evaluation.

    Attributes:
        rule_id (str | Unset): The ID of the matched rule.
        rule_index (int | Unset): The index of the matched rule.
        evaluated_outputs (list[EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItemEvaluatedOutputsItem] |
            Unset): The evaluated decision outputs.
    """

    rule_id: str | Unset = UNSET
    rule_index: int | Unset = UNSET
    evaluated_outputs: (
        list[
            EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItemEvaluatedOutputsItem
        ]
        | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rule_id = self.rule_id

        rule_index = self.rule_index

        evaluated_outputs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.evaluated_outputs, Unset):
            evaluated_outputs = []
            for evaluated_outputs_item_data in self.evaluated_outputs:
                evaluated_outputs_item = evaluated_outputs_item_data.to_dict()
                evaluated_outputs.append(evaluated_outputs_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if rule_id is not UNSET:
            field_dict["ruleId"] = rule_id
        if rule_index is not UNSET:
            field_dict["ruleIndex"] = rule_index
        if evaluated_outputs is not UNSET:
            field_dict["evaluatedOutputs"] = evaluated_outputs

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.evaluate_decision_response_200_evaluated_decisions_item_matched_rules_item_evaluated_outputs_item import (
            EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItemEvaluatedOutputsItem,
        )

        d = dict(src_dict)
        rule_id = d.pop("ruleId", UNSET)

        rule_index = d.pop("ruleIndex", UNSET)

        _evaluated_outputs = d.pop("evaluatedOutputs", UNSET)
        evaluated_outputs: (
            list[
                EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItemEvaluatedOutputsItem
            ]
            | Unset
        ) = UNSET
        if _evaluated_outputs is not UNSET:
            evaluated_outputs = []
            for evaluated_outputs_item_data in _evaluated_outputs:
                evaluated_outputs_item = EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItemEvaluatedOutputsItem.from_dict(
                    evaluated_outputs_item_data
                )

                evaluated_outputs.append(evaluated_outputs_item)

        evaluate_decision_response_200_evaluated_decisions_item_matched_rules_item = (
            cls(
                rule_id=rule_id,
                rule_index=rule_index,
                evaluated_outputs=evaluated_outputs,
            )
        )

        evaluate_decision_response_200_evaluated_decisions_item_matched_rules_item.additional_properties = d
        return (
            evaluate_decision_response_200_evaluated_decisions_item_matched_rules_item
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
