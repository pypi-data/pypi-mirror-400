from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.get_process_instance_response_200_state import (
    GetProcessInstanceResponse200State,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetProcessInstanceResponse200")


@_attrs_define
class GetProcessInstanceResponse200:
    """Process instance search response item.

    Attributes:
        process_definition_id (str): Id of a process definition, from the model. Only ids of process definitions that
            are deployed are useful. Example: new-account-onboarding-workflow.
        process_definition_name (str): The process definition name.
        process_definition_version (int):
        start_date (datetime.datetime):
        state (GetProcessInstanceResponse200State): Process instance states
        has_incident (bool): Whether this process instance has a related incident or not.
        tenant_id (str): The unique identifier of the tenant. Example: customer-service.
        process_instance_key (str): The key of this process instance. Example: 2251799813690746.
        process_definition_key (str): The process definition key. Example: 2251799813686749.
        process_definition_version_tag (str | Unset): The process definition version tag.
        end_date (datetime.datetime | Unset):
        parent_process_instance_key (str | Unset): The parent process instance key. Example: 2251799813690746.
        parent_element_instance_key (str | Unset): The parent element instance key. Example: 2251799813686789.
        tags (list[str] | Unset): List of tags. Tags need to start with a letter; then alphanumerics, `_`, `-`, `:`, or
            `.`; length ≤ 100. Example: ['high-touch', 'remediation'].
    """

    process_definition_id: ProcessDefinitionId
    process_definition_name: str
    process_definition_version: int
    start_date: datetime.datetime
    state: GetProcessInstanceResponse200State
    has_incident: bool
    tenant_id: TenantId
    process_instance_key: ProcessInstanceKey
    process_definition_key: ProcessDefinitionKey
    process_definition_version_tag: str | Unset = UNSET
    end_date: datetime.datetime | Unset = UNSET
    parent_process_instance_key: ProcessInstanceKey | Unset = UNSET
    parent_element_instance_key: ElementInstanceKey | Unset = UNSET
    tags: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition_id = self.process_definition_id

        process_definition_name = self.process_definition_name

        process_definition_version = self.process_definition_version

        start_date = self.start_date.isoformat()

        state = self.state.value

        has_incident = self.has_incident

        tenant_id = self.tenant_id

        process_instance_key = self.process_instance_key

        process_definition_key = self.process_definition_key

        process_definition_version_tag = self.process_definition_version_tag

        end_date: str | Unset = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        parent_process_instance_key = self.parent_process_instance_key

        parent_element_instance_key = self.parent_element_instance_key

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "processDefinitionId": process_definition_id,
                "processDefinitionName": process_definition_name,
                "processDefinitionVersion": process_definition_version,
                "startDate": start_date,
                "state": state,
                "hasIncident": has_incident,
                "tenantId": tenant_id,
                "processInstanceKey": process_instance_key,
                "processDefinitionKey": process_definition_key,
            }
        )
        if process_definition_version_tag is not UNSET:
            field_dict["processDefinitionVersionTag"] = process_definition_version_tag
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if parent_process_instance_key is not UNSET:
            field_dict["parentProcessInstanceKey"] = parent_process_instance_key
        if parent_element_instance_key is not UNSET:
            field_dict["parentElementInstanceKey"] = parent_element_instance_key
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        process_definition_id = lift_process_definition_id(d.pop("processDefinitionId"))

        process_definition_name = d.pop("processDefinitionName")

        process_definition_version = d.pop("processDefinitionVersion")

        start_date = isoparse(d.pop("startDate"))

        state = GetProcessInstanceResponse200State(d.pop("state"))

        has_incident = d.pop("hasIncident")

        tenant_id = lift_tenant_id(d.pop("tenantId"))

        process_instance_key = lift_process_instance_key(d.pop("processInstanceKey"))

        process_definition_key = lift_process_definition_key(d.pop("processDefinitionKey"))

        process_definition_version_tag = d.pop("processDefinitionVersionTag", UNSET)

        _end_date = d.pop("endDate", UNSET)
        end_date: datetime.datetime | Unset
        if isinstance(_end_date, Unset):
            end_date = UNSET
        else:
            end_date = isoparse(_end_date)

        parent_process_instance_key = d.pop("parentProcessInstanceKey", UNSET)

        parent_element_instance_key = lift_element_instance_key(_val) if (_val := d.pop("parentElementInstanceKey", UNSET)) is not UNSET else UNSET

        tags = cast(list[str], d.pop("tags", UNSET))

        get_process_instance_response_200 = cls(
            process_definition_id=process_definition_id,
            process_definition_name=process_definition_name,
            process_definition_version=process_definition_version,
            start_date=start_date,
            state=state,
            has_incident=has_incident,
            tenant_id=tenant_id,
            process_instance_key=process_instance_key,
            process_definition_key=process_definition_key,
            process_definition_version_tag=process_definition_version_tag,
            end_date=end_date,
            parent_process_instance_key=parent_process_instance_key,
            parent_element_instance_key=parent_element_instance_key,
            tags=tags,
        )

        get_process_instance_response_200.additional_properties = d
        return get_process_instance_response_200

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
