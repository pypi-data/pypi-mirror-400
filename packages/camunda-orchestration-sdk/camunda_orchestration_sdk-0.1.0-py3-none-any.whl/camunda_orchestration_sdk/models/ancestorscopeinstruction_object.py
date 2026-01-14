from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AncestorscopeinstructionObject")


@_attrs_define
class AncestorscopeinstructionObject:
    """Provides a concrete key to use as ancestor scope for the created element instance.

    Attributes:
        ancestor_scope_type (str): The type of ancestor scope instruction. Example: direct.
        ancestor_element_instance_key (str): The key of the ancestor scope the element instance should be created in.
            Set to -1 to create the new element instance within an existing element instance of the
            flow scope. If multiple instances of the target element's flow scope exist, choose one
            specifically with this property by providing its key.
    """

    ancestor_scope_type: str
    ancestor_element_instance_key: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ancestor_scope_type = self.ancestor_scope_type

        ancestor_element_instance_key: str
        ancestor_element_instance_key = self.ancestor_element_instance_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ancestorScopeType": ancestor_scope_type,
                "ancestorElementInstanceKey": ancestor_element_instance_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ancestor_scope_type = d.pop("ancestorScopeType")

        def _parse_ancestor_element_instance_key(data: object) -> str:
            return cast(str, data)

        ancestor_element_instance_key = _parse_ancestor_element_instance_key(
            d.pop("ancestorElementInstanceKey")
        )

        ancestorscopeinstruction_object = cls(
            ancestor_scope_type=ancestor_scope_type,
            ancestor_element_instance_key=ancestor_element_instance_key,
        )

        ancestorscopeinstruction_object.additional_properties = d
        return ancestorscopeinstruction_object

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
