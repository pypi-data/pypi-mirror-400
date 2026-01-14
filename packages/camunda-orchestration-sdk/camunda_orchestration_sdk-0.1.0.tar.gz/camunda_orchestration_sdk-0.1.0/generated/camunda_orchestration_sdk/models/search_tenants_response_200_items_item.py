from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchTenantsResponse200ItemsItem")


@_attrs_define
class SearchTenantsResponse200ItemsItem:
    """Tenant search response item.

    Attributes:
        name (str | Unset): The tenant name. Example: Customer Service department.
        tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
        description (str | Unset): The tenant description. Example: Customer Service department business processes.
    """

    name: str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    description: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        tenant_id = self.tenant_id

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        description = d.pop("description", UNSET)

        search_tenants_response_200_items_item = cls(
            name=name,
            tenant_id=tenant_id,
            description=description,
        )

        search_tenants_response_200_items_item.additional_properties = d
        return search_tenants_response_200_items_item

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
