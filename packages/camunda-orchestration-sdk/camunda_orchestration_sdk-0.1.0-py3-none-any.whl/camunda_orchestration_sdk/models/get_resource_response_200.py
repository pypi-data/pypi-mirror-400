from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetResourceResponse200")


@_attrs_define
class GetResourceResponse200:
    """
    Attributes:
        resource_name (str | Unset): The resource name from which this resource was parsed.
        version (int | Unset): The assigned resource version.
        version_tag (str | Unset): The version tag of this resource.
        resource_id (str | Unset): The resource ID of this resource.
        tenant_id (str | Unset): The tenant ID of this resource. Example: customer-service.
        resource_key (str | Unset): The unique key of this resource.
    """

    resource_name: str | Unset = UNSET
    version: int | Unset = UNSET
    version_tag: str | Unset = UNSET
    resource_id: str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    resource_key: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resource_name = self.resource_name

        version = self.version

        version_tag = self.version_tag

        resource_id = self.resource_id

        tenant_id = self.tenant_id

        resource_key: str | Unset
        if isinstance(self.resource_key, Unset):
            resource_key = UNSET
        else:
            resource_key = self.resource_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if resource_name is not UNSET:
            field_dict["resourceName"] = resource_name
        if version is not UNSET:
            field_dict["version"] = version
        if version_tag is not UNSET:
            field_dict["versionTag"] = version_tag
        if resource_id is not UNSET:
            field_dict["resourceId"] = resource_id
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if resource_key is not UNSET:
            field_dict["resourceKey"] = resource_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        resource_name = d.pop("resourceName", UNSET)

        version = d.pop("version", UNSET)

        version_tag = d.pop("versionTag", UNSET)

        resource_id = d.pop("resourceId", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        def _parse_resource_key(data: object) -> str | Unset:
            if isinstance(data, Unset):
                return data
            return cast(str | Unset, data)

        resource_key = _parse_resource_key(d.pop("resourceKey", UNSET))

        get_resource_response_200 = cls(
            resource_name=resource_name,
            version=version,
            version_tag=version_tag,
            resource_id=resource_id,
            tenant_id=tenant_id,
            resource_key=resource_key,
        )

        get_resource_response_200.additional_properties = d
        return get_resource_response_200

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
