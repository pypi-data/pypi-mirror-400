from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateDeploymentResponse200DeploymentsItemDecisionRequirements")


@_attrs_define
class CreateDeploymentResponse200DeploymentsItemDecisionRequirements:
    """Deployed decision requirements.

    Attributes:
        decision_requirements_id (str | Unset):
        decision_requirements_name (str | Unset):
        version (int | Unset):
        resource_name (str | Unset):
        tenant_id (str | Unset): The tenant ID of the deployed decision requirements. Example: customer-service.
        decision_requirements_key (str | Unset): The assigned decision requirements key, which acts as a unique
            identifier for this decision requirements.
             Example: 2251799813683346.
    """

    decision_requirements_id: str | Unset = UNSET
    decision_requirements_name: str | Unset = UNSET
    version: int | Unset = UNSET
    resource_name: str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    decision_requirements_key: DecisionRequirementsKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        decision_requirements_id = self.decision_requirements_id

        decision_requirements_name = self.decision_requirements_name

        version = self.version

        resource_name = self.resource_name

        tenant_id = self.tenant_id

        decision_requirements_key = self.decision_requirements_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if decision_requirements_id is not UNSET:
            field_dict["decisionRequirementsId"] = decision_requirements_id
        if decision_requirements_name is not UNSET:
            field_dict["decisionRequirementsName"] = decision_requirements_name
        if version is not UNSET:
            field_dict["version"] = version
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
        decision_requirements_id = d.pop("decisionRequirementsId", UNSET)

        decision_requirements_name = d.pop("decisionRequirementsName", UNSET)

        version = d.pop("version", UNSET)

        resource_name = d.pop("resourceName", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        decision_requirements_key = lift_decision_requirements_key(_val) if (_val := d.pop("decisionRequirementsKey", UNSET)) is not UNSET else UNSET

        create_deployment_response_200_deployments_item_decision_requirements = cls(
            decision_requirements_id=decision_requirements_id,
            decision_requirements_name=decision_requirements_name,
            version=version,
            resource_name=resource_name,
            tenant_id=tenant_id,
            decision_requirements_key=decision_requirements_key,
        )

        create_deployment_response_200_deployments_item_decision_requirements.additional_properties = d
        return create_deployment_response_200_deployments_item_decision_requirements

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
