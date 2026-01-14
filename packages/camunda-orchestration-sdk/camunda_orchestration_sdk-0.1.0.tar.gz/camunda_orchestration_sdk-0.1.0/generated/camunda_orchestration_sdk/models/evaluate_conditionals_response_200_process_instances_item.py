from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EvaluateConditionalsResponse200ProcessInstancesItem")


@_attrs_define
class EvaluateConditionalsResponse200ProcessInstancesItem:
    """
    Attributes:
        process_definition_key (str | Unset): The key of the process definition. Example: 2251799813686749.
        process_instance_key (str | Unset): The key of the created process instance. Example: 2251799813690746.
    """

    process_definition_key: ProcessDefinitionKey | Unset = UNSET
    process_instance_key: ProcessInstanceKey | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_definition_key = self.process_definition_key

        process_instance_key = self.process_instance_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if process_definition_key is not UNSET:
            field_dict["processDefinitionKey"] = process_definition_key
        if process_instance_key is not UNSET:
            field_dict["processInstanceKey"] = process_instance_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        process_definition_key = lift_process_definition_key(_val) if (_val := d.pop("processDefinitionKey", UNSET)) is not UNSET else UNSET

        process_instance_key = lift_process_instance_key(_val) if (_val := d.pop("processInstanceKey", UNSET)) is not UNSET else UNSET

        evaluate_conditionals_response_200_process_instances_item = cls(
            process_definition_key=process_definition_key,
            process_instance_key=process_instance_key,
        )

        evaluate_conditionals_response_200_process_instances_item.additional_properties = d
        return evaluate_conditionals_response_200_process_instances_item

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
