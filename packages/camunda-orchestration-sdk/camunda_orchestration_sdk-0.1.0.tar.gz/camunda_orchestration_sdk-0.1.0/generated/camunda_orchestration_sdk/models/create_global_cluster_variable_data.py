from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.create_global_cluster_variable_data_value import (
        CreateGlobalClusterVariableDataValue,
    )


T = TypeVar("T", bound="CreateGlobalClusterVariableData")


@_attrs_define
class CreateGlobalClusterVariableData:
    """
    Attributes:
        name (str): The name of the cluster variable. Must be unique within its scope (global or tenant-specific).
        value (CreateGlobalClusterVariableDataValue): The value of the cluster variable. Can be any JSON object or
            primitive value. Will be serialized as a JSON string in responses.
    """

    name: str
    value: CreateGlobalClusterVariableDataValue
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        value = self.value.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_global_cluster_variable_data_value import (
            CreateGlobalClusterVariableDataValue,
        )

        d = dict(src_dict)
        name = d.pop("name")

        value = CreateGlobalClusterVariableDataValue.from_dict(d.pop("value"))

        create_global_cluster_variable_data = cls(
            name=name,
            value=value,
        )

        create_global_cluster_variable_data.additional_properties = d
        return create_global_cluster_variable_data

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
