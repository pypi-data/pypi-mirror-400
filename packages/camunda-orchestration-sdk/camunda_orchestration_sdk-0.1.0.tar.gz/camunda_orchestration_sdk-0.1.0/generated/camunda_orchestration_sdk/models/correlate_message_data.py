from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.correlate_message_data_variables import CorrelateMessageDataVariables


T = TypeVar("T", bound="CorrelateMessageData")


@_attrs_define
class CorrelateMessageData:
    """
    Attributes:
        name (str): The message name as defined in the BPMN process
        correlation_key (str | Unset): The correlation key of the message. Default: ''. Example: customer-43421.
        variables (CorrelateMessageDataVariables | Unset): The message variables as JSON document
        tenant_id (str | Unset): the tenant for which the message is published Example: customer-service.
    """

    name: str
    correlation_key: MessageCorrelationKey | Unset = ""
    variables: CorrelateMessageDataVariables | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        correlation_key = self.correlation_key

        variables: dict[str, Any] | Unset = UNSET
        if not isinstance(self.variables, Unset):
            variables = self.variables.to_dict()

        tenant_id = self.tenant_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
            }
        )
        if correlation_key is not UNSET:
            field_dict["correlationKey"] = correlation_key
        if variables is not UNSET:
            field_dict["variables"] = variables
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.correlate_message_data_variables import (
            CorrelateMessageDataVariables,
        )

        d = dict(src_dict)
        name = d.pop("name")

        correlation_key = lift_message_correlation_key(_val) if (_val := d.pop("correlationKey", UNSET)) is not UNSET else UNSET

        _variables = d.pop("variables", UNSET)
        variables: CorrelateMessageDataVariables | Unset
        if isinstance(_variables, Unset):
            variables = UNSET
        else:
            variables = CorrelateMessageDataVariables.from_dict(_variables)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        correlate_message_data = cls(
            name=name,
            correlation_key=correlation_key,
            variables=variables,
            tenant_id=tenant_id,
        )

        return correlate_message_data
