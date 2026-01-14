from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AncestorscopeinstructionObject1")


@_attrs_define
class AncestorscopeinstructionObject1:
    """Instructs the engine to derive the ancestor scope key from the source element's hierarchy. The engine traverses the
    source element's ancestry to find an instance that matches one of the target element's flow scopes, ensuring the
    target is activated in the correct scope.

        Attributes:
            ancestor_scope_type (str): The type of ancestor scope instruction. Example: inferred.
    """

    ancestor_scope_type: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ancestor_scope_type = self.ancestor_scope_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ancestorScopeType": ancestor_scope_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ancestor_scope_type = d.pop("ancestorScopeType")

        ancestorscopeinstruction_object_1 = cls(
            ancestor_scope_type=ancestor_scope_type,
        )

        ancestorscopeinstruction_object_1.additional_properties = d
        return ancestorscopeinstruction_object_1

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
