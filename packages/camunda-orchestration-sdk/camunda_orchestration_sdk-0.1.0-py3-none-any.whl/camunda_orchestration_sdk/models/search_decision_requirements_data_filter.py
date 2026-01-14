from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchDecisionRequirementsDataFilter")


@_attrs_define
class SearchDecisionRequirementsDataFilter:
    """The decision definition search filters.

    Attributes:
        decision_requirements_name (str | Unset): The DMN name of the decision requirements.
        decision_requirements_id (str | Unset): the DMN ID of the decision requirements.
        decision_requirements_key (str | Unset): System-generated key for a deployed decision requirements definition.
            Example: 2251799813683346.
        version (int | Unset): The assigned version of the decision requirements.
        tenant_id (str | Unset): The tenant ID of the decision requirements. Example: customer-service.
        resource_name (str | Unset): The name of the resource from which the decision requirements were parsed
    """

    decision_requirements_name: str | Unset = UNSET
    decision_requirements_id: str | Unset = UNSET
    decision_requirements_key: DecisionRequirementsKey | Unset = UNSET
    version: int | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    resource_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        decision_requirements_name = self.decision_requirements_name

        decision_requirements_id = self.decision_requirements_id

        decision_requirements_key = self.decision_requirements_key

        version = self.version

        tenant_id = self.tenant_id

        resource_name = self.resource_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if decision_requirements_name is not UNSET:
            field_dict["decisionRequirementsName"] = decision_requirements_name
        if decision_requirements_id is not UNSET:
            field_dict["decisionRequirementsId"] = decision_requirements_id
        if decision_requirements_key is not UNSET:
            field_dict["decisionRequirementsKey"] = decision_requirements_key
        if version is not UNSET:
            field_dict["version"] = version
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if resource_name is not UNSET:
            field_dict["resourceName"] = resource_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        decision_requirements_name = d.pop("decisionRequirementsName", UNSET)

        decision_requirements_id = d.pop("decisionRequirementsId", UNSET)

        decision_requirements_key = lift_decision_requirements_key(_val) if (_val := d.pop("decisionRequirementsKey", UNSET)) is not UNSET else UNSET

        version = d.pop("version", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        resource_name = d.pop("resourceName", UNSET)

        search_decision_requirements_data_filter = cls(
            decision_requirements_name=decision_requirements_name,
            decision_requirements_id=decision_requirements_id,
            decision_requirements_key=decision_requirements_key,
            version=version,
            tenant_id=tenant_id,
            resource_name=resource_name,
        )

        search_decision_requirements_data_filter.additional_properties = d
        return search_decision_requirements_data_filter

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
