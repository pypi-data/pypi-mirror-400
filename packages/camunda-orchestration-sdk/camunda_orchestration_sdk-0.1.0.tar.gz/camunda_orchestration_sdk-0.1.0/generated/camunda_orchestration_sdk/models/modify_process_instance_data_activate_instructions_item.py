from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.modify_process_instance_data_activate_instructions_item_variable_instructions_item import (
        ModifyProcessInstanceDataActivateInstructionsItemVariableInstructionsItem,
    )


T = TypeVar("T", bound="ModifyProcessInstanceDataActivateInstructionsItem")


@_attrs_define
class ModifyProcessInstanceDataActivateInstructionsItem:
    """Instruction describing an element to activate.

    Attributes:
        element_id (str): The id of the element to activate. Example: Activity_106kosb.
        variable_instructions (list[ModifyProcessInstanceDataActivateInstructionsItemVariableInstructionsItem] | Unset):
            Instructions describing which variables to create or update.
        ancestor_element_instance_key (str | Unset): The key of the ancestor scope the element instance should be
            created in.
            Set to -1 to create the new element instance within an existing element instance of the
            flow scope. If multiple instances of the target element's flow scope exist, choose one
            specifically with this property by providing its key.
    """

    element_id: ElementId
    variable_instructions: (
        list[ModifyProcessInstanceDataActivateInstructionsItemVariableInstructionsItem]
        | Unset
    ) = UNSET
    ancestor_element_instance_key: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        element_id = self.element_id

        variable_instructions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.variable_instructions, Unset):
            variable_instructions = []
            for variable_instructions_item_data in self.variable_instructions:
                variable_instructions_item = variable_instructions_item_data.to_dict()
                variable_instructions.append(variable_instructions_item)

        ancestor_element_instance_key: str | Unset
        if isinstance(self.ancestor_element_instance_key, Unset):
            ancestor_element_instance_key = UNSET
        else:
            ancestor_element_instance_key = self.ancestor_element_instance_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "elementId": element_id,
            }
        )
        if variable_instructions is not UNSET:
            field_dict["variableInstructions"] = variable_instructions
        if ancestor_element_instance_key is not UNSET:
            field_dict["ancestorElementInstanceKey"] = ancestor_element_instance_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.modify_process_instance_data_activate_instructions_item_variable_instructions_item import (
            ModifyProcessInstanceDataActivateInstructionsItemVariableInstructionsItem,
        )

        d = dict(src_dict)
        element_id = lift_element_id(d.pop("elementId"))

        _variable_instructions = d.pop("variableInstructions", UNSET)
        variable_instructions: (
            list[
                ModifyProcessInstanceDataActivateInstructionsItemVariableInstructionsItem
            ]
            | Unset
        ) = UNSET
        if _variable_instructions is not UNSET:
            variable_instructions = []
            for variable_instructions_item_data in _variable_instructions:
                variable_instructions_item = ModifyProcessInstanceDataActivateInstructionsItemVariableInstructionsItem.from_dict(
                    variable_instructions_item_data
                )

                variable_instructions.append(variable_instructions_item)

        def _parse_ancestor_element_instance_key(data: object) -> str | Unset:
            if isinstance(data, Unset):
                return data
            return cast(str | Unset, data)

        ancestor_element_instance_key = _parse_ancestor_element_instance_key(
            d.pop("ancestorElementInstanceKey", UNSET)
        )

        modify_process_instance_data_activate_instructions_item = cls(
            element_id=element_id,
            variable_instructions=variable_instructions,
            ancestor_element_instance_key=ancestor_element_instance_key,
        )

        modify_process_instance_data_activate_instructions_item.additional_properties = d
        return modify_process_instance_data_activate_instructions_item

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
