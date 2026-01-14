from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar(
    "T", bound="GetProcessDefinitionInstanceVersionStatisticsResponse200ItemsItem"
)


@_attrs_define
class GetProcessDefinitionInstanceVersionStatisticsResponse200ItemsItem:
    """Process definition instance version statistics response.

    Attributes:
        process_definition_id (str): The ID associated with the process definition. Example: new-account-onboarding-
            workflow.
        process_definition_key (str): The unique key of the process definition. Example: 2251799813686749.
        process_definition_name (str): The name of the process definition.
        tenant_id (str): The tenant ID associated with the process definition. Example: customer-service.
        process_definition_version (int): The version number of the process definition.
        active_instances_with_incident_count (int): The number of active process instances for this version that
            currently have incidents.
        active_instances_without_incident_count (int): The number of active process instances for this version that do
            not have any incidents.
    """

    process_definition_id: ProcessDefinitionId
    process_definition_key: ProcessDefinitionKey
    process_definition_name: str
    tenant_id: TenantId
    process_definition_version: int
    active_instances_with_incident_count: int
    active_instances_without_incident_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition_id = self.process_definition_id

        process_definition_key = self.process_definition_key

        process_definition_name = self.process_definition_name

        tenant_id = self.tenant_id

        process_definition_version = self.process_definition_version

        active_instances_with_incident_count = self.active_instances_with_incident_count

        active_instances_without_incident_count = (
            self.active_instances_without_incident_count
        )

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "processDefinitionId": process_definition_id,
                "processDefinitionKey": process_definition_key,
                "processDefinitionName": process_definition_name,
                "tenantId": tenant_id,
                "processDefinitionVersion": process_definition_version,
                "activeInstancesWithIncidentCount": active_instances_with_incident_count,
                "activeInstancesWithoutIncidentCount": active_instances_without_incident_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        process_definition_id = lift_process_definition_id(d.pop("processDefinitionId"))

        process_definition_key = lift_process_definition_key(d.pop("processDefinitionKey"))

        process_definition_name = d.pop("processDefinitionName")

        tenant_id = lift_tenant_id(d.pop("tenantId"))

        process_definition_version = d.pop("processDefinitionVersion")

        active_instances_with_incident_count = d.pop("activeInstancesWithIncidentCount")

        active_instances_without_incident_count = d.pop(
            "activeInstancesWithoutIncidentCount"
        )

        get_process_definition_instance_version_statistics_response_200_items_item = cls(
            process_definition_id=process_definition_id,
            process_definition_key=process_definition_key,
            process_definition_name=process_definition_name,
            tenant_id=tenant_id,
            process_definition_version=process_definition_version,
            active_instances_with_incident_count=active_instances_with_incident_count,
            active_instances_without_incident_count=active_instances_without_incident_count,
        )

        get_process_definition_instance_version_statistics_response_200_items_item.additional_properties = d
        return (
            get_process_definition_instance_version_statistics_response_200_items_item
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
