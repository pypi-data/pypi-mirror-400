from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.search_decision_instances_data_filter_decision_definition_type import (
    SearchDecisionInstancesDataFilterDecisionDefinitionType,
)
from ..models.state_exactmatch_2 import StateExactmatch2
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.decisiondefinitionkey_advancedfilter import (
        DecisiondefinitionkeyAdvancedfilter,
    )
    from ..models.decisionevaluationinstancekey_advancedfilter import (
        DecisionevaluationinstancekeyAdvancedfilter,
    )
    from ..models.elementinstancekey_advancedfilter import (
        ElementinstancekeyAdvancedfilter,
    )
    from ..models.state_advancedfilter_2 import StateAdvancedfilter2
    from ..models.timestamp_advancedfilter import TimestampAdvancedfilter


T = TypeVar("T", bound="SearchDecisionInstancesDataFilter")


@_attrs_define
class SearchDecisionInstancesDataFilter:
    """The decision instance search filters.

    Attributes:
        decision_evaluation_instance_key (DecisionevaluationinstancekeyAdvancedfilter | str | Unset):
        state (StateAdvancedfilter2 | StateExactmatch2 | Unset):
        evaluation_failure (str | Unset): The evaluation failure of the decision instance.
        evaluation_date (datetime.datetime | TimestampAdvancedfilter | Unset):
        decision_definition_id (str | Unset): The ID of the DMN decision. Example: new-hire-onboarding-workflow.
        decision_definition_name (str | Unset): The name of the DMN decision.
        decision_definition_version (int | Unset): The version of the decision.
        decision_definition_type (SearchDecisionInstancesDataFilterDecisionDefinitionType | Unset): The type of the
            decision.
        tenant_id (str | Unset): The tenant ID of the decision instance. Example: customer-service.
        decision_evaluation_key (str | Unset): The key of the parent decision evaluation. Note that this is not the
            identifier of an individual decision instance; the `decisionEvaluationInstanceKey` is the identifier for a
            decision instance.
             Example: 2251792362345323.
        process_definition_key (str | Unset): The key of the process definition. Example: 2251799813686749.
        process_instance_key (str | Unset): The key of the process instance. Example: 2251799813690746.
        decision_definition_key (DecisiondefinitionkeyAdvancedfilter | str | Unset):
        element_instance_key (ElementinstancekeyAdvancedfilter | str | Unset):
        root_decision_definition_key (DecisiondefinitionkeyAdvancedfilter | str | Unset):
    """

    decision_evaluation_instance_key: (
        DecisionevaluationinstancekeyAdvancedfilter | str | Unset
    ) = UNSET
    state: StateAdvancedfilter2 | StateExactmatch2 | Unset = UNSET
    evaluation_failure: str | Unset = UNSET
    evaluation_date: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    decision_definition_id: DecisionDefinitionId | Unset = UNSET
    decision_definition_name: str | Unset = UNSET
    decision_definition_version: int | Unset = UNSET
    decision_definition_type: (
        SearchDecisionInstancesDataFilterDecisionDefinitionType | Unset
    ) = UNSET
    tenant_id: TenantId | Unset = UNSET
    decision_evaluation_key: DecisionEvaluationKey | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    decision_definition_key: DecisiondefinitionkeyAdvancedfilter | str | Unset = UNSET
    element_instance_key: ElementinstancekeyAdvancedfilter | str | Unset = UNSET
    root_decision_definition_key: DecisiondefinitionkeyAdvancedfilter | str | Unset = (
        UNSET
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.decisiondefinitionkey_advancedfilter import (
            DecisiondefinitionkeyAdvancedfilter,
        )
        from ..models.decisionevaluationinstancekey_advancedfilter import (
            DecisionevaluationinstancekeyAdvancedfilter,
        )
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )

        decision_evaluation_instance_key: dict[str, Any] | str | Unset
        if isinstance(self.decision_evaluation_instance_key, Unset):
            decision_evaluation_instance_key = UNSET
        elif isinstance(
            self.decision_evaluation_instance_key,
            DecisionevaluationinstancekeyAdvancedfilter,
        ):
            decision_evaluation_instance_key = (
                self.decision_evaluation_instance_key.to_dict()
            )
        else:
            decision_evaluation_instance_key = self.decision_evaluation_instance_key

        state: dict[str, Any] | str | Unset
        if isinstance(self.state, Unset):
            state = UNSET
        elif isinstance(self.state, StateExactmatch2):
            state = self.state.value
        else:
            state = self.state.to_dict()

        evaluation_failure = self.evaluation_failure

        evaluation_date: dict[str, Any] | str | Unset
        if isinstance(self.evaluation_date, Unset):
            evaluation_date = UNSET
        elif isinstance(self.evaluation_date, datetime.datetime):
            evaluation_date = self.evaluation_date.isoformat()
        else:
            evaluation_date = self.evaluation_date.to_dict()

        decision_definition_id = self.decision_definition_id

        decision_definition_name = self.decision_definition_name

        decision_definition_version = self.decision_definition_version

        decision_definition_type: str | Unset = UNSET
        if not isinstance(self.decision_definition_type, Unset):
            decision_definition_type = self.decision_definition_type.value

        tenant_id = self.tenant_id

        decision_evaluation_key = self.decision_evaluation_key

        process_definition_key = self.process_definition_key

        process_instance_key = self.process_instance_key

        decision_definition_key: dict[str, Any] | str | Unset
        if isinstance(self.decision_definition_key, Unset):
            decision_definition_key = UNSET
        elif isinstance(
            self.decision_definition_key, DecisiondefinitionkeyAdvancedfilter
        ):
            decision_definition_key = self.decision_definition_key.to_dict()
        else:
            decision_definition_key = self.decision_definition_key

        element_instance_key: dict[str, Any] | str | Unset
        if isinstance(self.element_instance_key, Unset):
            element_instance_key = UNSET
        elif isinstance(self.element_instance_key, ElementinstancekeyAdvancedfilter):
            element_instance_key = self.element_instance_key.to_dict()
        else:
            element_instance_key = self.element_instance_key

        root_decision_definition_key: dict[str, Any] | str | Unset
        if isinstance(self.root_decision_definition_key, Unset):
            root_decision_definition_key = UNSET
        elif isinstance(
            self.root_decision_definition_key, DecisiondefinitionkeyAdvancedfilter
        ):
            root_decision_definition_key = self.root_decision_definition_key.to_dict()
        else:
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
        if evaluation_failure is not UNSET:
            field_dict["evaluationFailure"] = evaluation_failure
        if evaluation_date is not UNSET:
            field_dict["evaluationDate"] = evaluation_date
        if decision_definition_id is not UNSET:
            field_dict["decisionDefinitionId"] = decision_definition_id
        if decision_definition_name is not UNSET:
            field_dict["decisionDefinitionName"] = decision_definition_name
        if decision_definition_version is not UNSET:
            field_dict["decisionDefinitionVersion"] = decision_definition_version
        if decision_definition_type is not UNSET:
            field_dict["decisionDefinitionType"] = decision_definition_type
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
        from ..models.decisiondefinitionkey_advancedfilter import (
            DecisiondefinitionkeyAdvancedfilter,
        )
        from ..models.decisionevaluationinstancekey_advancedfilter import (
            DecisionevaluationinstancekeyAdvancedfilter,
        )
        from ..models.elementinstancekey_advancedfilter import (
            ElementinstancekeyAdvancedfilter,
        )
        from ..models.state_advancedfilter_2 import StateAdvancedfilter2
        from ..models.timestamp_advancedfilter import TimestampAdvancedfilter

        d = dict(src_dict)

        def _parse_decision_evaluation_instance_key(
            data: object,
        ) -> DecisionevaluationinstancekeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                decision_evaluation_instance_key_type_1 = (
                    DecisionevaluationinstancekeyAdvancedfilter.from_dict(data)
                )

                return decision_evaluation_instance_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DecisionevaluationinstancekeyAdvancedfilter | str | Unset, data)

        decision_evaluation_instance_key = _parse_decision_evaluation_instance_key(
            d.pop("decisionEvaluationInstanceKey", UNSET)
        )

        def _parse_state(
            data: object,
        ) -> StateAdvancedfilter2 | StateExactmatch2 | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                state_type_0 = StateExactmatch2(data)

                return state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            state_type_1 = StateAdvancedfilter2.from_dict(data)

            return state_type_1

        state = _parse_state(d.pop("state", UNSET))

        evaluation_failure = d.pop("evaluationFailure", UNSET)

        def _parse_evaluation_date(
            data: object,
        ) -> datetime.datetime | TimestampAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                evaluation_date_type_0 = isoparse(data)

                return evaluation_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            evaluation_date_type_1 = TimestampAdvancedfilter.from_dict(data)

            return evaluation_date_type_1

        evaluation_date = _parse_evaluation_date(d.pop("evaluationDate", UNSET))

        decision_definition_id = lift_decision_definition_id(_val) if (_val := d.pop("decisionDefinitionId", UNSET)) is not UNSET else UNSET

        decision_definition_name = d.pop("decisionDefinitionName", UNSET)

        decision_definition_version = d.pop("decisionDefinitionVersion", UNSET)

        _decision_definition_type = d.pop("decisionDefinitionType", UNSET)
        decision_definition_type: (
            SearchDecisionInstancesDataFilterDecisionDefinitionType | Unset
        )
        if isinstance(_decision_definition_type, Unset):
            decision_definition_type = UNSET
        else:
            decision_definition_type = (
                SearchDecisionInstancesDataFilterDecisionDefinitionType(
                    _decision_definition_type
                )
            )

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        decision_evaluation_key = lift_decision_evaluation_key(_val) if (_val := d.pop("decisionEvaluationKey", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        def _parse_decision_definition_key(
            data: object,
        ) -> DecisiondefinitionkeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                decision_definition_key_type_1 = (
                    DecisiondefinitionkeyAdvancedfilter.from_dict(data)
                )

                return decision_definition_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DecisiondefinitionkeyAdvancedfilter | str | Unset, data)

        decision_definition_key = _parse_decision_definition_key(
            d.pop("decisionDefinitionKey", UNSET)
        )

        def _parse_element_instance_key(
            data: object,
        ) -> ElementinstancekeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                element_instance_key_type_1 = (
                    ElementinstancekeyAdvancedfilter.from_dict(data)
                )

                return element_instance_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ElementinstancekeyAdvancedfilter | str | Unset, data)

        element_instance_key = _parse_element_instance_key(
            d.pop("elementInstanceKey", UNSET)
        )

        def _parse_root_decision_definition_key(
            data: object,
        ) -> DecisiondefinitionkeyAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                root_decision_definition_key_type_1 = (
                    DecisiondefinitionkeyAdvancedfilter.from_dict(data)
                )

                return root_decision_definition_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DecisiondefinitionkeyAdvancedfilter | str | Unset, data)

        root_decision_definition_key = _parse_root_decision_definition_key(
            d.pop("rootDecisionDefinitionKey", UNSET)
        )

        search_decision_instances_data_filter = cls(
            decision_evaluation_instance_key=decision_evaluation_instance_key,
            state=state,
            evaluation_failure=evaluation_failure,
            evaluation_date=evaluation_date,
            decision_definition_id=decision_definition_id,
            decision_definition_name=decision_definition_name,
            decision_definition_version=decision_definition_version,
            decision_definition_type=decision_definition_type,
            tenant_id=tenant_id,
            decision_evaluation_key=decision_evaluation_key,
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
            decision_definition_key=decision_definition_key,
            element_instance_key=element_instance_key,
            root_decision_definition_key=root_decision_definition_key,
        )

        search_decision_instances_data_filter.additional_properties = d
        return search_decision_instances_data_filter

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
