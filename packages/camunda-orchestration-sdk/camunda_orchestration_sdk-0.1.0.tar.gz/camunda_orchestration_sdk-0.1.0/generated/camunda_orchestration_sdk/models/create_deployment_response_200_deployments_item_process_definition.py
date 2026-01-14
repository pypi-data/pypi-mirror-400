from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateDeploymentResponse200DeploymentsItemProcessDefinition")


@_attrs_define
class CreateDeploymentResponse200DeploymentsItemProcessDefinition:
    """A deployed process.

    Attributes:
        process_definition_id (str): The bpmn process ID, as parsed during deployment, together with the version forms a
            unique identifier for a specific process definition.
             Example: new-account-onboarding-workflow.
        process_definition_version (int): The assigned process version.
        resource_name (str): The resource name from which this process was parsed.
        tenant_id (str): The tenant ID of the deployed process. Example: customer-service.
        process_definition_key (str): The assigned key, which acts as a unique identifier for this process. Example:
            2251799813686749.
    """

    process_definition_id: ProcessDefinitionId
    process_definition_version: int
    resource_name: str
    tenant_id: TenantId
    process_definition_key: ProcessDefinitionKey
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition_id = self.process_definition_id

        process_definition_version = self.process_definition_version

        resource_name = self.resource_name

        tenant_id = self.tenant_id

        process_definition_key = self.process_definition_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "processDefinitionId": process_definition_id,
                "processDefinitionVersion": process_definition_version,
                "resourceName": resource_name,
                "tenantId": tenant_id,
                "processDefinitionKey": process_definition_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        process_definition_id = lift_process_definition_id(d.pop("processDefinitionId"))

        process_definition_version = d.pop("processDefinitionVersion")

        resource_name = d.pop("resourceName")

        tenant_id = lift_tenant_id(d.pop("tenantId"))

        process_definition_key = lift_process_definition_key(d.pop("processDefinitionKey"))

        create_deployment_response_200_deployments_item_process_definition = cls(
            process_definition_id=process_definition_id,
            process_definition_version=process_definition_version,
            resource_name=resource_name,
            tenant_id=tenant_id,
            process_definition_key=process_definition_key,
        )

        create_deployment_response_200_deployments_item_process_definition.additional_properties = d
        return create_deployment_response_200_deployments_item_process_definition

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
