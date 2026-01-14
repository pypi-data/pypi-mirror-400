from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateDeploymentResponse200DeploymentsItemDecisionDefinition")


@_attrs_define
class CreateDeploymentResponse200DeploymentsItemDecisionDefinition:
    """A deployed decision.

    Attributes:
        decision_definition_id (str | Unset): The dmn decision ID, as parsed during deployment, together with the
            version forms a
            unique identifier for a specific decision.
             Example: new-hire-onboarding-workflow.
        version (int | Unset): The assigned decision version.
        name (str | Unset): The DMN name of the decision, as parsed during deployment.
        tenant_id (str | Unset): The tenant ID of the deployed decision. Example: customer-service.
        decision_requirements_id (str | Unset): The dmn ID of the decision requirements graph that this decision is part
            of, as parsed during deployment.
        decision_definition_key (str | Unset): The assigned decision key, which acts as a unique identifier for this
            decision.
             Example: 2251799813326547.
        decision_requirements_key (str | Unset): The assigned key of the decision requirements graph that this decision
            is part of.
             Example: 2251799813683346.
    """

    decision_definition_id: DecisionDefinitionId | Unset = UNSET
    version: int | Unset = UNSET
    name: str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    decision_requirements_id: str | Unset = UNSET
    decision_definition_key: DecisionDefinitionKey | Unset = UNSET
    decision_requirements_key: DecisionRequirementsKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        decision_definition_id = self.decision_definition_id

        version = self.version

        name = self.name

        tenant_id = self.tenant_id

        decision_requirements_id = self.decision_requirements_id

        decision_definition_key = self.decision_definition_key

        decision_requirements_key = self.decision_requirements_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if decision_definition_id is not UNSET:
            field_dict["decisionDefinitionId"] = decision_definition_id
        if version is not UNSET:
            field_dict["version"] = version
        if name is not UNSET:
            field_dict["name"] = name
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if decision_requirements_id is not UNSET:
            field_dict["decisionRequirementsId"] = decision_requirements_id
        if decision_definition_key is not UNSET:
            field_dict["decisionDefinitionKey"] = decision_definition_key
        if decision_requirements_key is not UNSET:
            field_dict["decisionRequirementsKey"] = decision_requirements_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        decision_definition_id = lift_decision_definition_id(_val) if (_val := d.pop("decisionDefinitionId", UNSET)) is not UNSET else UNSET

        version = d.pop("version", UNSET)

        name = d.pop("name", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        decision_requirements_id = d.pop("decisionRequirementsId", UNSET)

        decision_definition_key = lift_decision_definition_key(_val) if (_val := d.pop("decisionDefinitionKey", UNSET)) is not UNSET else UNSET

        decision_requirements_key = lift_decision_requirements_key(_val) if (_val := d.pop("decisionRequirementsKey", UNSET)) is not UNSET else UNSET

        create_deployment_response_200_deployments_item_decision_definition = cls(
            decision_definition_id=decision_definition_id,
            version=version,
            name=name,
            tenant_id=tenant_id,
            decision_requirements_id=decision_requirements_id,
            decision_definition_key=decision_definition_key,
            decision_requirements_key=decision_requirements_key,
        )

        create_deployment_response_200_deployments_item_decision_definition.additional_properties = d
        return create_deployment_response_200_deployments_item_decision_definition

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
