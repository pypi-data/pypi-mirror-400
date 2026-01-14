from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar

from attrs import define as _attrs_define

from .. import types
from ..types import UNSET, File, Unset

T = TypeVar("T", bound="CreateDeploymentData")


@_attrs_define
class CreateDeploymentData:
    """
    Attributes:
        resources (list[File]): The binary data to create the deployment resources. It is possible to have more than one
            form part with different form part names for the binary data to create a deployment.
        tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
    """

    resources: list[File]
    tenant_id: TenantId | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        resources = []
        for resources_item_data in self.resources:
            resources_item = resources_item_data.to_tuple()

            resources.append(resources_item)

        tenant_id = self.tenant_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "resources": resources,
            }
        )
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        for resources_item_element in self.resources:
            files.append(("resources", resources_item_element.to_tuple()))

        if not isinstance(self.tenant_id, Unset):
            files.append(
                ("tenantId", (None, str(self.tenant_id).encode(), "text/plain"))
            )

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        resources = []
        _resources = d.pop("resources")
        for resources_item_data in _resources:
            resources_item = File(payload=BytesIO(resources_item_data))

            resources.append(resources_item)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        create_deployment_data = cls(
            resources=resources,
            tenant_id=tenant_id,
        )

        return create_deployment_data
