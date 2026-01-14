from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.search_cluster_variables_response_200_items_item_scope import (
    SearchClusterVariablesResponse200ItemsItemScope,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchClusterVariablesResponse200ItemsItem")


@_attrs_define
class SearchClusterVariablesResponse200ItemsItem:
    """Cluster variable search response item.

    Attributes:
        value (str): Value of this cluster variable. Can be truncated.
        name (str): The name of the cluster variable. Unique within its scope (global or tenant-specific).
        scope (SearchClusterVariablesResponse200ItemsItemScope): The scope of a cluster variable.
        is_truncated (bool | Unset): Whether the value is truncated or not.
        tenant_id (str | Unset): Only provided if the cluster variable scope is TENANT.
    """

    value: str
    name: str
    scope: SearchClusterVariablesResponse200ItemsItemScope
    is_truncated: bool | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = self.value

        name = self.name

        scope = self.scope.value

        is_truncated = self.is_truncated

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
        if is_truncated is not UNSET:
            field_dict["isTruncated"] = is_truncated
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value = d.pop("value")

        name = d.pop("name")

        scope = SearchClusterVariablesResponse200ItemsItemScope(d.pop("scope"))

        is_truncated = d.pop("isTruncated", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        search_cluster_variables_response_200_items_item = cls(
            value=value,
            name=name,
            scope=scope,
            is_truncated=is_truncated,
            tenant_id=tenant_id,
        )

        search_cluster_variables_response_200_items_item.additional_properties = d
        return search_cluster_variables_response_200_items_item

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
