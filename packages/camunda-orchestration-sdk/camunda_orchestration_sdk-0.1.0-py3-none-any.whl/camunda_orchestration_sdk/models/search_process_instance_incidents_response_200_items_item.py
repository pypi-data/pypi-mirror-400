from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_process_instance_incidents_response_200_items_item_error_type import (
        SearchProcessInstanceIncidentsResponse200ItemsItemErrorType,
    )
    from ..models.search_process_instance_incidents_response_200_items_item_state import (
        SearchProcessInstanceIncidentsResponse200ItemsItemState,
    )


T = TypeVar("T", bound="SearchProcessInstanceIncidentsResponse200ItemsItem")


@_attrs_define
class SearchProcessInstanceIncidentsResponse200ItemsItem:
    """
    Attributes:
        process_definition_id (str | Unset): The process definition ID associated to this incident. Example: new-
            account-onboarding-workflow.
        error_type (SearchProcessInstanceIncidentsResponse200ItemsItemErrorType | Unset):
        error_message (str | Unset): Error message which describes the error in more detail.
        element_id (str | Unset): The element ID associated to this incident. Example: Activity_106kosb.
        creation_time (datetime.datetime | Unset):
        state (SearchProcessInstanceIncidentsResponse200ItemsItemState | Unset):
        tenant_id (str | Unset): The tenant ID of the incident. Example: customer-service.
        incident_key (str | Unset): The assigned key, which acts as a unique identifier for this incident. Example:
            2251799813689432.
        process_definition_key (str | Unset): The process definition key associated to this incident. Example:
            2251799813686749.
        process_instance_key (str | Unset): The process instance key associated to this incident. Example:
            2251799813690746.
        element_instance_key (str | Unset): The element instance key associated to this incident. Example:
            2251799813686789.
        job_key (str | Unset): The job key, if exists, associated with this incident. Example: 2251799813653498.
    """

    process_definition_id: ProcessDefinitionId | Unset = UNSET
    error_type: SearchProcessInstanceIncidentsResponse200ItemsItemErrorType | Unset = (
        UNSET
    )
    error_message: str | Unset = UNSET
    element_id: ElementId | Unset = UNSET
    creation_time: datetime.datetime | Unset = UNSET
    state: SearchProcessInstanceIncidentsResponse200ItemsItemState | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    incident_key: IncidentKey | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    element_instance_key: ElementInstanceKey | Unset = UNSET
    job_key: JobKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition_id = self.process_definition_id

        error_type: dict[str, Any] | Unset = UNSET
        if not isinstance(self.error_type, Unset):
            error_type = self.error_type.to_dict()

        error_message = self.error_message

        element_id = self.element_id

        creation_time: str | Unset = UNSET
        if not isinstance(self.creation_time, Unset):
            creation_time = self.creation_time.isoformat()

        state: dict[str, Any] | Unset = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.to_dict()

        tenant_id = self.tenant_id

        incident_key = self.incident_key

        process_definition_key = self.process_definition_key

        process_instance_key = self.process_instance_key

        element_instance_key = self.element_instance_key

        job_key = self.job_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if error_type is not UNSET:
            field_dict["errorType"] = error_type
        if error_message is not UNSET:
            field_dict["errorMessage"] = error_message
        if element_id is not UNSET:
            field_dict["elementId"] = element_id
        if creation_time is not UNSET:
            field_dict["creationTime"] = creation_time
        if state is not UNSET:
            field_dict["state"] = state
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if incident_key is not UNSET:
            field_dict["incidentKey"] = incident_key
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if element_instance_key is not UNSET:
            field_dict["elementInstanceKey"] = element_instance_key
        if job_key is not UNSET:
            field_dict["jobKey"] = job_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_process_instance_incidents_response_200_items_item_error_type import (
            SearchProcessInstanceIncidentsResponse200ItemsItemErrorType,
        )
        from ..models.search_process_instance_incidents_response_200_items_item_state import (
            SearchProcessInstanceIncidentsResponse200ItemsItemState,
        )

        d = dict(src_dict)
        process_definition_id = lift_process_definition_id(_val) if (_val := d.pop("processDefinitionId", UNSET)) is not UNSET else UNSET

        _error_type = d.pop("errorType", UNSET)
        error_type: SearchProcessInstanceIncidentsResponse200ItemsItemErrorType | Unset
        if isinstance(_error_type, Unset):
            error_type = UNSET
        else:
            error_type = (
                SearchProcessInstanceIncidentsResponse200ItemsItemErrorType.from_dict(
                    _error_type
                )
            )

        error_message = d.pop("errorMessage", UNSET)

        element_id = lift_element_id(_val) if (_val := d.pop("elementId", UNSET)) is not UNSET else UNSET

        _creation_time = d.pop("creationTime", UNSET)
        creation_time: datetime.datetime | Unset
        if isinstance(_creation_time, Unset):
            creation_time = UNSET
        else:
            creation_time = isoparse(_creation_time)

        _state = d.pop("state", UNSET)
        state: SearchProcessInstanceIncidentsResponse200ItemsItemState | Unset
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = SearchProcessInstanceIncidentsResponse200ItemsItemState.from_dict(
                _state
            )

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        incident_key = lift_incident_key(_val) if (_val := d.pop("incidentKey", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        element_instance_key = lift_element_instance_key(_val) if (_val := d.pop("elementInstanceKey", UNSET)) is not UNSET else UNSET

        job_key = lift_job_key(_val) if (_val := d.pop("jobKey", UNSET)) is not UNSET else UNSET

        search_process_instance_incidents_response_200_items_item = cls(
            process_definition_id=process_definition_id,
            error_type=error_type,
            error_message=error_message,
            element_id=element_id,
            creation_time=creation_time,
            state=state,
            tenant_id=tenant_id,
            incident_key=incident_key,
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
            element_instance_key=element_instance_key,
            job_key=job_key,
        )

        search_process_instance_incidents_response_200_items_item.additional_properties = d
        return search_process_instance_incidents_response_200_items_item

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
