from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ProcesscreationbyidStartinstructionsItem")


@_attrs_define
class ProcesscreationbyidStartinstructionsItem:
    """
    Attributes:
        element_id (str): Future extensions might include:
              - different types of start instructions
              - ability to set local variables for different flow scopes

            For now, however, the start instruction is implicitly a "startBeforeElement" instruction
             Example: Activity_106kosb.
    """

    element_id: ElementId
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        element_id = self.element_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "elementId": element_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        element_id = lift_element_id(d.pop("elementId"))

        processcreationbyid_startinstructions_item = cls(
            element_id=element_id,
        )

        processcreationbyid_startinstructions_item.additional_properties = d
        return processcreationbyid_startinstructions_item

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
