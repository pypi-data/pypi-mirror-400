from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.evaluate_conditionals_data_variables import (
        EvaluateConditionalsDataVariables,
    )


T = TypeVar("T", bound="EvaluateConditionalsData")


@_attrs_define
class EvaluateConditionalsData:
    """
    Attributes:
        variables (EvaluateConditionalsDataVariables): JSON object representing the variables to use for evaluation of
            the conditions and to pass to the process instances that have been triggered.
             Example: {'x': 2}.
        tenant_id (str | Unset): Used to evaluate root-level conditional start events for a tenant with the given ID.
            This will only evaluate root-level conditional start events of process definitions which belong to the tenant.
             Example: customer-service.
        process_definition_key (str | Unset): Used to evaluate root-level conditional start events of the process
            definition with the given key.
             Example: 2251799813686749.
    """

    variables: EvaluateConditionalsDataVariables
    tenant_id: TenantId | Unset = UNSET
    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        variables = self.variables.to_dict()

        tenant_id = self.tenant_id

        process_definition_key = self.process_definition_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "variables": variables,
            }
        )
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.evaluate_conditionals_data_variables import (
            EvaluateConditionalsDataVariables,
        )

        d = dict(src_dict)
        variables = EvaluateConditionalsDataVariables.from_dict(d.pop("variables"))

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        evaluate_conditionals_data = cls(
            variables=variables,
            tenant_id=tenant_id,
            process_definition_key=process_definition_key,
        )

        evaluate_conditionals_data.additional_properties = d
        return evaluate_conditionals_data

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
