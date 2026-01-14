from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetVariableResponse200")


@_attrs_define
class GetVariableResponse200:
    """Variable search response item.

    Attributes:
        value (str | Unset): Full value of this variable.
        name (str | Unset): Name of this variable.
        tenant_id (str | Unset): Tenant ID of this variable. Example: customer-service.
        variable_key (str | Unset): The key for this variable. Example: 2251799813683287.
        scope_key (str | Unset): The key of the scope of this variable. Example: 2251799813683890.
        process_instance_key (str | Unset): The key of the process instance of this variable. Example: 2251799813690746.
    """

    value: str | Unset = UNSET
    name: str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    variable_key: VariableKey | Unset = UNSET
    scope_key: ScopeKey | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = self.value

        name = self.name

        tenant_id = self.tenant_id

        variable_key = self.variable_key

        scope_key = self.scope_key

        process_instance_key = self.process_instance_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if value is not UNSET:
            field_dict["value"] = value
        if name is not UNSET:
            field_dict["name"] = name
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if variable_key is not UNSET:
            field_dict["variableKey"] = variable_key
        if scope_key is not UNSET:
            field_dict["scopeKey"] = scope_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value = d.pop("value", UNSET)

        name = d.pop("name", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        variable_key = lift_variable_key(_val) if (_val := d.pop("variableKey", UNSET)) is not UNSET else UNSET

        scope_key = lift_scope_key(_val) if (_val := d.pop("scopeKey", UNSET)) is not UNSET else UNSET

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        get_variable_response_200 = cls(
            value=value,
            name=name,
            tenant_id=tenant_id,
            variable_key=variable_key,
            scope_key=scope_key,
            process_instance_key=process_instance_key,
        )

        get_variable_response_200.additional_properties = d
        return get_variable_response_200

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
