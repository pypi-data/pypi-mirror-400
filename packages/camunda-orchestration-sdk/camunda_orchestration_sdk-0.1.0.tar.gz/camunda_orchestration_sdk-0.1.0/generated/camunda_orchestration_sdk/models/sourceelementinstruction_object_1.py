from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SourceelementinstructionObject1")


@_attrs_define
class SourceelementinstructionObject1:
    """Defines an instruction with a sourceElementInstanceKey. The move instruction with this sourceType will terminate one
    active element
    instance with the sourceElementInstanceKey and activate a new element instance at targetElementId.

        Attributes:
            source_type (str): The type of source element instruction. Example: byKey.
            source_element_instance_key (str): The source element instance key for the move instruction.
                 Example: 2251799813686789.
    """

    source_type: str
    source_element_instance_key: ElementInstanceKey
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_type = self.source_type

        source_element_instance_key = self.source_element_instance_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sourceType": source_type,
                "sourceElementInstanceKey": source_element_instance_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        source_type = d.pop("sourceType")

        source_element_instance_key = lift_element_instance_key(d.pop("sourceElementInstanceKey"))

        sourceelementinstruction_object_1 = cls(
            source_type=source_type,
            source_element_instance_key=source_element_instance_key,
        )

        sourceelementinstruction_object_1.additional_properties = d
        return sourceelementinstruction_object_1

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
