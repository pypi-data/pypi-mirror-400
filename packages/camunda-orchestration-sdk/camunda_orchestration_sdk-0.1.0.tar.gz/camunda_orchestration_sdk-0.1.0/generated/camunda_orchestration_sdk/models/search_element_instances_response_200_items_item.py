from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.search_element_instances_response_200_items_item_state import (
    SearchElementInstancesResponse200ItemsItemState,
)
from ..models.search_element_instances_response_200_items_item_type import (
    SearchElementInstancesResponse200ItemsItemType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchElementInstancesResponse200ItemsItem")


@_attrs_define
class SearchElementInstancesResponse200ItemsItem:
    """
    Attributes:
        process_definition_id (str): The process definition ID associated to this element instance. Example: new-
            account-onboarding-workflow.
        start_date (datetime.datetime): Date when element instance started.
        element_id (str): The element ID for this element instance. Example: Activity_106kosb.
        element_name (str): The element name for this element instance.
        type_ (SearchElementInstancesResponse200ItemsItemType): Type of element as defined set of values.
        state (SearchElementInstancesResponse200ItemsItemState): State of element instance as defined set of values.
        has_incident (bool): Shows whether this element instance has an incident. If true also an incidentKey is
            provided.
        tenant_id (str): The tenant ID of the incident. Example: customer-service.
        element_instance_key (str): The assigned key, which acts as a unique identifier for this element instance.
            Example: 2251799813686789.
        process_instance_key (str): The process instance key associated to this element instance. Example:
            2251799813690746.
        process_definition_key (str): The process definition key associated to this element instance. Example:
            2251799813686749.
        end_date (datetime.datetime | Unset): Date when element instance finished.
        incident_key (str | Unset): Incident key associated with this element instance. Example: 2251799813689432.
    """

    process_definition_id: ProcessDefinitionId
    start_date: datetime.datetime
    element_id: ElementId
    element_name: str
    type_: SearchElementInstancesResponse200ItemsItemType
    state: SearchElementInstancesResponse200ItemsItemState
    has_incident: bool
    tenant_id: TenantId
    element_instance_key: ElementInstanceKey
    process_instance_key: ProcessInstanceKey
    process_definition_key: ProcessDefinitionKey
    end_date: datetime.datetime | Unset = UNSET
    incident_key: IncidentKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition_id = self.process_definition_id

        start_date = self.start_date.isoformat()

        element_id = self.element_id

        element_name = self.element_name

        type_ = self.type_.value

        state = self.state.value

        has_incident = self.has_incident

        tenant_id = self.tenant_id

        element_instance_key = self.element_instance_key

        process_instance_key = self.process_instance_key

        process_definition_key = self.process_definition_key

        end_date: str | Unset = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        incident_key = self.incident_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "processDefinitionId": process_definition_id,
                "startDate": start_date,
                "elementId": element_id,
                "elementName": element_name,
                "type": type_,
                "state": state,
                "hasIncident": has_incident,
                "tenantId": tenant_id,
                "elementInstanceKey": element_instance_key,
                "processInstanceKey": process_instance_key,
                "processDefinitionKey": process_definition_key,
            }
        )
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if incident_key is not UNSET:
            field_dict["incidentKey"] = incident_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        process_definition_id = lift_process_definition_id(d.pop("processDefinitionId"))

        start_date = isoparse(d.pop("startDate"))

        element_id = lift_element_id(d.pop("elementId"))

        element_name = d.pop("elementName")

        type_ = SearchElementInstancesResponse200ItemsItemType(d.pop("type"))

        state = SearchElementInstancesResponse200ItemsItemState(d.pop("state"))

        has_incident = d.pop("hasIncident")

        tenant_id = lift_tenant_id(d.pop("tenantId"))

        element_instance_key = lift_element_instance_key(d.pop("elementInstanceKey"))

        process_instance_key = lift_process_instance_key(d.pop("processInstanceKey"))

        process_definition_key = lift_process_definition_key(d.pop("processDefinitionKey"))

        _end_date = d.pop("endDate", UNSET)
        end_date: datetime.datetime | Unset
        if isinstance(_end_date, Unset):
            end_date = UNSET
        else:
            end_date = isoparse(_end_date)

        incident_key = lift_incident_key(_val) if (_val := d.pop("incidentKey", UNSET)) is not UNSET else UNSET

        search_element_instances_response_200_items_item = cls(
            process_definition_id=process_definition_id,
            start_date=start_date,
            element_id=element_id,
            element_name=element_name,
            type_=type_,
            state=state,
            has_incident=has_incident,
            tenant_id=tenant_id,
            element_instance_key=element_instance_key,
            process_instance_key=process_instance_key,
            process_definition_key=process_definition_key,
            end_date=end_date,
            incident_key=incident_key,
        )

        search_element_instances_response_200_items_item.additional_properties = d
        return search_element_instances_response_200_items_item

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
