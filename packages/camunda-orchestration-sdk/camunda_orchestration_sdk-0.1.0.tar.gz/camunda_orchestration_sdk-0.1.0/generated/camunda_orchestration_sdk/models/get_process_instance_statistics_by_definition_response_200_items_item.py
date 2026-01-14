from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetProcessInstanceStatisticsByDefinitionResponse200ItemsItem")


@_attrs_define
class GetProcessInstanceStatisticsByDefinitionResponse200ItemsItem:
    """
    Attributes:
        process_definition_id (str | Unset): Id of a process definition, from the model. Only ids of process definitions
            that are deployed are useful. Example: new-account-onboarding-workflow.
        process_definition_key (str | Unset): System-generated key for a deployed process definition. Example:
            2251799813686749.
        process_definition_name (str | Unset): The name of the process definition.
        process_definition_version (int | Unset): The version of the process definition.
        tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
        active_instances_with_error_count (int | Unset): The number of active process instances that currently have an
            incident
            with the specified error hash code.
    """

    process_definition_id: ProcessDefinitionId | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    process_definition_name: str | Unset = UNSET
    process_definition_version: int | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    active_instances_with_error_count: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition_id = self.process_definition_id

        process_definition_key = self.process_definition_key

        process_definition_name = self.process_definition_name

        process_definition_version = self.process_definition_version

        tenant_id = self.tenant_id

        active_instances_with_error_count = self.active_instances_with_error_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_definition_name is not UNSET:
            field_dict["processDefinitionName"] = process_definition_name
        if process_definition_version is not UNSET:
            field_dict["processDefinitionVersion"] = process_definition_version
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if active_instances_with_error_count is not UNSET:
            field_dict["activeInstancesWithErrorCount"] = (
                active_instances_with_error_count
            )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        process_definition_id = lift_process_definition_id(_val) if (_val := d.pop("processDefinitionId", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        process_definition_name = d.pop("processDefinitionName", UNSET)

        process_definition_version = d.pop("processDefinitionVersion", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        active_instances_with_error_count = d.pop(
            "activeInstancesWithErrorCount", UNSET
        )

        get_process_instance_statistics_by_definition_response_200_items_item = cls(
            process_definition_id=process_definition_id,
            process_definition_key=process_definition_key,
            process_definition_name=process_definition_name,
            process_definition_version=process_definition_version,
            tenant_id=tenant_id,
            active_instances_with_error_count=active_instances_with_error_count,
        )

        get_process_instance_statistics_by_definition_response_200_items_item.additional_properties = d
        return get_process_instance_statistics_by_definition_response_200_items_item

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
