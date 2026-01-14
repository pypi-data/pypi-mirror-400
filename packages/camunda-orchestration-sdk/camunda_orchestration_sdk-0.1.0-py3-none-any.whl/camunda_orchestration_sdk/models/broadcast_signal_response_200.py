from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="BroadcastSignalResponse200")


@_attrs_define
class BroadcastSignalResponse200:
    """
    Attributes:
        tenant_id (str): The tenant ID of the signal that was broadcast. Example: customer-service.
        signal_key (str): The key of the broadcasted signal. Example: 22517998136987467.
    """

    tenant_id: TenantId
    signal_key: SignalKey
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        signal_key = self.signal_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tenantId": tenant_id,
                "signalKey": signal_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tenant_id = lift_tenant_id(d.pop("tenantId"))

        signal_key = lift_signal_key(d.pop("signalKey"))

        broadcast_signal_response_200 = cls(
            tenant_id=tenant_id,
            signal_key=signal_key,
        )

        broadcast_signal_response_200.additional_properties = d
        return broadcast_signal_response_200

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
