from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.migrate_process_instances_batch_operation_data_migration_plan_mapping_instructions_item import (
        MigrateProcessInstancesBatchOperationDataMigrationPlanMappingInstructionsItem,
    )


T = TypeVar("T", bound="MigrateProcessInstancesBatchOperationDataMigrationPlan")


@_attrs_define
class MigrateProcessInstancesBatchOperationDataMigrationPlan:
    """The migration plan.

    Attributes:
        target_process_definition_key (str): The target process definition key. Example: 2251799813686749.
        mapping_instructions (list[MigrateProcessInstancesBatchOperationDataMigrationPlanMappingInstructionsItem]): The
            mapping instructions.
    """

    target_process_definition_key: ProcessDefinitionKey
    mapping_instructions: list[
        MigrateProcessInstancesBatchOperationDataMigrationPlanMappingInstructionsItem
    ]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        target_process_definition_key = self.target_process_definition_key

        mapping_instructions = []
        for mapping_instructions_item_data in self.mapping_instructions:
            mapping_instructions_item = mapping_instructions_item_data.to_dict()
            mapping_instructions.append(mapping_instructions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "targetProcessDefinitionKey": target_process_definition_key,
                "mappingInstructions": mapping_instructions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.migrate_process_instances_batch_operation_data_migration_plan_mapping_instructions_item import (
            MigrateProcessInstancesBatchOperationDataMigrationPlanMappingInstructionsItem,
        )

        d = dict(src_dict)
        target_process_definition_key = lift_process_definition_key(d.pop("targetProcessDefinitionKey"))

        mapping_instructions = []
        _mapping_instructions = d.pop("mappingInstructions")
        for mapping_instructions_item_data in _mapping_instructions:
            mapping_instructions_item = MigrateProcessInstancesBatchOperationDataMigrationPlanMappingInstructionsItem.from_dict(
                mapping_instructions_item_data
            )

            mapping_instructions.append(mapping_instructions_item)

        migrate_process_instances_batch_operation_data_migration_plan = cls(
            target_process_definition_key=target_process_definition_key,
            mapping_instructions=mapping_instructions,
        )

        migrate_process_instances_batch_operation_data_migration_plan.additional_properties = d
        return migrate_process_instances_batch_operation_data_migration_plan

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
