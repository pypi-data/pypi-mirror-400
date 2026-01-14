from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.migrate_process_instance_data_mapping_instructions_item import (
        MigrateProcessInstanceDataMappingInstructionsItem,
    )


T = TypeVar("T", bound="MigrateProcessInstanceData")


@_attrs_define
class MigrateProcessInstanceData:
    """The migration instructions describe how to migrate a process instance from one process definition to another.

    Attributes:
        target_process_definition_key (str): The key of process definition to migrate the process instance to. Example:
            2251799813686749.
        mapping_instructions (list[MigrateProcessInstanceDataMappingInstructionsItem]): Element mappings from the source
            process instance to the target process instance.
        operation_reference (int | Unset): A reference key chosen by the user that will be part of all records resulting
            from this operation.
            Must be > 0 if provided.
    """

    target_process_definition_key: ProcessDefinitionKey
    mapping_instructions: list[MigrateProcessInstanceDataMappingInstructionsItem]
    operation_reference: int | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        target_process_definition_key = self.target_process_definition_key

        mapping_instructions = []
        for mapping_instructions_item_data in self.mapping_instructions:
            mapping_instructions_item = mapping_instructions_item_data.to_dict()
            mapping_instructions.append(mapping_instructions_item)

        operation_reference = self.operation_reference

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "targetProcessDefinitionKey": target_process_definition_key,
                "mappingInstructions": mapping_instructions,
            }
        )
        if operation_reference is not UNSET:
            field_dict["operationReference"] = operation_reference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.migrate_process_instance_data_mapping_instructions_item import (
            MigrateProcessInstanceDataMappingInstructionsItem,
        )

        d = dict(src_dict)
        target_process_definition_key = lift_process_definition_key(d.pop("targetProcessDefinitionKey"))

        mapping_instructions = []
        _mapping_instructions = d.pop("mappingInstructions")
        for mapping_instructions_item_data in _mapping_instructions:
            mapping_instructions_item = (
                MigrateProcessInstanceDataMappingInstructionsItem.from_dict(
                    mapping_instructions_item_data
                )
            )

            mapping_instructions.append(mapping_instructions_item)

        operation_reference = d.pop("operationReference", UNSET)

        migrate_process_instance_data = cls(
            target_process_definition_key=target_process_definition_key,
            mapping_instructions=mapping_instructions,
            operation_reference=operation_reference,
        )

        return migrate_process_instance_data
