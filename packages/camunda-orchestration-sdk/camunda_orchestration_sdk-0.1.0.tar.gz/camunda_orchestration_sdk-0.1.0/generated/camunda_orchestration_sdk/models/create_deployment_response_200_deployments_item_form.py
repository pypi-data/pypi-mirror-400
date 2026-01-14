from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateDeploymentResponse200DeploymentsItemForm")


@_attrs_define
class CreateDeploymentResponse200DeploymentsItemForm:
    """A deployed form.

    Attributes:
        form_id (str | Unset): The form ID, as parsed during deployment, together with the version forms a
            unique identifier for a specific form.
             Example: Form_1nx5hav.
        version (int | Unset):
        resource_name (str | Unset):
        tenant_id (str | Unset): The unique identifier of the tenant. Example: customer-service.
        form_key (str | Unset): The assigned key, which acts as a unique identifier for this form. Example:
            2251799813684365.
    """

    form_id: FormId | Unset = UNSET
    version: int | Unset = UNSET
    resource_name: str | Unset = UNSET
    tenant_id: TenantId | Unset = UNSET
    form_key: FormKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        form_id = self.form_id

        version = self.version

        resource_name = self.resource_name

        tenant_id = self.tenant_id

        form_key = self.form_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if form_id is not UNSET:
            field_dict["formId"] = form_id
        if version is not UNSET:
            field_dict["version"] = version
        if resource_name is not UNSET:
            field_dict["resourceName"] = resource_name
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if form_key is not UNSET:
            field_dict["formKey"] = form_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        form_id = lift_form_id(_val) if (_val := d.pop("formId", UNSET)) is not UNSET else UNSET

        version = d.pop("version", UNSET)

        resource_name = d.pop("resourceName", UNSET)

        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        form_key = lift_form_key(_val) if (_val := d.pop("formKey", UNSET)) is not UNSET else UNSET

        create_deployment_response_200_deployments_item_form = cls(
            form_id=form_id,
            version=version,
            resource_name=resource_name,
            tenant_id=tenant_id,
            form_key=form_key,
        )

        create_deployment_response_200_deployments_item_form.additional_properties = d
        return create_deployment_response_200_deployments_item_form

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
