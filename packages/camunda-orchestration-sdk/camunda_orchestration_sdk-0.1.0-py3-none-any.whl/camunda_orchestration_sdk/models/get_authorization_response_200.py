from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_authorization_response_200_owner_type import (
    GetAuthorizationResponse200OwnerType,
)
from ..models.get_authorization_response_200_permission_types_item import (
    GetAuthorizationResponse200PermissionTypesItem,
)
from ..models.get_authorization_response_200_resource_type import (
    GetAuthorizationResponse200ResourceType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetAuthorizationResponse200")


@_attrs_define
class GetAuthorizationResponse200:
    """
    Attributes:
        owner_id (str | Unset): The ID of the owner of permissions.
        owner_type (GetAuthorizationResponse200OwnerType | Unset): The type of the owner of permissions.
        resource_type (GetAuthorizationResponse200ResourceType | Unset): The type of resource that the permissions
            relate to.
        resource_id (str | Unset): ID of the resource the permission relates to (mutually exclusive with
            `resourcePropertyName`).
        resource_property_name (str | Unset): The name of the resource property the permission relates to (mutually
            exclusive with `resourceId`).
        permission_types (list[GetAuthorizationResponse200PermissionTypesItem] | Unset): Specifies the types of the
            permissions.
        authorization_key (str | Unset): The key of the authorization. Example: 2251799813684332.
    """

    owner_id: str | Unset = UNSET
    owner_type: GetAuthorizationResponse200OwnerType | Unset = UNSET
    resource_type: GetAuthorizationResponse200ResourceType | Unset = UNSET
    resource_id: str | Unset = UNSET
    resource_property_name: str | Unset = UNSET
    permission_types: list[GetAuthorizationResponse200PermissionTypesItem] | Unset = (
        UNSET
    )
    authorization_key: AuthorizationKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        owner_id = self.owner_id

        owner_type: str | Unset = UNSET
        if not isinstance(self.owner_type, Unset):
            owner_type = self.owner_type.value

        resource_type: str | Unset = UNSET
        if not isinstance(self.resource_type, Unset):
            resource_type = self.resource_type.value

        resource_id = self.resource_id

        resource_property_name = self.resource_property_name

        permission_types: list[str] | Unset = UNSET
        if not isinstance(self.permission_types, Unset):
            permission_types = []
            for permission_types_item_data in self.permission_types:
                permission_types_item = permission_types_item_data.value
                permission_types.append(permission_types_item)

        authorization_key = self.authorization_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if owner_id is not UNSET:
            field_dict["ownerId"] = owner_id
        if owner_type is not UNSET:
            field_dict["ownerType"] = owner_type
        if resource_type is not UNSET:
            field_dict["resourceType"] = resource_type
        if resource_id is not UNSET:
            field_dict["resourceId"] = resource_id
        if resource_property_name is not UNSET:
            field_dict["resourcePropertyName"] = resource_property_name
        if permission_types is not UNSET:
            field_dict["permissionTypes"] = permission_types
        if authorization_key is not UNSET:
            field_dict["authorizationKey"] = authorization_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        owner_id = d.pop("ownerId", UNSET)

        _owner_type = d.pop("ownerType", UNSET)
        owner_type: GetAuthorizationResponse200OwnerType | Unset
        if isinstance(_owner_type, Unset):
            owner_type = UNSET
        else:
            owner_type = GetAuthorizationResponse200OwnerType(_owner_type)

        _resource_type = d.pop("resourceType", UNSET)
        resource_type: GetAuthorizationResponse200ResourceType | Unset
        if isinstance(_resource_type, Unset):
            resource_type = UNSET
        else:
            resource_type = GetAuthorizationResponse200ResourceType(_resource_type)

        resource_id = d.pop("resourceId", UNSET)

        resource_property_name = d.pop("resourcePropertyName", UNSET)

        _permission_types = d.pop("permissionTypes", UNSET)
        permission_types: (
            list[GetAuthorizationResponse200PermissionTypesItem] | Unset
        ) = UNSET
        if _permission_types is not UNSET:
            permission_types = []
            for permission_types_item_data in _permission_types:
                permission_types_item = GetAuthorizationResponse200PermissionTypesItem(
                    permission_types_item_data
                )

                permission_types.append(permission_types_item)

        authorization_key = lift_authorization_key(_val) if (_val := d.pop("authorizationKey", UNSET)) is not UNSET else UNSET

        get_authorization_response_200 = cls(
            owner_id=owner_id,
            owner_type=owner_type,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_property_name=resource_property_name,
            permission_types=permission_types,
            authorization_key=authorization_key,
        )

        get_authorization_response_200.additional_properties = d
        return get_authorization_response_200

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
