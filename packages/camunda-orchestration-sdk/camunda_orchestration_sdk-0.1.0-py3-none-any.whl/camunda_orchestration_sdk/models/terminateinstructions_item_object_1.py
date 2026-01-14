from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TerminateinstructionsItemObject1")


@_attrs_define
class TerminateinstructionsItemObject1:
    """Instruction providing the key of the element instance to terminate.

    Attributes:
        element_instance_key (str): The key of the element instance to terminate. Example: 2251799813686789.
    """

    element_instance_key: ElementInstanceKey
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        element_instance_key = self.element_instance_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "elementInstanceKey": element_instance_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        element_instance_key = lift_element_instance_key(d.pop("elementInstanceKey"))

        terminateinstructions_item_object_1 = cls(
            element_instance_key=element_instance_key,
        )

        terminateinstructions_item_object_1.additional_properties = d
        return terminateinstructions_item_object_1

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
