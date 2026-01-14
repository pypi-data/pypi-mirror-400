from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetProcessInstanceCallHierarchyResponse200Item")


@_attrs_define
class GetProcessInstanceCallHierarchyResponse200Item:
    """
    Attributes:
        process_instance_key (str): The key of the process instance. Example: 2251799813690746.
        process_definition_key (str): The key of the process definition. Example: 2251799813686749.
        process_definition_name (str): The name of the process definition (fall backs to the process definition id if
            not available).
    """

    process_instance_key: ProcessInstanceKey
    process_definition_key: ProcessDefinitionKey
    process_definition_name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_instance_key = self.process_instance_key

        process_definition_key = self.process_definition_key

        process_definition_name = self.process_definition_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "processInstanceKey": process_instance_key,
                "processDefinitionKey": process_definition_key,
                "processDefinitionName": process_definition_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        process_instance_key = lift_process_instance_key(d.pop("processInstanceKey"))

        process_definition_key = lift_process_definition_key(d.pop("processDefinitionKey"))

        process_definition_name = d.pop("processDefinitionName")

        get_process_instance_call_hierarchy_response_200_item = cls(
            process_instance_key=process_instance_key,
            process_definition_key=process_definition_key,
            process_definition_name=process_definition_name,
        )

        get_process_instance_call_hierarchy_response_200_item.additional_properties = d
        return get_process_instance_call_hierarchy_response_200_item

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
