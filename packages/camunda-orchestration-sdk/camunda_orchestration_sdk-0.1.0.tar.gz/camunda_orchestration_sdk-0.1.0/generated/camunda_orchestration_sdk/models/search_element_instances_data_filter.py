from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.search_element_instances_data_filter_type import (
    SearchElementInstancesDataFilterType,
)
from ..models.state_exactmatch_3 import StateExactmatch3
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.state_advancedfilter_3 import StateAdvancedfilter3
    from ..models.timestamp_advancedfilter import TimestampAdvancedfilter


T = TypeVar("T", bound="SearchElementInstancesDataFilter")


@_attrs_define
class SearchElementInstancesDataFilter:
    """The element instance search filters.

    Attributes:
        process_definition_id (str | Unset): The process definition ID associated to this element instance. Example:
            new-account-onboarding-workflow.
        state (StateAdvancedfilter3 | StateExactmatch3 | Unset):
        type_ (SearchElementInstancesDataFilterType | Unset): Type of element as defined set of values.
        element_id (str | Unset): The element ID for this element instance. Example: Activity_106kosb.
        element_name (str | Unset): The element name. This only works for data created with 8.8 and onwards. Instances
            from prior versions don't contain this data and cannot be found.
        has_incident (bool | Unset): Shows whether this element instance has an incident related to.
        tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
        element_instance_key (str | Unset): The assigned key, which acts as a unique identifier for this element
            instance. Example: 2251799813686789.
        process_instance_key (str | Unset): The process instance key associated to this element instance. Example:
            2251799813690746.
        process_definition_key (str | Unset): The process definition key associated to this element instance. Example:
            2251799813686749.
        incident_key (str | Unset): The key of incident if field incident is true. Example: 2251799813689432.
        start_date (datetime.datetime | TimestampAdvancedfilter | Unset):
        end_date (datetime.datetime | TimestampAdvancedfilter | Unset):
        element_instance_scope_key (str | Unset): The scope key of this element instance. If provided with a process
            instance key it will return element instances that are immediate children of the process instance. If provided
            with an element instance key it will return element instances that are immediate children of the element
            instance.
    """

    process_definition_id: ProcessDefinitionId | Unset = UNSET
    state: StateAdvancedfilter3 | StateExactmatch3 | Unset = UNSET
    type_: SearchElementInstancesDataFilterType | Unset = UNSET
    element_id: ElementId | Unset = UNSET
    element_name: str | Unset = UNSET
    has_incident: bool | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    element_instance_key: ElementInstanceKey | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    incident_key: IncidentKey | Unset = UNSET
    start_date: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    end_date: datetime.datetime | TimestampAdvancedfilter | Unset = UNSET
    element_instance_scope_key: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition_id = self.process_definition_id

        state: dict[str, Any] | str | Unset
        if isinstance(self.state, Unset):
            state = UNSET
        elif isinstance(self.state, StateExactmatch3):
            state = self.state.value
        else:
            state = self.state.to_dict()

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        element_id = self.element_id

        element_name = self.element_name

        has_incident = self.has_incident

        tenant_id = self.tenant_id

        element_instance_key = self.element_instance_key

        process_instance_key = self.process_instance_key

        process_definition_key = self.process_definition_key

        incident_key = self.incident_key

        start_date: dict[str, Any] | str | Unset
        if isinstance(self.start_date, Unset):
            start_date = UNSET
        elif isinstance(self.start_date, datetime.datetime):
            start_date = self.start_date.isoformat()
        else:
            start_date = self.start_date.to_dict()

        end_date: dict[str, Any] | str | Unset
        if isinstance(self.end_date, Unset):
            end_date = UNSET
        elif isinstance(self.end_date, datetime.datetime):
            end_date = self.end_date.isoformat()
        else:
            end_date = self.end_date.to_dict()

        element_instance_scope_key: str | Unset
        if isinstance(self.element_instance_scope_key, Unset):
            element_instance_scope_key = UNSET
        else:
            element_instance_scope_key = self.element_instance_scope_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if state is not UNSET:
            field_dict["state"] = state
        if type_ is not UNSET:
            field_dict["type"] = type_
        if element_id is not UNSET:
            field_dict["elementId"] = element_id
        if element_name is not UNSET:
            field_dict["elementName"] = element_name
        if has_incident is not UNSET:
            field_dict["hasIncident"] = has_incident
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if element_instance_key is not UNSET:
            field_dict["elementInstanceKey"] = element_instance_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if incident_key is not UNSET:
            field_dict["incidentKey"] = incident_key
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if element_instance_scope_key is not UNSET:
            field_dict["elementInstanceScopeKey"] = element_instance_scope_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.state_advancedfilter_3 import StateAdvancedfilter3
        from ..models.timestamp_advancedfilter import TimestampAdvancedfilter

        d = dict(src_dict)
        process_definition_id = lift_process_definition_id(_val) if (_val := d.pop("processDefinitionId", UNSET)) is not UNSET else UNSET

        def _parse_state(
            data: object,
        ) -> StateAdvancedfilter3 | StateExactmatch3 | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                state_type_0 = StateExactmatch3(data)

                return state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            state_type_1 = StateAdvancedfilter3.from_dict(data)

            return state_type_1

        state = _parse_state(d.pop("state", UNSET))

        _type_ = d.pop("type", UNSET)
        type_: SearchElementInstancesDataFilterType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = SearchElementInstancesDataFilterType(_type_)

        element_id = lift_element_id(_val) if (_val := d.pop("elementId", UNSET)) is not UNSET else UNSET

        element_name = d.pop("elementName", UNSET)

        has_incident = d.pop("hasIncident", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        element_instance_key = lift_element_instance_key(_val) if (_val := d.pop("elementInstanceKey", UNSET)) is not UNSET else UNSET

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        incident_key = lift_incident_key(_val) if (_val := d.pop("incidentKey", UNSET)) is not UNSET else UNSET

        def _parse_start_date(
            data: object,
        ) -> datetime.datetime | TimestampAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_date_type_0 = isoparse(data)

                return start_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            start_date_type_1 = TimestampAdvancedfilter.from_dict(data)

            return start_date_type_1

        start_date = _parse_start_date(d.pop("startDate", UNSET))

        def _parse_end_date(
            data: object,
        ) -> datetime.datetime | TimestampAdvancedfilter | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                end_date_type_0 = isoparse(data)

                return end_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            end_date_type_1 = TimestampAdvancedfilter.from_dict(data)

            return end_date_type_1

        end_date = _parse_end_date(d.pop("endDate", UNSET))

        def _parse_element_instance_scope_key(data: object) -> str | Unset:
            if isinstance(data, Unset):
                return data
            return cast(str | Unset, data)

        element_instance_scope_key = _parse_element_instance_scope_key(
            d.pop("elementInstanceScopeKey", UNSET)
        )

        search_element_instances_data_filter = cls(
            process_definition_id=process_definition_id,
            state=state,
            type_=type_,
            element_id=element_id,
            element_name=element_name,
            has_incident=has_incident,
            tenant_id=tenant_id,
            element_instance_key=element_instance_key,
            process_instance_key=process_instance_key,
            process_definition_key=process_definition_key,
            incident_key=incident_key,
            start_date=start_date,
            end_date=end_date,
            element_instance_scope_key=element_instance_scope_key,
        )

        search_element_instances_data_filter.additional_properties = d
        return search_element_instances_data_filter

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
