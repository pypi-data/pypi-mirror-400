from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.evaluate_decision_response_200_evaluated_decisions_item_evaluated_inputs_item import (
        EvaluateDecisionResponse200EvaluatedDecisionsItemEvaluatedInputsItem,
    )
    from ..models.evaluate_decision_response_200_evaluated_decisions_item_matched_rules_item import (
        EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItem,
    )


T = TypeVar("T", bound="EvaluateDecisionResponse200EvaluatedDecisionsItem")


@_attrs_define
class EvaluateDecisionResponse200EvaluatedDecisionsItem:
    """A decision that was evaluated.

    Attributes:
        decision_definition_id (str | Unset): The ID of the decision which was evaluated. Example: new-hire-onboarding-
            workflow.
        decision_definition_name (str | Unset): The name of the decision which was evaluated.
        decision_definition_version (int | Unset): The version of the decision which was evaluated.
        decision_definition_type (str | Unset): The type of the decision which was evaluated.
        output (str | Unset): JSON document that will instantiate the result of the decision which was evaluated.
        tenant_id (str | Unset): The tenant ID of the evaluated decision. Example: customer-service.
        matched_rules (list[EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItem] | Unset): The decision
            rules that matched within this decision evaluation.
        evaluated_inputs (list[EvaluateDecisionResponse200EvaluatedDecisionsItemEvaluatedInputsItem] | Unset): The
            decision inputs that were evaluated within this decision evaluation.
        decision_definition_key (str | Unset): The unique key identifying the decision which was evaluate. Example:
            2251799813326547.
        decision_evaluation_instance_key (str | Unset): The unique key identifying this decision evaluation instance.
            Example: 2251799813684367.
    """

    decision_definition_id: DecisionDefinitionId | Unset = UNSET
    decision_definition_name: str | Unset = UNSET
    decision_definition_version: int | Unset = UNSET
    decision_definition_type: str | Unset = UNSET
    output: str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    matched_rules: (
        list[EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItem] | Unset
    ) = UNSET
    evaluated_inputs: (
        list[EvaluateDecisionResponse200EvaluatedDecisionsItemEvaluatedInputsItem]
        | Unset
    ) = UNSET
    decision_definition_key: DecisionDefinitionKey | Unset = UNSET
    decision_evaluation_instance_key: DecisionEvaluationInstanceKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        decision_definition_id = self.decision_definition_id

        decision_definition_name = self.decision_definition_name

        decision_definition_version = self.decision_definition_version

        decision_definition_type = self.decision_definition_type

        output = self.output

        tenant_id = self.tenant_id

        matched_rules: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.matched_rules, Unset):
            matched_rules = []
            for matched_rules_item_data in self.matched_rules:
                matched_rules_item = matched_rules_item_data.to_dict()
                matched_rules.append(matched_rules_item)

        evaluated_inputs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.evaluated_inputs, Unset):
            evaluated_inputs = []
            for evaluated_inputs_item_data in self.evaluated_inputs:
                evaluated_inputs_item = evaluated_inputs_item_data.to_dict()
                evaluated_inputs.append(evaluated_inputs_item)

        decision_definition_key = self.decision_definition_key

        decision_evaluation_instance_key = self.decision_evaluation_instance_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if decision_definition_id is not UNSET:
            field_dict["decisionDefinitionId"] = decision_definition_id
        if decision_definition_name is not UNSET:
            field_dict["decisionDefinitionName"] = decision_definition_name
        if decision_definition_version is not UNSET:
            field_dict["decisionDefinitionVersion"] = decision_definition_version
        if decision_definition_type is not UNSET:
            field_dict["decisionDefinitionType"] = decision_definition_type
        if output is not UNSET:
            field_dict["output"] = output
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if matched_rules is not UNSET:
            field_dict["matchedRules"] = matched_rules
        if evaluated_inputs is not UNSET:
            field_dict["evaluatedInputs"] = evaluated_inputs
        if decision_definition_key is not UNSET:
            field_dict["decisionDefinitionKey"] = decision_definition_key
        if decision_evaluation_instance_key is not UNSET:
            field_dict["decisionEvaluationInstanceKey"] = (
                decision_evaluation_instance_key
            )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.evaluate_decision_response_200_evaluated_decisions_item_evaluated_inputs_item import (
            EvaluateDecisionResponse200EvaluatedDecisionsItemEvaluatedInputsItem,
        )
        from ..models.evaluate_decision_response_200_evaluated_decisions_item_matched_rules_item import (
            EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItem,
        )

        d = dict(src_dict)
        decision_definition_id = lift_decision_definition_id(_val) if (_val := d.pop("decisionDefinitionId", UNSET)) is not UNSET else UNSET

        decision_definition_name = d.pop("decisionDefinitionName", UNSET)

        decision_definition_version = d.pop("decisionDefinitionVersion", UNSET)

        decision_definition_type = d.pop("decisionDefinitionType", UNSET)

        output = d.pop("output", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        _matched_rules = d.pop("matchedRules", UNSET)
        matched_rules: (
            list[EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItem]
            | Unset
        ) = UNSET
        if _matched_rules is not UNSET:
            matched_rules = []
            for matched_rules_item_data in _matched_rules:
                matched_rules_item = EvaluateDecisionResponse200EvaluatedDecisionsItemMatchedRulesItem.from_dict(
                    matched_rules_item_data
                )

                matched_rules.append(matched_rules_item)

        _evaluated_inputs = d.pop("evaluatedInputs", UNSET)
        evaluated_inputs: (
            list[EvaluateDecisionResponse200EvaluatedDecisionsItemEvaluatedInputsItem]
            | Unset
        ) = UNSET
        if _evaluated_inputs is not UNSET:
            evaluated_inputs = []
            for evaluated_inputs_item_data in _evaluated_inputs:
                evaluated_inputs_item = EvaluateDecisionResponse200EvaluatedDecisionsItemEvaluatedInputsItem.from_dict(
                    evaluated_inputs_item_data
                )

                evaluated_inputs.append(evaluated_inputs_item)

        decision_definition_key = lift_decision_definition_key(_val) if (_val := d.pop("decisionDefinitionKey", UNSET)) is not UNSET else UNSET

        decision_evaluation_instance_key = lift_decision_evaluation_instance_key(_val) if (_val := d.pop("decisionEvaluationInstanceKey", UNSET)) is not UNSET else UNSET

        evaluate_decision_response_200_evaluated_decisions_item = cls(
            decision_definition_id=decision_definition_id,
            decision_definition_name=decision_definition_name,
            decision_definition_version=decision_definition_version,
            decision_definition_type=decision_definition_type,
            output=output,
            tenant_id=tenant_id,
            matched_rules=matched_rules,
            evaluated_inputs=evaluated_inputs,
            decision_definition_key=decision_definition_key,
            decision_evaluation_instance_key=decision_evaluation_instance_key,
        )

        evaluate_decision_response_200_evaluated_decisions_item.additional_properties = d
        return evaluate_decision_response_200_evaluated_decisions_item

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
