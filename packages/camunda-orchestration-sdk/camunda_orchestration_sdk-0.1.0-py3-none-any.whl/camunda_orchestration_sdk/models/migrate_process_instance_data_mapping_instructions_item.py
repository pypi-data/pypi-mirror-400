from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MigrateProcessInstanceDataMappingInstructionsItem")


@_attrs_define
class MigrateProcessInstanceDataMappingInstructionsItem:
    """The mapping instructions describe how to map elements from the source process definition to the target process
    definition.

        Attributes:
            source_element_id (str): The element id to migrate from. Example: Activity_106kosb.
            target_element_id (str): The element id to migrate into. Example: Activity_106kosb.
    """

    source_element_id: ElementId
    target_element_id: ElementId
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_element_id = self.source_element_id

        target_element_id = self.target_element_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sourceElementId": source_element_id,
                "targetElementId": target_element_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        source_element_id = lift_element_id(d.pop("sourceElementId"))

        target_element_id = d.pop("targetElementId")

        migrate_process_instance_data_mapping_instructions_item = cls(
            source_element_id=source_element_id,
            target_element_id=target_element_id,
        )

        migrate_process_instance_data_mapping_instructions_item.additional_properties = d
        return migrate_process_instance_data_mapping_instructions_item

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
