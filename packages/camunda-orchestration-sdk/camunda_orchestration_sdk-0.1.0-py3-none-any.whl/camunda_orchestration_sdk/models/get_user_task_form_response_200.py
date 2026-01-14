from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_user_task_form_response_200_schema import (
        GetUserTaskFormResponse200Schema,
    )


T = TypeVar("T", bound="GetUserTaskFormResponse200")


@_attrs_define
class GetUserTaskFormResponse200:
    """
    Attributes:
        tenant_id (str | Unset): The tenant ID of the form. Example: customer-service.
        form_id (str | Unset): The user-provided identifier of the form. Example: Form_1nx5hav.
        schema (GetUserTaskFormResponse200Schema | Unset): The form content.
        version (int | Unset): The version of the the deployed form.
        form_key (str | Unset): The assigned key, which acts as a unique identifier for this form. Example:
            2251799813684365.
    """

    tenant_id: TenantId | Unset = UNSET
    form_id: FormId | Unset = UNSET
    schema: GetUserTaskFormResponse200Schema | Unset = UNSET
    version: int | Unset = UNSET
    form_key: FormKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tenant_id = self.tenant_id

        form_id = self.form_id

        schema: dict[str, Any] | Unset = UNSET
        if not isinstance(self.schema, Unset):
            schema = self.schema.to_dict()

        version = self.version

        form_key = self.form_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tenant_id is not UNSET:
            field_dict["tenantId"] = tenant_id
        if form_id is not UNSET:
            field_dict["formId"] = form_id
        if schema is not UNSET:
            field_dict["schema"] = schema
        if version is not UNSET:
            field_dict["version"] = version
        if form_key is not UNSET:
            field_dict["formKey"] = form_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_user_task_form_response_200_schema import (
            GetUserTaskFormResponse200Schema,
        )

        d = dict(src_dict)
        tenant_id = lift_tenant_id(_val) if (_val := d.pop("tenantId", UNSET)) is not UNSET else UNSET

        form_id = lift_form_id(_val) if (_val := d.pop("formId", UNSET)) is not UNSET else UNSET

        _schema = d.pop("schema", UNSET)
        schema: GetUserTaskFormResponse200Schema | Unset
        if isinstance(_schema, Unset):
            schema = UNSET
        else:
            schema = GetUserTaskFormResponse200Schema.from_dict(_schema)

        version = d.pop("version", UNSET)

        form_key = lift_form_key(_val) if (_val := d.pop("formKey", UNSET)) is not UNSET else UNSET

        get_user_task_form_response_200 = cls(
            tenant_id=tenant_id,
            form_id=form_id,
            schema=schema,
            version=version,
            form_key=form_key,
        )

        get_user_task_form_response_200.additional_properties = d
        return get_user_task_form_response_200

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
