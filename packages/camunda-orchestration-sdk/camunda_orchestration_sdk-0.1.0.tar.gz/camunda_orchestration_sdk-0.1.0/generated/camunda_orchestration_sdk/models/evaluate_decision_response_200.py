from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.evaluate_decision_response_200_evaluated_decisions_item import (
        EvaluateDecisionResponse200EvaluatedDecisionsItem,
    )


T = TypeVar("T", bound="EvaluateDecisionResponse200")


@_attrs_define
class EvaluateDecisionResponse200:
    """
    Attributes:
        decision_definition_id (str): The ID of the decision which was evaluated. Example: new-hire-onboarding-workflow.
        decision_definition_name (str): The name of the decision which was evaluated.
        decision_definition_version (int): The version of the decision which was evaluated.
        decision_requirements_id (str): The ID of the decision requirements graph that the decision which was evaluated
            is part of.
        output (str): JSON document that will instantiate the result of the decision which was evaluated.
        failed_decision_definition_id (str): The ID of the decision which failed during evaluation. Example: new-hire-
            onboarding-workflow.
        failure_message (str): Message describing why the decision which was evaluated failed.
        tenant_id (str): The tenant ID of the evaluated decision. Example: customer-service.
        decision_definition_key (str): The unique key identifying the decision which was evaluated. Example:
            2251799813326547.
        decision_requirements_key (str): The unique key identifying the decision requirements graph that the decision
            which was evaluated is part of. Example: 2251799813683346.
        decision_evaluation_key (str): The unique key identifying this decision evaluation. Example: 2251792362345323.
        evaluated_decisions (list[EvaluateDecisionResponse200EvaluatedDecisionsItem]): Decisions that were evaluated
            within the requested decision evaluation.
        decision_instance_key (str | Unset): Deprecated, please refer to `decisionEvaluationKey`. Example:
            22517998136843567.
    """

    decision_definition_id: DecisionDefinitionId
    decision_definition_name: str
    decision_definition_version: int
    decision_requirements_id: str
    output: str
    failed_decision_definition_id: DecisionDefinitionId
    failure_message: str
    tenant_id: TenantId
    decision_definition_key: DecisionDefinitionKey
    decision_requirements_key: DecisionRequirementsKey
    decision_evaluation_key: DecisionEvaluationKey
    evaluated_decisions: list[EvaluateDecisionResponse200EvaluatedDecisionsItem]
    decision_instance_key: DecisionInstanceKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        decision_definition_id = self.decision_definition_id

        decision_definition_name = self.decision_definition_name

        decision_definition_version = self.decision_definition_version

        decision_requirements_id = self.decision_requirements_id

        output = self.output

        failed_decision_definition_id = self.failed_decision_definition_id

        failure_message = self.failure_message

        tenant_id = self.tenant_id

        decision_definition_key = self.decision_definition_key

        decision_requirements_key = self.decision_requirements_key

        decision_evaluation_key = self.decision_evaluation_key

        evaluated_decisions = []
        for evaluated_decisions_item_data in self.evaluated_decisions:
            evaluated_decisions_item = evaluated_decisions_item_data.to_dict()
            evaluated_decisions.append(evaluated_decisions_item)

        decision_instance_key = self.decision_instance_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "decisionDefinitionId": decision_definition_id,
                "decisionDefinitionName": decision_definition_name,
                "decisionDefinitionVersion": decision_definition_version,
                "decisionRequirementsId": decision_requirements_id,
                "output": output,
                "failedDecisionDefinitionId": failed_decision_definition_id,
                "failureMessage": failure_message,
                "tenantId": tenant_id,
                "decisionDefinitionKey": decision_definition_key,
                "decisionRequirementsKey": decision_requirements_key,
                "decisionEvaluationKey": decision_evaluation_key,
                "evaluatedDecisions": evaluated_decisions,
            }
        )
        if decision_instance_key is not UNSET:
            field_dict["decisionInstanceKey"] = decision_instance_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.evaluate_decision_response_200_evaluated_decisions_item import (
            EvaluateDecisionResponse200EvaluatedDecisionsItem,
        )

        d = dict(src_dict)
        decision_definition_id = lift_decision_definition_id(d.pop("decisionDefinitionId"))

        decision_definition_name = d.pop("decisionDefinitionName")

        decision_definition_version = d.pop("decisionDefinitionVersion")

        decision_requirements_id = d.pop("decisionRequirementsId")

        output = d.pop("output")

        failed_decision_definition_id = d.pop("failedDecisionDefinitionId")

        failure_message = d.pop("failureMessage")

        tenant_id = lift_tenant_id(d.pop("tenantId"))

        decision_definition_key = lift_decision_definition_key(d.pop("decisionDefinitionKey"))

        decision_requirements_key = lift_decision_requirements_key(d.pop("decisionRequirementsKey"))

        decision_evaluation_key = lift_decision_evaluation_key(d.pop("decisionEvaluationKey"))

        evaluated_decisions = []
        _evaluated_decisions = d.pop("evaluatedDecisions")
        for evaluated_decisions_item_data in _evaluated_decisions:
            evaluated_decisions_item = (
                EvaluateDecisionResponse200EvaluatedDecisionsItem.from_dict(
                    evaluated_decisions_item_data
                )
            )

            evaluated_decisions.append(evaluated_decisions_item)

        decision_instance_key = lift_decision_instance_key(_val) if (_val := d.pop("decisionInstanceKey", UNSET)) is not UNSET else UNSET

        evaluate_decision_response_200 = cls(
            decision_definition_id=decision_definition_id,
            decision_definition_name=decision_definition_name,
            decision_definition_version=decision_definition_version,
            decision_requirements_id=decision_requirements_id,
            output=output,
            failed_decision_definition_id=failed_decision_definition_id,
            failure_message=failure_message,
            tenant_id=tenant_id,
            decision_definition_key=decision_definition_key,
            decision_requirements_key=decision_requirements_key,
            decision_evaluation_key=decision_evaluation_key,
            evaluated_decisions=evaluated_decisions,
            decision_instance_key=decision_instance_key,
        )

        evaluate_decision_response_200.additional_properties = d
        return evaluate_decision_response_200

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
