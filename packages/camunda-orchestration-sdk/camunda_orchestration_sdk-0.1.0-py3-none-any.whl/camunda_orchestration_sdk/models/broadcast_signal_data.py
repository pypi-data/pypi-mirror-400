from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.broadcast_signal_data_variables import BroadcastSignalDataVariables


T = TypeVar("T", bound="BroadcastSignalData")


@_attrs_define
class BroadcastSignalData:
    """
    Attributes:
        signal_name (str): The name of the signal to broadcast.
        variables (BroadcastSignalDataVariables | Unset): The signal variables as a JSON object.
        tenant_id (str | Unset): The ID of the tenant that owns the signal. Example: customer-service.
    """

    signal_name: str
    variables: BroadcastSignalDataVariables | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        signal_name = self.signal_name

        variables: dict[str, Any] | Unset = UNSET
        if not isinstance(self.variables, Unset):
            variables = self.variables.to_dict()

        tenant_id = self.tenant_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "signalName": signal_name,
            }
        )
        if variables is not UNSET:
            field_dict["variables"] = variables
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.broadcast_signal_data_variables import (
            BroadcastSignalDataVariables,
        )

        d = dict(src_dict)
        signal_name = d.pop("signalName")

        _variables = d.pop("variables", UNSET)
        variables: BroadcastSignalDataVariables | Unset
        if isinstance(_variables, Unset):
            variables = UNSET
        else:
            variables = BroadcastSignalDataVariables.from_dict(_variables)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        broadcast_signal_data = cls(
            signal_name=signal_name,
            variables=variables,
            tenant_id=tenant_id,
        )

        return broadcast_signal_data
