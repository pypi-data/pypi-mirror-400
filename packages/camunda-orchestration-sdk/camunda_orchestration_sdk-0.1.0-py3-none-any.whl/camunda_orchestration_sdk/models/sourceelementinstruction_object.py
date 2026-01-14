from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SourceelementinstructionObject")


@_attrs_define
class SourceelementinstructionObject:
    """Defines an instruction with a sourceElementId. The move instruction with this sourceType will terminate all active
    element
    instances with the sourceElementId and activate a new element instance for each terminated
    one at targetElementId.

        Attributes:
            source_type (str): The type of source element instruction. Example: byId.
            source_element_id (str): The id of the source element for the move instruction.
                 Example: Activity_106kosb.
    """

    source_type: str
    source_element_id: ElementId
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_type = self.source_type

        source_element_id = self.source_element_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sourceType": source_type,
                "sourceElementId": source_element_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        source_type = d.pop("sourceType")

        source_element_id = lift_element_id(d.pop("sourceElementId"))

        sourceelementinstruction_object = cls(
            source_type=source_type,
            source_element_id=source_element_id,
        )

        sourceelementinstruction_object.additional_properties = d
        return sourceelementinstruction_object

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
