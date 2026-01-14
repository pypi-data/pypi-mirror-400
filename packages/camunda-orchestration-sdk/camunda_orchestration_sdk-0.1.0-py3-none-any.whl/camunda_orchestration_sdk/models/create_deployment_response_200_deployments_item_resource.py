from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateDeploymentResponse200DeploymentsItemResource")


@_attrs_define
class CreateDeploymentResponse200DeploymentsItemResource:
    """A deployed Resource.

    Attributes:
        resource_id (str | Unset):
        resource_name (str | Unset):
        version (int | Unset):
        tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
        resource_key (str | Unset): The assigned key, which acts as a unique identifier for this Resource.
    """

    resource_id: str | Unset = UNSET
    resource_name: str | Unset = UNSET
    version: int | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    resource_key: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resource_id = self.resource_id

        resource_name = self.resource_name

        version = self.version

        tenant_id = self.tenant_id

        resource_key: str | Unset
        if isinstance(self.resource_key, Unset):
            resource_key = UNSET
        else:
            resource_key = self.resource_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if resource_id is not UNSET:
            field_dict["resourceId"] = resource_id
        if resource_name is not UNSET:
            field_dict["resourceName"] = resource_name
        if version is not UNSET:
            field_dict["version"] = version
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if resource_key is not UNSET:
            field_dict["resourceKey"] = resource_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        resource_id = d.pop("resourceId", UNSET)

        resource_name = d.pop("resourceName", UNSET)

        version = d.pop("version", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        def _parse_resource_key(data: object) -> str | Unset:
            if isinstance(data, Unset):
                return data
            return cast(str | Unset, data)

        resource_key = _parse_resource_key(d.pop("resourceKey", UNSET))

        create_deployment_response_200_deployments_item_resource = cls(
            resource_id=resource_id,
            resource_name=resource_name,
            version=version,
            tenant_id=tenant_id,
            resource_key=resource_key,
        )

        create_deployment_response_200_deployments_item_resource.additional_properties = d
        return create_deployment_response_200_deployments_item_resource

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
