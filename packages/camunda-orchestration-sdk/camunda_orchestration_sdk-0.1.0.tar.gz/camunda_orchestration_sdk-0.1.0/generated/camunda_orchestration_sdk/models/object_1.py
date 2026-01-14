from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.object_1_owner_type import Object1OwnerType
from ..models.object_1_permission_types_item import Object1PermissionTypesItem
from ..models.object_1_resource_type import Object1ResourceType

T = TypeVar("T", bound="Object1")


@_attrs_define
class Object1:
    """
    Attributes:
        owner_id (str): The ID of the owner of the permissions.
        owner_type (Object1OwnerType): The type of the owner of permissions.
        resource_property_name (str): The name of the resource property on which this authorization is based.
        resource_type (Object1ResourceType): The type of resource to add permissions to.
        permission_types (list[Object1PermissionTypesItem]): The permission types to add.
    """

    owner_id: str
    owner_type: Object1OwnerType
    resource_property_name: str
    resource_type: Object1ResourceType
    permission_types: list[Object1PermissionTypesItem]

    def to_dict(self) -> dict[str, Any]:
        owner_id = self.owner_id

        owner_type = self.owner_type.value

        resource_property_name = self.resource_property_name

        resource_type = self.resource_type.value

        permission_types = []
        for permission_types_item_data in self.permission_types:
            permission_types_item = permission_types_item_data.value
            permission_types.append(permission_types_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "ownerId": owner_id,
                "ownerType": owner_type,
                "resourcePropertyName": resource_property_name,
                "resourceType": resource_type,
                "permissionTypes": permission_types,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        owner_id = d.pop("ownerId")

        owner_type = Object1OwnerType(d.pop("ownerType"))

        resource_property_name = d.pop("resourcePropertyName")

        resource_type = Object1ResourceType(d.pop("resourceType"))

        permission_types = []
        _permission_types = d.pop("permissionTypes")
        for permission_types_item_data in _permission_types:
            permission_types_item = Object1PermissionTypesItem(
                permission_types_item_data
            )

            permission_types.append(permission_types_item)

        object_1 = cls(
            owner_id=owner_id,
            owner_type=owner_type,
            resource_property_name=resource_property_name,
            resource_type=resource_type,
            permission_types=permission_types,
        )

        return object_1
