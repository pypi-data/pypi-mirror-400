from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_global_cluster_variable_response_200_scope import (
    GetGlobalClusterVariableResponse200Scope,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetGlobalClusterVariableResponse200")


@_attrs_define
class GetGlobalClusterVariableResponse200:
    """
    Attributes:
        value (str): Full value of this cluster variable.
        name (str): The name of the cluster variable. Unique within its scope (global or tenant-specific).
        scope (GetGlobalClusterVariableResponse200Scope): The scope of a cluster variable.
        tenant_id (str | Unset): Only provided if the cluster variable scope is TENANT.
    """

    value: str
    name: str
    scope: GetGlobalClusterVariableResponse200Scope
    tenant_id: TenantId | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = self.value

        name = self.name

        scope = self.scope.value

        tenant_id = self.tenant_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
                "name": name,
                "scope": scope,
            }
        )
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value = d.pop("value")

        name = d.pop("name")

        scope = GetGlobalClusterVariableResponse200Scope(d.pop("scope"))

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        get_global_cluster_variable_response_200 = cls(
            value=value,
            name=name,
            scope=scope,
            tenant_id=tenant_id,
        )

        get_global_cluster_variable_response_200.additional_properties = d
        return get_global_cluster_variable_response_200

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
