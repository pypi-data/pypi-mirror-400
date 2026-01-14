from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.search_decision_instances_response_200_items_item_decision_definition_type import (
    SearchDecisionInstancesResponse200ItemsItemDecisionDefinitionType,
)
from ..models.search_decision_instances_response_200_items_item_state import (
    SearchDecisionInstancesResponse200ItemsItemState,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchDecisionInstancesResponse200ItemsItem")


@_attrs_define
class SearchDecisionInstancesResponse200ItemsItem:
    """
    Attributes:
        decision_evaluation_instance_key (str | Unset): System-generated key for a decision evaluation instance.
            Example: 2251799813684367.
        state (SearchDecisionInstancesResponse200ItemsItemState | Unset): The state of the decision instance.
        evaluation_date (datetime.datetime | Unset): The evaluation date of the decision instance.
        evaluation_failure (str | Unset): The evaluation failure of the decision instance.
        decision_definition_id (str | Unset): The ID of the DMN decision. Example: new-hire-onboarding-workflow.
        decision_definition_name (str | Unset): The name of the DMN decision.
        decision_definition_version (int | Unset): The version of the decision.
        decision_definition_type (SearchDecisionInstancesResponse200ItemsItemDecisionDefinitionType | Unset): The type
            of the decision.
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
    """

    decision_evaluation_instance_key: DecisionEvaluationInstanceKey | Unset = UNSET
    state: SearchDecisionInstancesResponse200ItemsItemState | Unset = UNSET
    evaluation_date: datetime.datetime | Unset = UNSET
    evaluation_failure: str | Unset = UNSET
    decision_definition_id: DecisionDefinitionId | Unset = UNSET
    decision_definition_name: str | Unset = UNSET
    decision_definition_version: int | Unset = UNSET
    decision_definition_type: (
        SearchDecisionInstancesResponse200ItemsItemDecisionDefinitionType | Unset
    ) = UNSET
    result: str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    decision_evaluation_key: DecisionEvaluationKey | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    decision_definition_key: DecisionDefinitionKey | Unset = UNSET
    element_instance_key: ElementInstanceKey | Unset = UNSET
    root_decision_definition_key: DecisionDefinitionKey | Unset = UNSET
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        decision_evaluation_instance_key = lift_decision_evaluation_instance_key(_val) if (_val := d.pop("decisionEvaluationInstanceKey", UNSET)) is not UNSET else UNSET

        _state = d.pop("state", UNSET)
        state: SearchDecisionInstancesResponse200ItemsItemState | Unset
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = SearchDecisionInstancesResponse200ItemsItemState(_state)

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
            SearchDecisionInstancesResponse200ItemsItemDecisionDefinitionType | Unset
        )
        if isinstance(_decision_definition_type, Unset):
            decision_definition_type = UNSET
        else:
            decision_definition_type = (
                SearchDecisionInstancesResponse200ItemsItemDecisionDefinitionType(
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

        search_decision_instances_response_200_items_item = cls(
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
        )

        search_decision_instances_response_200_items_item.additional_properties = d
        return search_decision_instances_response_200_items_item

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
