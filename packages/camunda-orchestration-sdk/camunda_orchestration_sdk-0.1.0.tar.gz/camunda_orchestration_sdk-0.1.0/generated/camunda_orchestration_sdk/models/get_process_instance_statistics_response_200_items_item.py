from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetProcessInstanceStatisticsResponse200ItemsItem")


@_attrs_define
class GetProcessInstanceStatisticsResponse200ItemsItem:
    """Process element statistics response.

    Attributes:
        element_id (str | Unset): The element ID for which the results are aggregated. Example: Activity_106kosb.
        active (int | Unset): The total number of active instances of the element.
        canceled (int | Unset): The total number of canceled instances of the element.
        incidents (int | Unset): The total number of incidents for the element.
        completed (int | Unset): The total number of completed instances of the element.
    """

    element_id: ElementId | Unset = UNSET
    active: int | Unset = UNSET
    canceled: int | Unset = UNSET
    incidents: int | Unset = UNSET
    completed: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        element_id = self.element_id

        active = self.active

        canceled = self.canceled

        incidents = self.incidents

        completed = self.completed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if element_id is not UNSET:
            field_dict["elementId"] = element_id
        if active is not UNSET:
            field_dict["active"] = active
        if canceled is not UNSET:
            field_dict["canceled"] = canceled
        if incidents is not UNSET:
            field_dict["incidents"] = incidents
        if completed is not UNSET:
            field_dict["completed"] = completed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        element_id = lift_element_id(_val) if (_val := d.pop("elementId", UNSET)) is not UNSET else UNSET

        active = d.pop("active", UNSET)

        canceled = d.pop("canceled", UNSET)

        incidents = d.pop("incidents", UNSET)

        completed = d.pop("completed", UNSET)

        get_process_instance_statistics_response_200_items_item = cls(
            element_id=element_id,
            active=active,
            canceled=canceled,
            incidents=incidents,
            completed=completed,
        )

        get_process_instance_statistics_response_200_items_item.additional_properties = d
        return get_process_instance_statistics_response_200_items_item

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
