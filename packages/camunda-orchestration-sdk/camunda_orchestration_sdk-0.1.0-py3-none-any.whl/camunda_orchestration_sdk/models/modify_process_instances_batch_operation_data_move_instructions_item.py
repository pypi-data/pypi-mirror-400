from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ModifyProcessInstancesBatchOperationDataMoveInstructionsItem")


@_attrs_define
class ModifyProcessInstancesBatchOperationDataMoveInstructionsItem:
    """Instructions describing a move operation. This instruction will terminate all active
    element instances at `sourceElementId` and activate a new element instance for each
    terminated one at `targetElementId`. The new element instances are created in the parent
    scope of the source element instances.

        Attributes:
            source_element_id (str): The source element ID. Example: Activity_106kosb.
            target_element_id (str): The target element ID. Example: Activity_106kosb.
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

        modify_process_instances_batch_operation_data_move_instructions_item = cls(
            source_element_id=source_element_id,
            target_element_id=target_element_id,
        )

        modify_process_instances_batch_operation_data_move_instructions_item.additional_properties = d
        return modify_process_instances_batch_operation_data_move_instructions_item

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
