from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetProcessDefinitionResponse200")


@_attrs_define
class GetProcessDefinitionResponse200:
    """
    Attributes:
        name (str | Unset): Name of this process definition.
        resource_name (str | Unset): Resource name for this process definition.
        version (int | Unset): Version of this process definition.
        version_tag (str | Unset): Version tag of this process definition.
        process_definition_id (str | Unset): Process definition ID of this process definition. Example: new-account-
            onboarding-workflow.
        tenant_id (str | Unset): Tenant ID of this process definition. Example: customer-service.
        process_definition_key (str | Unset): The key for this process definition. Example: 2251799813686749.
        has_start_form (bool | Unset): Indicates whether the start event of the process has an associated Form Key.
    """

    name: str | Unset = UNSET
    resource_name: str | Unset = UNSET
    version: int | Unset = UNSET
    version_tag: str | Unset = UNSET
    process_definition_id: ProcessDefinitionId | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    has_start_form: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        resource_name = self.resource_name

        version = self.version

        version_tag = self.version_tag

        process_definition_id = self.process_definition_id

        tenant_id = self.tenant_id

        process_definition_key = self.process_definition_key

        has_start_form = self.has_start_form

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if resource_name is not UNSET:
            field_dict["resourceName"] = resource_name
        if version is not UNSET:
            field_dict["version"] = version
        if version_tag is not UNSET:
            field_dict["versionTag"] = version_tag
        if process_definition_id is not UNSET:
            field_dict["processDefinitionId"] = process_definition_id
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if has_start_form is not UNSET:
            field_dict["hasStartForm"] = has_start_form

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        resource_name = d.pop("resourceName", UNSET)

        version = d.pop("version", UNSET)

        version_tag = d.pop("versionTag", UNSET)

        process_definition_id = lift_process_definition_id(_val) if (_val := d.pop("processDefinitionId", UNSET)) is not UNSET else UNSET

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        has_start_form = d.pop("hasStartForm", UNSET)

        get_process_definition_response_200 = cls(
            name=name,
            resource_name=resource_name,
            version=version,
            version_tag=version_tag,
            process_definition_id=process_definition_id,
            tenant_id=tenant_id,
            process_definition_key=process_definition_key,
            has_start_form=has_start_form,
        )

        get_process_definition_response_200.additional_properties = d
        return get_process_definition_response_200

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
