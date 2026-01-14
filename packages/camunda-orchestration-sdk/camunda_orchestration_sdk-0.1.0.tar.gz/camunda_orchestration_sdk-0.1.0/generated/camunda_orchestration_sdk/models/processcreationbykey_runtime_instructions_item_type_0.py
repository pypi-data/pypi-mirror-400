from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProcesscreationbykeyRuntimeInstructionsItemType0")


@_attrs_define
class ProcesscreationbykeyRuntimeInstructionsItemType0:
    """Terminates the process instance after a specific BPMN element is completed or terminated.

    Attributes:
        after_element_id (str): The id of the element that, once completed or terminated, will cause the process to be
            terminated.
             Example: Activity_106kb.
        type_ (str | Unset): The type of the runtime instruction Example: TERMINATE_PROCESS_INSTANCE.
    """

    after_element_id: ElementId
    type_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        after_element_id = self.after_element_id

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "afterElementId": after_element_id,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        after_element_id = lift_element_id(d.pop("afterElementId"))

        type_ = d.pop("type", UNSET)

        processcreationbykey_runtime_instructions_item_type_0 = cls(
            after_element_id=after_element_id,
            type_=type_,
        )

        processcreationbykey_runtime_instructions_item_type_0.additional_properties = d
        return processcreationbykey_runtime_instructions_item_type_0

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
