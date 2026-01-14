from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDecisionRequirementsResponse200")


@_attrs_define
class GetDecisionRequirementsResponse200:
    """
    Attributes:
        decision_requirements_name (str | Unset): The DMN name of the decision requirements.
        version (int | Unset): The assigned version of the decision requirements.
        decision_requirements_id (str | Unset): The DMN ID of the decision requirements.
        resource_name (str | Unset): The name of the resource from which this decision requirements was parsed.
        tenant_id (str | Unset): The tenant ID of the decision requirements. Example: customer-service.
        decision_requirements_key (str | Unset): The assigned key, which acts as a unique identifier for this decision
            requirements. Example: 2251799813683346.
    """

    decision_requirements_name: str | Unset = UNSET
    version: int | Unset = UNSET
    decision_requirements_id: str | Unset = UNSET
    resource_name: str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    decision_requirements_key: DecisionRequirementsKey | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        decision_requirements_name = self.decision_requirements_name

        version = self.version

        decision_requirements_id = self.decision_requirements_id

        resource_name = self.resource_name

        tenant_id = self.tenant_id

        decision_requirements_key = self.decision_requirements_key

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if decision_requirements_name is not UNSET:
            field_dict["decisionRequirementsName"] = decision_requirements_name
        if version is not UNSET:
            field_dict["version"] = version
        if decision_requirements_id is not UNSET:
            field_dict["decisionRequirementsId"] = decision_requirements_id
        if resource_name is not UNSET:
            field_dict["resourceName"] = resource_name
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if decision_requirements_key is not UNSET:
            field_dict["decisionRequirementsKey"] = decision_requirements_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        decision_requirements_name = d.pop("decisionRequirementsName", UNSET)

        version = d.pop("version", UNSET)

        decision_requirements_id = d.pop("decisionRequirementsId", UNSET)

        resource_name = d.pop("resourceName", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        decision_requirements_key = lift_decision_requirements_key(_val) if (_val := d.pop("decisionRequirementsKey", UNSET)) is not UNSET else UNSET

        get_decision_requirements_response_200 = cls(
            decision_requirements_name=decision_requirements_name,
            version=version,
            decision_requirements_id=decision_requirements_id,
            resource_name=resource_name,
            tenant_id=tenant_id,
            decision_requirements_key=decision_requirements_key,
        )

        return get_decision_requirements_response_200
