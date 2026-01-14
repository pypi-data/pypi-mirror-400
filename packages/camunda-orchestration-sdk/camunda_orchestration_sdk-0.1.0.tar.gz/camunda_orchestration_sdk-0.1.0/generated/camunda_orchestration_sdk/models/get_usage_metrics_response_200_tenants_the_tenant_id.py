from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetUsageMetricsResponse200TenantsTheTenantID")


@_attrs_define
class GetUsageMetricsResponse200TenantsTheTenantID:
    """The usage metrics for the specific tenant.

    Attributes:
        process_instances (int | Unset): The amount of created root process instances.
        decision_instances (int | Unset): The amount of executed decision instances.
        assignees (int | Unset): The amount of unique active task users.
    """

    process_instances: int | Unset = UNSET
    decision_instances: int | Unset = UNSET
    assignees: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_instances = self.process_instances

        decision_instances = self.decision_instances

        assignees = self.assignees

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if process_instances is not UNSET:
            field_dict["processInstances"] = process_instances
        if decision_instances is not UNSET:
            field_dict["decisionInstances"] = decision_instances
        if assignees is not UNSET:
            field_dict["assignees"] = assignees

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        process_instances = d.pop("processInstances", UNSET)

        decision_instances = d.pop("decisionInstances", UNSET)

        assignees = d.pop("assignees", UNSET)

        get_usage_metrics_response_200_tenants_the_tenant_id = cls(
            process_instances=process_instances,
            decision_instances=decision_instances,
            assignees=assignees,
        )

        get_usage_metrics_response_200_tenants_the_tenant_id.additional_properties = d
        return get_usage_metrics_response_200_tenants_the_tenant_id

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
