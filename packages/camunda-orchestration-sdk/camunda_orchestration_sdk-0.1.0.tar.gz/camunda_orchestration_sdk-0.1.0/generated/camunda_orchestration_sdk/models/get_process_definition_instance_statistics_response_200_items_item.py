from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetProcessDefinitionInstanceStatisticsResponse200ItemsItem")


@_attrs_define
class GetProcessDefinitionInstanceStatisticsResponse200ItemsItem:
    """Process definition instance statistics response.

    Attributes:
        process_definition_id (str | Unset): Id of a process definition, from the model. Only ids of process definitions
            that are deployed are useful. Example: new-account-onboarding-workflow.
        tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
        latest_process_definition_name (str | Unset): Name of the latest deployed process definition instance version.
        has_multiple_versions (bool | Unset): Indicates whether multiple versions of this process definition instance
            are deployed.
        active_instances_without_incident_count (int | Unset): Total number of currently active process instances of
            this definition that do not have incidents.
        active_instances_with_incident_count (int | Unset): Total number of currently active process instances of this
            definition that have at least one incident.
    """

    process_definition_id: ProcessDefinitionId | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    latest_process_definition_name: str | Unset = UNSET
    has_multiple_versions: bool | Unset = UNSET
    active_instances_without_incident_count: int | Unset = UNSET
    active_instances_with_incident_count: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition_id = self.process_definition_id

        tenant_id = self.tenant_id

        latest_process_definition_name = self.latest_process_definition_name

        has_multiple_versions = self.has_multiple_versions

        active_instances_without_incident_count = (
            self.active_instances_without_incident_count
        )

        active_instances_with_incident_count = self.active_instances_with_incident_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if latest_process_definition_name is not UNSET:
            field_dict["latestProcessDefinitionName"] = latest_process_definition_name
        if has_multiple_versions is not UNSET:
            field_dict["hasMultipleVersions"] = has_multiple_versions
        if active_instances_without_incident_count is not UNSET:
            field_dict["activeInstancesWithoutIncidentCount"] = (
                active_instances_without_incident_count
            )
        if active_instances_with_incident_count is not UNSET:
            field_dict["activeInstancesWithIncidentCount"] = (
                active_instances_with_incident_count
            )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        process_definition_id = lift_process_definition_id(_val) if (_val := d.pop("processDefinitionId", UNSET)) is not UNSET else UNSET

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        latest_process_definition_name = d.pop("latestProcessDefinitionName", UNSET)

        has_multiple_versions = d.pop("hasMultipleVersions", UNSET)

        active_instances_without_incident_count = d.pop(
            "activeInstancesWithoutIncidentCount", UNSET
        )

        active_instances_with_incident_count = d.pop(
            "activeInstancesWithIncidentCount", UNSET
        )

        get_process_definition_instance_statistics_response_200_items_item = cls(
            process_definition_id=process_definition_id,
            tenant_id=tenant_id,
            latest_process_definition_name=latest_process_definition_name,
            has_multiple_versions=has_multiple_versions,
            active_instances_without_incident_count=active_instances_without_incident_count,
            active_instances_with_incident_count=active_instances_with_incident_count,
        )

        get_process_definition_instance_statistics_response_200_items_item.additional_properties = d
        return get_process_definition_instance_statistics_response_200_items_item

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
