from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.evaluate_conditionals_response_200_process_instances_item import (
        EvaluateConditionalsResponse200ProcessInstancesItem,
    )


T = TypeVar("T", bound="EvaluateConditionalsResponse200")


@_attrs_define
class EvaluateConditionalsResponse200:
    """
    Attributes:
        process_instances (list[EvaluateConditionalsResponse200ProcessInstancesItem]): List of process instances
            created. If no root-level conditional start events evaluated to true, the list will be empty.
    """

    process_instances: list[EvaluateConditionalsResponse200ProcessInstancesItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        process_instances = []
        for process_instances_item_data in self.process_instances:
            process_instances_item = process_instances_item_data.to_dict()
            process_instances.append(process_instances_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "processInstances": process_instances,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.evaluate_conditionals_response_200_process_instances_item import (
            EvaluateConditionalsResponse200ProcessInstancesItem,
        )

        d = dict(src_dict)
        process_instances = []
        _process_instances = d.pop("processInstances")
        for process_instances_item_data in _process_instances:
            process_instances_item = (
                EvaluateConditionalsResponse200ProcessInstancesItem.from_dict(
                    process_instances_item_data
                )
            )

            process_instances.append(process_instances_item)

        evaluate_conditionals_response_200 = cls(
            process_instances=process_instances,
        )

        evaluate_conditionals_response_200.additional_properties = d
        return evaluate_conditionals_response_200

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
