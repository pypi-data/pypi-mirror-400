from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_process_instance_response_200_variables import (
        CreateProcessInstanceResponse200Variables,
    )


T = TypeVar("T", bound="CreateProcessInstanceResponse200")


@_attrs_define
class CreateProcessInstanceResponse200:
    """
    Attributes:
        process_definition_id (str): The BPMN process id of the process definition which was used to create the process.
            instance
             Example: my-process-model-1.
        process_definition_version (int): The version of the process definition which was used to create the process
            instance.
             Example: 3.
        tenant_id (str): The tenant id of the created process instance. Example: <default>.
        variables (CreateProcessInstanceResponse200Variables): All the variables visible in the root scope.
        process_definition_key (str): The key of the process definition which was used to create the process instance.
             Example: 2251799813686749.
        process_instance_key (str): The unique identifier of the created process instance; to be used wherever a request
            needs a process instance key (e.g. CancelProcessInstanceRequest).
             Example: 2251799813690746.
        tags (list[str] | Unset): List of tags. Tags need to start with a letter; then alphanumerics, `_`, `-`, `:`, or
            `.`; length ≤ 100. Example: ['high-touch', 'remediation'].
    """

    process_definition_id: ProcessDefinitionId
    process_definition_version: int
    tenant_id: TenantId
    variables: CreateProcessInstanceResponse200Variables
    process_definition_key: ProcessDefinitionKey
    process_instance_key: ProcessInstanceKey
    tags: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition_id = self.process_definition_id

        process_definition_version = self.process_definition_version

        tenant_id = self.tenant_id

        variables = self.variables.to_dict()

        process_definition_key = self.process_definition_key

        process_instance_key = self.process_instance_key

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "processDefinitionId": process_definition_id,
                "processDefinitionVersion": process_definition_version,
                "tenantId": tenant_id,
                "variables": variables,
                "processDefinitionKey": process_definition_key,
                "processInstanceKey": process_instance_key,
            }
        )
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_process_instance_response_200_variables import (
            CreateProcessInstanceResponse200Variables,
        )

        d = dict(src_dict)
        process_definition_id = lift_process_definition_id(d.pop("processDefinitionId"))

        process_definition_version = d.pop("processDefinitionVersion")

        tenant_id = lift_tenant_id(d.pop("tenantId"))

        variables = CreateProcessInstanceResponse200Variables.from_dict(
            d.pop("variables")
        )

        process_definition_key = lift_process_definition_key(d.pop("processDefinitionKey"))

        process_instance_key = lift_process_instance_key(d.pop("processInstanceKey"))

        tags = cast(list[str], d.pop("tags", UNSET))

        create_process_instance_response_200 = cls(
            process_definition_id=process_definition_id,
            process_definition_version=process_definition_version,
            tenant_id=tenant_id,
            variables=variables,
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
            tags=tags,
        )

        create_process_instance_response_200.additional_properties = d
        return create_process_instance_response_200

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
