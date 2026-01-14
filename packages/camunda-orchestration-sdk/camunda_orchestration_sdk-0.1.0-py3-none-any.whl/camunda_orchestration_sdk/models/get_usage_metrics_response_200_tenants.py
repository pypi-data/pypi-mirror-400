from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_usage_metrics_response_200_tenants_the_tenant_id import (
        GetUsageMetricsResponse200TenantsTheTenantID,
    )


T = TypeVar("T", bound="GetUsageMetricsResponse200Tenants")


@_attrs_define
class GetUsageMetricsResponse200Tenants:
    """The usage metrics by tenants. Only available if request `withTenants` query parameter was `true`."""

    additional_properties: dict[str, GetUsageMetricsResponse200TenantsTheTenantID] = (
        _attrs_field(init=False, factory=dict)
    )

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_usage_metrics_response_200_tenants_the_tenant_id import (
            GetUsageMetricsResponse200TenantsTheTenantID,
        )

        d = dict(src_dict)
        get_usage_metrics_response_200_tenants = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = (
                GetUsageMetricsResponse200TenantsTheTenantID.from_dict(prop_dict)
            )

            additional_properties[prop_name] = additional_property

        get_usage_metrics_response_200_tenants.additional_properties = (
            additional_properties
        )
        return get_usage_metrics_response_200_tenants

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> GetUsageMetricsResponse200TenantsTheTenantID:
        return self.additional_properties[key]

    def __setitem__(
        self, key: str, value: GetUsageMetricsResponse200TenantsTheTenantID
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
