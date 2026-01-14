from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateTenantData")


@_attrs_define
class CreateTenantData:
    """
    Attributes:
        tenant_id (str): The unique ID for the tenant. Must be 255 characters or less. Can contain letters, numbers,
            [`_`, `-`, `+`, `.`, `@`].
        name (str): The name of the tenant.
        description (str | Unset): The description of the tenant.
    """

    tenant_id: TenantId
    name: str
    description: str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        name = self.name

        description = self.description

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "tenantId": tenant_id,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tenant_id = lift_tenant_id(d.pop("tenantId"))

        name = d.pop("name")

        description = d.pop("description", UNSET)

        create_tenant_data = cls(
            tenant_id=tenant_id,
            name=name,
            description=description,
        )

        return create_tenant_data
