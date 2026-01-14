from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.get_decision_instance_response_200_decision_definition_type import (
    GetDecisionInstanceResponse200DecisionDefinitionType,
)
from ..models.get_decision_instance_response_200_state import (
    GetDecisionInstanceResponse200State,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_decision_instance_response_200_evaluated_inputs_item import (
        GetDecisionInstanceResponse200EvaluatedInputsItem,
    )
    from ..models.get_decision_instance_response_200_matched_rules_item import (
        GetDecisionInstanceResponse200MatchedRulesItem,
    )


T = TypeVar("T", bound="GetDecisionInstanceResponse200")


@_attrs_define
class GetDecisionInstanceResponse200:
    """
    Attributes:
        decision_evaluation_instance_key (str | Unset): System-generated key for a decision evaluation instance.
            Example: 2251799813684367.
        state (GetDecisionInstanceResponse200State | Unset): The state of the decision instance.
        evaluation_date (datetime.datetime | Unset): The evaluation date of the decision instance.
        evaluation_failure (str | Unset): The evaluation failure of the decision instance.
        decision_definition_id (str | Unset): The ID of the DMN decision. Example: new-hire-onboarding-workflow.
        decision_definition_name (str | Unset): The name of the DMN decision.
        decision_definition_version (int | Unset): The version of the decision.
        decision_definition_type (GetDecisionInstanceResponse200DecisionDefinitionType | Unset): The type of the
            decision.
        result (str | Unset): The result of the decision instance.
        tenant_id (str | Unset): The tenant ID of the decision instance. Example: customer-service.
        decision_evaluation_key (str | Unset): The key of the decision evaluation where this instance was created.
            Example: 2251792362345323.
        process_definition_key (str | Unset): The key of the process definition. Example: 2251799813686749.
        process_instance_key (str | Unset): The key of the process instance. Example: 2251799813690746.
        decision_definition_key (str | Unset): The key of the decision. Example: 2251799813326547.
        element_instance_key (str | Unset): The key of the element instance this decision instance is linked to.
            Example: 2251799813686789.
        root_decision_definition_key (str | Unset): The key of the root decision definition. Example: 2251799813326547.
        evaluated_inputs (list[GetDecisionInstanceResponse200EvaluatedInputsItem] | Unset): The evaluated inputs of the
            decision instance.
        matched_rules (list[GetDecisionInstanceResponse200MatchedRulesItem] | Unset): The matched rules of the decision
            instance.
    """

    decision_evaluation_instance_key: DecisionEvaluationInstanceKey | Unset = UNSET
    state: GetDecisionInstanceResponse200State | Unset = UNSET
    evaluation_date: datetime.datetime | Unset = UNSET
    evaluation_failure: str | Unset = UNSET
    decision_definition_id: DecisionDefinitionId | Unset = UNSET
    decision_definition_name: str | Unset = UNSET
    decision_definition_version: int | Unset = UNSET
    decision_definition_type: (
        GetDecisionInstanceResponse200DecisionDefinitionType | Unset
    ) = UNSET
    result: str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    decision_evaluation_key: DecisionEvaluationKey | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    decision_definition_key: DecisionDefinitionKey | Unset = UNSET
    element_instance_key: ElementInstanceKey | Unset = UNSET
    root_decision_definition_key: DecisionDefinitionKey | Unset = UNSET
    evaluated_inputs: (
        list[GetDecisionInstanceResponse200EvaluatedInputsItem] | Unset
    ) = UNSET
    matched_rules: list[GetDecisionInstanceResponse200MatchedRulesItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        decision_evaluation_instance_key = self.decision_evaluation_instance_key

        state: str | Unset = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        evaluation_date: str | Unset = UNSET
        if not isinstance(self.evaluation_date, Unset):
            evaluation_date = self.evaluation_date.isoformat()

        evaluation_failure = self.evaluation_failure

        decision_definition_id = self.decision_definition_id

        decision_definition_name = self.decision_definition_name

        decision_definition_version = self.decision_definition_version

        decision_definition_type: str | Unset = UNSET
        if not isinstance(self.decision_definition_type, Unset):
            decision_definition_type = self.decision_definition_type.value

        result = self.result

        tenant_id = self.tenant_id

        decision_evaluation_key = self.decision_evaluation_key

        process_definition_key = self.process_definition_key

        process_instance_key = self.process_instance_key

        decision_definition_key = self.decision_definition_key

        element_instance_key = self.element_instance_key

        root_decision_definition_key = self.root_decision_definition_key

        evaluated_inputs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.evaluated_inputs, Unset):
            evaluated_inputs = []
            for evaluated_inputs_item_data in self.evaluated_inputs:
                evaluated_inputs_item = evaluated_inputs_item_data.to_dict()
                evaluated_inputs.append(evaluated_inputs_item)

        matched_rules: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.matched_rules, Unset):
            matched_rules = []
            for matched_rules_item_data in self.matched_rules:
                matched_rules_item = matched_rules_item_data.to_dict()
                matched_rules.append(matched_rules_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if decision_evaluation_instance_key is not UNSET:
            field_dict["decisionEvaluationInstanceKey"] = (
                decision_evaluation_instance_key
            )
        if state is not UNSET:
            field_dict["state"] = state
        if evaluation_date is not UNSET:
            field_dict["evaluationDate"] = evaluation_date
        if evaluation_failure is not UNSET:
            field_dict["evaluationFailure"] = evaluation_failure
        if decision_definition_id is not UNSET:
            field_dict["decisionDefinitionId"] = decision_definition_id
        if decision_definition_name is not UNSET:
            field_dict["decisionDefinitionName"] = decision_definition_name
        if decision_definition_version is not UNSET:
            field_dict["decisionDefinitionVersion"] = decision_definition_version
        if decision_definition_type is not UNSET:
            field_dict["decisionDefinitionType"] = decision_definition_type
        if result is not UNSET:
            field_dict["result"] = result
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if decision_evaluation_key is not UNSET:
            field_dict["decisionEvaluationKey"] = decision_evaluation_key
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if decision_definition_key is not UNSET:
            field_dict["decisionDefinitionKey"] = decision_definition_key
        if element_instance_key is not UNSET:
            field_dict["elementInstanceKey"] = element_instance_key
        if root_decision_definition_key is not UNSET:
            field_dict["rootDecisionDefinitionKey"] = root_decision_definition_key
        if evaluated_inputs is not UNSET:
            field_dict["evaluatedInputs"] = evaluated_inputs
        if matched_rules is not UNSET:
            field_dict["matchedRules"] = matched_rules

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_decision_instance_response_200_evaluated_inputs_item import (
            GetDecisionInstanceResponse200EvaluatedInputsItem,
        )
        from ..models.get_decision_instance_response_200_matched_rules_item import (
            GetDecisionInstanceResponse200MatchedRulesItem,
        )

        d = dict(src_dict)
        decision_evaluation_instance_key = lift_decision_evaluation_instance_key(_val) if (_val := d.pop("decisionEvaluationInstanceKey", UNSET)) is not UNSET else UNSET

        _state = d.pop("state", UNSET)
        state: GetDecisionInstanceResponse200State | Unset
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = GetDecisionInstanceResponse200State(_state)

        _evaluation_date = d.pop("evaluationDate", UNSET)
        evaluation_date: datetime.datetime | Unset
        if isinstance(_evaluation_date, Unset):
            evaluation_date = UNSET
        else:
            evaluation_date = isoparse(_evaluation_date)

        evaluation_failure = d.pop("evaluationFailure", UNSET)

        decision_definition_id = lift_decision_definition_id(_val) if (_val := d.pop("decisionDefinitionId", UNSET)) is not UNSET else UNSET

        decision_definition_name = d.pop("decisionDefinitionName", UNSET)

        decision_definition_version = d.pop("decisionDefinitionVersion", UNSET)

        _decision_definition_type = d.pop("decisionDefinitionType", UNSET)
        decision_definition_type: (
            GetDecisionInstanceResponse200DecisionDefinitionType | Unset
        )
        if isinstance(_decision_definition_type, Unset):
            decision_definition_type = UNSET
        else:
            decision_definition_type = (
                GetDecisionInstanceResponse200DecisionDefinitionType(
                    _decision_definition_type
                )
            )

        result = d.pop("result", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        decision_evaluation_key = lift_decision_evaluation_key(_val) if (_val := d.pop("decisionEvaluationKey", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        decision_definition_key = lift_decision_definition_key(_val) if (_val := d.pop("decisionDefinitionKey", UNSET)) is not UNSET else UNSET

        element_instance_key = lift_element_instance_key(_val) if (_val := d.pop("elementInstanceKey", UNSET)) is not UNSET else UNSET

        root_decision_definition_key = d.pop("rootDecisionDefinitionKey", UNSET)

        _evaluated_inputs = d.pop("evaluatedInputs", UNSET)
        evaluated_inputs: (
            list[GetDecisionInstanceResponse200EvaluatedInputsItem] | Unset
        ) = UNSET
        if _evaluated_inputs is not UNSET:
            evaluated_inputs = []
            for evaluated_inputs_item_data in _evaluated_inputs:
                evaluated_inputs_item = (
                    GetDecisionInstanceResponse200EvaluatedInputsItem.from_dict(
                        evaluated_inputs_item_data
                    )
                )

                evaluated_inputs.append(evaluated_inputs_item)

        _matched_rules = d.pop("matchedRules", UNSET)
        matched_rules: list[GetDecisionInstanceResponse200MatchedRulesItem] | Unset = (
            UNSET
        )
        if _matched_rules is not UNSET:
            matched_rules = []
            for matched_rules_item_data in _matched_rules:
                matched_rules_item = (
                    GetDecisionInstanceResponse200MatchedRulesItem.from_dict(
                        matched_rules_item_data
                    )
                )

                matched_rules.append(matched_rules_item)

        get_decision_instance_response_200 = cls(
            decision_evaluation_instance_key=decision_evaluation_instance_key,
            state=state,
            evaluation_date=evaluation_date,
            evaluation_failure=evaluation_failure,
            decision_definition_id=decision_definition_id,
            decision_definition_name=decision_definition_name,
            decision_definition_version=decision_definition_version,
            decision_definition_type=decision_definition_type,
            result=result,
            tenant_id=tenant_id,
            decision_evaluation_key=decision_evaluation_key,
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
            decision_definition_key=decision_definition_key,
            element_instance_key=element_instance_key,
            root_decision_definition_key=root_decision_definition_key,
            evaluated_inputs=evaluated_inputs,
            matched_rules=matched_rules,
        )

        get_decision_instance_response_200.additional_properties = d
        return get_decision_instance_response_200

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
