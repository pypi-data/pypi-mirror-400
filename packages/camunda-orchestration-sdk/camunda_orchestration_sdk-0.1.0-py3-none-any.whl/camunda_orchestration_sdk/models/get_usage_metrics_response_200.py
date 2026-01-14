from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_usage_metrics_response_200_tenants import (
        GetUsageMetricsResponse200Tenants,
    )


T = TypeVar("T", bound="GetUsageMetricsResponse200")


@_attrs_define
class GetUsageMetricsResponse200:
    """
    Attributes:
        active_tenants (int | Unset): The amount of active tenants.
        tenants (GetUsageMetricsResponse200Tenants | Unset): The usage metrics by tenants. Only available if request
            `withTenants` query parameter was `true`.
        process_instances (int | Unset): The amount of created root process instances.
        decision_instances (int | Unset): The amount of executed decision instances.
        assignees (int | Unset): The amount of unique active task users.
    """

    active_tenants: int | Unset = UNSET
    tenants: GetUsageMetricsResponse200Tenants | Unset = UNSET
    process_instances: int | Unset = UNSET
    decision_instances: int | Unset = UNSET
    assignees: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        active_tenants = self.active_tenants

        tenants: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tenants, Unset):
            tenants = self.tenants.to_dict()

        process_instances = self.process_instances

        decision_instances = self.decision_instances

        assignees = self.assignees

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if active_tenants is not UNSET:
            field_dict["activeTenants"] = active_tenants
        if tenants is not UNSET:
            field_dict["tenants"] = tenants
        if process_instances is not UNSET:
            field_dict["processInstances"] = process_instances
        if decision_instances is not UNSET:
            field_dict["decisionInstances"] = decision_instances
        if assignees is not UNSET:
            field_dict["assignees"] = assignees

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_usage_metrics_response_200_tenants import (
            GetUsageMetricsResponse200Tenants,
        )

        d = dict(src_dict)
        active_tenants = d.pop("activeTenants", UNSET)

        _tenants = d.pop("tenants", UNSET)
        tenants: GetUsageMetricsResponse200Tenants | Unset
        if isinstance(_tenants, Unset):
            tenants = UNSET
        else:
            tenants = GetUsageMetricsResponse200Tenants.from_dict(_tenants)

        process_instances = d.pop("processInstances", UNSET)

        decision_instances = d.pop("decisionInstances", UNSET)

        assignees = d.pop("assignees", UNSET)

        get_usage_metrics_response_200 = cls(
            active_tenants=active_tenants,
            tenants=tenants,
            process_instances=process_instances,
            decision_instances=decision_instances,
            assignees=assignees,
        )

        get_usage_metrics_response_200.additional_properties = d
        return get_usage_metrics_response_200

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
