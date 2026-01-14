from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.modify_process_instances_batch_operation_data_filter import (
        ModifyProcessInstancesBatchOperationDataFilter,
    )
    from ..models.modify_process_instances_batch_operation_data_move_instructions_item import (
        ModifyProcessInstancesBatchOperationDataMoveInstructionsItem,
    )


T = TypeVar("T", bound="ModifyProcessInstancesBatchOperationData")


@_attrs_define
class ModifyProcessInstancesBatchOperationData:
    """The process instance filter to define on which process instances tokens should be moved,
    and new element instances should be activated or terminated.

        Attributes:
            filter_ (ModifyProcessInstancesBatchOperationDataFilter): The process instance filter.
            move_instructions (list[ModifyProcessInstancesBatchOperationDataMoveInstructionsItem]): Instructions for moving
                tokens between elements.
            operation_reference (int | Unset): A reference key chosen by the user that will be part of all records resulting
                from this operation.
                Must be > 0 if provided.
    """

    filter_: ModifyProcessInstancesBatchOperationDataFilter
    move_instructions: list[
        ModifyProcessInstancesBatchOperationDataMoveInstructionsItem
    ]
    operation_reference: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        filter_ = self.filter_.to_dict()

        move_instructions = []
        for move_instructions_item_data in self.move_instructions:
            move_instructions_item = move_instructions_item_data.to_dict()
            move_instructions.append(move_instructions_item)

        operation_reference = self.operation_reference

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "filter": filter_,
                "moveInstructions": move_instructions,
            }
        )
        if operation_reference is not UNSET:
            field_dict["operationReference"] = operation_reference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.modify_process_instances_batch_operation_data_filter import (
            ModifyProcessInstancesBatchOperationDataFilter,
        )
        from ..models.modify_process_instances_batch_operation_data_move_instructions_item import (
            ModifyProcessInstancesBatchOperationDataMoveInstructionsItem,
        )

        d = dict(src_dict)
        filter_ = ModifyProcessInstancesBatchOperationDataFilter.from_dict(
            d.pop("filter")
        )

        move_instructions = []
        _move_instructions = d.pop("moveInstructions")
        for move_instructions_item_data in _move_instructions:
            move_instructions_item = (
                ModifyProcessInstancesBatchOperationDataMoveInstructionsItem.from_dict(
                    move_instructions_item_data
                )
            )

            move_instructions.append(move_instructions_item)

        operation_reference = d.pop("operationReference", UNSET)

        modify_process_instances_batch_operation_data = cls(
            filter_=filter_,
            move_instructions=move_instructions,
            operation_reference=operation_reference,
        )

        return modify_process_instances_batch_operation_data
