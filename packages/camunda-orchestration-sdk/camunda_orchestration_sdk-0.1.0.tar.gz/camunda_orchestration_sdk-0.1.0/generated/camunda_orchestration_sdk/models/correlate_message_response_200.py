from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CorrelateMessageResponse200")


@_attrs_define
class CorrelateMessageResponse200:
    """The message key of the correlated message, as well as the first process instance key it
    correlated with.

        Attributes:
            tenant_id (str | Unset): The tenant ID of the correlated message Example: customer-service.
            message_key (str | Unset): The key of the correlated message. Example: 2251799813683467.
            process_instance_key (str | Unset): The key of the first process instance the message correlated with Example:
                2251799813690746.
    """

    tenant_id: TenantId | Unset = UNSET
    message_key: MessageKey | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        message_key = self.message_key

        process_instance_key = self.process_instance_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if message_key is not UNSET:
            field_dict["messageKey"] = message_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        message_key = lift_message_key(_val) if (_val := d.pop("messageKey", UNSET)) is not UNSET else UNSET

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        correlate_message_response_200 = cls(
            tenant_id=tenant_id,
            message_key=message_key,
            process_instance_key=process_instance_key,
        )

        correlate_message_response_200.additional_properties = d
        return correlate_message_response_200

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
