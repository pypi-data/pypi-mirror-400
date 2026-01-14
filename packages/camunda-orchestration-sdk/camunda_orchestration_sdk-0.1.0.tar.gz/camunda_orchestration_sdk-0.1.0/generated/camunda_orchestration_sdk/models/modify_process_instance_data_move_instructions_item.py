from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ancestorscopeinstruction_object import AncestorscopeinstructionObject
    from ..models.ancestorscopeinstruction_object_1 import (
        AncestorscopeinstructionObject1,
    )
    from ..models.ancestorscopeinstruction_object_2 import (
        AncestorscopeinstructionObject2,
    )
    from ..models.modify_process_instance_data_move_instructions_item_variable_instructions_item import (
        ModifyProcessInstanceDataMoveInstructionsItemVariableInstructionsItem,
    )
    from ..models.sourceelementinstruction_object import SourceelementinstructionObject
    from ..models.sourceelementinstruction_object_1 import (
        SourceelementinstructionObject1,
    )


T = TypeVar("T", bound="ModifyProcessInstanceDataMoveInstructionsItem")


@_attrs_define
class ModifyProcessInstanceDataMoveInstructionsItem:
    """Instruction describing a move operation. This instruction will terminate active element
    instances based on the sourceElementInstruction and activate a new element instance for each terminated
    one at targetElementId. Note that, for multi-instance activities, only the multi-instance
    body instances will activate new element instances at the target id.

        Attributes:
            source_element_instruction (SourceelementinstructionObject | SourceelementinstructionObject1): Defines the
                source element identifier for the move instruction. It can either be a sourceElementId, or
                sourceElementInstanceKey.
            target_element_id (str): The target element id. Example: Activity_106kosb.
            ancestor_scope_instruction (AncestorscopeinstructionObject | AncestorscopeinstructionObject1 |
                AncestorscopeinstructionObject2 | Unset): Defines the ancestor scope for the created element instances. The
                default behavior resembles
                a "direct" scope instruction with an `ancestorElementInstanceKey` of `"-1"`.
            variable_instructions (list[ModifyProcessInstanceDataMoveInstructionsItemVariableInstructionsItem] | Unset):
                Instructions describing which variables to create or update.
    """

    source_element_instruction: (
        SourceelementinstructionObject | SourceelementinstructionObject1
    )
    target_element_id: ElementId
    ancestor_scope_instruction: (
        AncestorscopeinstructionObject
        | AncestorscopeinstructionObject1
        | AncestorscopeinstructionObject2
        | Unset
    ) = UNSET
    variable_instructions: (
        list[ModifyProcessInstanceDataMoveInstructionsItemVariableInstructionsItem]
        | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.ancestorscopeinstruction_object import (
            AncestorscopeinstructionObject,
        )
        from ..models.ancestorscopeinstruction_object_1 import (
            AncestorscopeinstructionObject1,
        )
        from ..models.sourceelementinstruction_object import (
            SourceelementinstructionObject,
        )

        source_element_instruction: dict[str, Any]
        if isinstance(self.source_element_instruction, SourceelementinstructionObject):
            source_element_instruction = self.source_element_instruction.to_dict()
        else:
            source_element_instruction = self.source_element_instruction.to_dict()

        target_element_id = self.target_element_id

        ancestor_scope_instruction: dict[str, Any] | Unset
        if isinstance(self.ancestor_scope_instruction, Unset):
            ancestor_scope_instruction = UNSET
        elif isinstance(
            self.ancestor_scope_instruction, AncestorscopeinstructionObject
        ):
            ancestor_scope_instruction = self.ancestor_scope_instruction.to_dict()
        elif isinstance(
            self.ancestor_scope_instruction, AncestorscopeinstructionObject1
        ):
            ancestor_scope_instruction = self.ancestor_scope_instruction.to_dict()
        else:
            ancestor_scope_instruction = self.ancestor_scope_instruction.to_dict()

        variable_instructions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.variable_instructions, Unset):
            variable_instructions = []
            for variable_instructions_item_data in self.variable_instructions:
                variable_instructions_item = variable_instructions_item_data.to_dict()
                variable_instructions.append(variable_instructions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sourceElementInstruction": source_element_instruction,
                "targetElementId": target_element_id,
            }
        )
        if ancestor_scope_instruction is not UNSET:
            field_dict["ancestorScopeInstruction"] = ancestor_scope_instruction
        if variable_instructions is not UNSET:
            field_dict["variableInstructions"] = variable_instructions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ancestorscopeinstruction_object import (
            AncestorscopeinstructionObject,
        )
        from ..models.ancestorscopeinstruction_object_1 import (
            AncestorscopeinstructionObject1,
        )
        from ..models.ancestorscopeinstruction_object_2 import (
            AncestorscopeinstructionObject2,
        )
        from ..models.modify_process_instance_data_move_instructions_item_variable_instructions_item import (
            ModifyProcessInstanceDataMoveInstructionsItemVariableInstructionsItem,
        )
        from ..models.sourceelementinstruction_object import (
            SourceelementinstructionObject,
        )
        from ..models.sourceelementinstruction_object_1 import (
            SourceelementinstructionObject1,
        )

        d = dict(src_dict)

        def _parse_source_element_instruction(
            data: object,
        ) -> SourceelementinstructionObject | SourceelementinstructionObject1:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_element_instruction_type_0 = (
                    SourceelementinstructionObject.from_dict(data)
                )

                return source_element_instruction_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            source_element_instruction_type_1 = (
                SourceelementinstructionObject1.from_dict(data)
            )

            return source_element_instruction_type_1

        source_element_instruction = _parse_source_element_instruction(
            d.pop("sourceElementInstruction")
        )

        target_element_id = lift_element_id(d.pop("targetElementId"))

        def _parse_ancestor_scope_instruction(
            data: object,
        ) -> (
            AncestorscopeinstructionObject
            | AncestorscopeinstructionObject1
            | AncestorscopeinstructionObject2
            | Unset
        ):
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                ancestor_scope_instruction_type_0 = (
                    AncestorscopeinstructionObject.from_dict(data)
                )

                return ancestor_scope_instruction_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                ancestor_scope_instruction_type_1 = (
                    AncestorscopeinstructionObject1.from_dict(data)
                )

                return ancestor_scope_instruction_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            ancestor_scope_instruction_type_2 = (
                AncestorscopeinstructionObject2.from_dict(data)
            )

            return ancestor_scope_instruction_type_2

        ancestor_scope_instruction = _parse_ancestor_scope_instruction(
            d.pop("ancestorScopeInstruction", UNSET)
        )

        _variable_instructions = d.pop("variableInstructions", UNSET)
        variable_instructions: (
            list[ModifyProcessInstanceDataMoveInstructionsItemVariableInstructionsItem]
            | Unset
        ) = UNSET
        if _variable_instructions is not UNSET:
            variable_instructions = []
            for variable_instructions_item_data in _variable_instructions:
                variable_instructions_item = ModifyProcessInstanceDataMoveInstructionsItemVariableInstructionsItem.from_dict(
                    variable_instructions_item_data
                )

                variable_instructions.append(variable_instructions_item)

        modify_process_instance_data_move_instructions_item = cls(
            source_element_instruction=source_element_instruction,
            target_element_id=target_element_id,
            ancestor_scope_instruction=ancestor_scope_instruction,
            variable_instructions=variable_instructions,
        )

        modify_process_instance_data_move_instructions_item.additional_properties = d
        return modify_process_instance_data_move_instructions_item

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
