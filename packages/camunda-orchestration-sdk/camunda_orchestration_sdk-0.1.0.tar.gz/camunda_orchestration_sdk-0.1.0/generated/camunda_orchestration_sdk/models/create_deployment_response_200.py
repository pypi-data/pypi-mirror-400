from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.create_deployment_response_200_deployments_item import (
        CreateDeploymentResponse200DeploymentsItem,
    )


T = TypeVar("T", bound="CreateDeploymentResponse200")


@_attrs_define
class CreateDeploymentResponse200:
    """
    Attributes:
        deployment_key (str): The unique key identifying the deployment.
        tenant_id (str): The tenant ID associated with the deployment. Example: customer-service.
        deployments (list[CreateDeploymentResponse200DeploymentsItem]): Items deployed by the request.
    """

    deployment_key: DeploymentKey
    tenant_id: TenantId
    deployments: list[CreateDeploymentResponse200DeploymentsItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        deployment_key = self.deployment_key

        tenant_id = self.tenant_id

        deployments = []
        for deployments_item_data in self.deployments:
            deployments_item = deployments_item_data.to_dict()
            deployments.append(deployments_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "deploymentKey": deployment_key,
                "tenantId": tenant_id,
                "deployments": deployments,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_deployment_response_200_deployments_item import (
            CreateDeploymentResponse200DeploymentsItem,
        )

        d = dict(src_dict)
        deployment_key = lift_deployment_key(d.pop("deploymentKey"))

        tenant_id = lift_tenant_id(d.pop("tenantId"))

        deployments = []
        _deployments = d.pop("deployments")
        for deployments_item_data in _deployments:
            deployments_item = CreateDeploymentResponse200DeploymentsItem.from_dict(
                deployments_item_data
            )

            deployments.append(deployments_item)

        create_deployment_response_200 = cls(
            deployment_key=deployment_key,
            tenant_id=tenant_id,
            deployments=deployments,
        )

        create_deployment_response_200.additional_properties = d
        return create_deployment_response_200

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
