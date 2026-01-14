from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchDecisionDefinitionsDataFilter")


@_attrs_define
class SearchDecisionDefinitionsDataFilter:
    """The decision definition search filters.

    Attributes:
        decision_definition_id (str | Unset): The DMN ID of the decision definition. Example: new-hire-onboarding-
            workflow.
        name (str | Unset): The DMN name of the decision definition.
        version (int | Unset): The assigned version of the decision definition.
        decision_requirements_id (str | Unset): the DMN ID of the decision requirements graph that the decision
            definition is part of.
        tenant_id (str | Unset): The tenant ID of the decision definition. Example: customer-service.
        decision_definition_key (str | Unset): The assigned key, which acts as a unique identifier for this decision
            definition. Example: 2251799813326547.
        decision_requirements_key (str | Unset): The assigned key of the decision requirements graph that the decision
            definition is part of. Example: 2251799813683346.
        decision_requirements_name (str | Unset): The DMN name of the decision requirements that the decision definition
            is part of.
        decision_requirements_version (int | Unset): The assigned version of the decision requirements that the decision
            definition is part of.
    """

    decision_definition_id: DecisionDefinitionId | Unset = UNSET
    name: str | Unset = UNSET
    version: int | Unset = UNSET
    decision_requirements_id: str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    decision_definition_key: DecisionDefinitionKey | Unset = UNSET
    decision_requirements_key: DecisionRequirementsKey | Unset = UNSET
    decision_requirements_name: str | Unset = UNSET
    decision_requirements_version: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        decision_definition_id = self.decision_definition_id

        name = self.name

        version = self.version

        decision_requirements_id = self.decision_requirements_id

        tenant_id = self.tenant_id

        decision_definition_key = self.decision_definition_key

        decision_requirements_key = self.decision_requirements_key

        decision_requirements_name = self.decision_requirements_name

        decision_requirements_version = self.decision_requirements_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if decision_definition_id is not UNSET:
            field_dict["decisionDefinitionId"] = decision_definition_id
        if name is not UNSET:
            field_dict["name"] = name
        if version is not UNSET:
            field_dict["version"] = version
        if decision_requirements_id is not UNSET:
            field_dict["decisionRequirementsId"] = decision_requirements_id
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if decision_definition_key is not UNSET:
            field_dict["decisionDefinitionKey"] = decision_definition_key
        if decision_requirements_key is not UNSET:
            field_dict["decisionRequirementsKey"] = decision_requirements_key
        if decision_requirements_name is not UNSET:
            field_dict["decisionRequirementsName"] = decision_requirements_name
        if decision_requirements_version is not UNSET:
            field_dict["decisionRequirementsVersion"] = decision_requirements_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        decision_definition_id = lift_decision_definition_id(_val) if (_val := d.pop("decisionDefinitionId", UNSET)) is not UNSET else UNSET

        name = d.pop("name", UNSET)

        version = d.pop("version", UNSET)

        decision_requirements_id = d.pop("decisionRequirementsId", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        decision_definition_key = lift_decision_definition_key(_val) if (_val := d.pop("decisionDefinitionKey", UNSET)) is not UNSET else UNSET

        decision_requirements_key = lift_decision_requirements_key(_val) if (_val := d.pop("decisionRequirementsKey", UNSET)) is not UNSET else UNSET

        decision_requirements_name = d.pop("decisionRequirementsName", UNSET)

        decision_requirements_version = d.pop("decisionRequirementsVersion", UNSET)

        search_decision_definitions_data_filter = cls(
            decision_definition_id=decision_definition_id,
            name=name,
            version=version,
            decision_requirements_id=decision_requirements_id,
            tenant_id=tenant_id,
            decision_definition_key=decision_definition_key,
            decision_requirements_key=decision_requirements_key,
            decision_requirements_name=decision_requirements_name,
            decision_requirements_version=decision_requirements_version,
        )

        search_decision_definitions_data_filter.additional_properties = d
        return search_decision_definitions_data_filter

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
