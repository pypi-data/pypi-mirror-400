from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.decisionevaluationby_id_variables import (
        DecisionevaluationbyIDVariables,
    )


T = TypeVar("T", bound="Decisionevaluationbykey")


@_attrs_define
class Decisionevaluationbykey:
    """
    Attributes:
        decision_definition_key (str): System-generated key for a decision definition. Example: 2251799813326547.
        variables (DecisionevaluationbyIDVariables | Unset): The message variables as JSON document.
        tenant_id (str | Unset): The tenant ID of the decision. Example: customer-service.
    """

    decision_definition_key: DecisionDefinitionKey
    variables: DecisionevaluationbyIDVariables | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        decision_definition_key = self.decision_definition_key

        variables: dict[str, Any] | Unset = UNSET
        if not isinstance(self.variables, Unset):
            variables = self.variables.to_dict()

        tenant_id = self.tenant_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "decisionDefinitionKey": decision_definition_key,
            }
        )
        if variables is not UNSET:
            field_dict["variables"] = variables
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.decisionevaluationby_id_variables import (
            DecisionevaluationbyIDVariables,
        )

        d = dict(src_dict)
        decision_definition_key = lift_decision_definition_key(d.pop("decisionDefinitionKey"))

        _variables = d.pop("variables", UNSET)
        variables: DecisionevaluationbyIDVariables | Unset
        if isinstance(_variables, Unset):
            variables = UNSET
        else:
            variables = DecisionevaluationbyIDVariables.from_dict(_variables)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        decisionevaluationbykey = cls(
            decision_definition_key=decision_definition_key,
            variables=variables,
            tenant_id=tenant_id,
        )

        return decisionevaluationbykey
