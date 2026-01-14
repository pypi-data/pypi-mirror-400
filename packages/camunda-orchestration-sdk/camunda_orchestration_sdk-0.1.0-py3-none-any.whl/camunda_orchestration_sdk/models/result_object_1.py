from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.result_object_1_activateelements_item import (
        ResultObject1ActivateelementsItem,
    )


T = TypeVar("T", bound="ResultObject1")


@_attrs_define
class ResultObject1:
    """Job result details for an ad‑hoc sub‑process, including elements to activate and flags indicating completion or
    cancellation behavior.

        Attributes:
            activate_elements (list[ResultObject1ActivateelementsItem] | Unset): Indicates which elements need to be
                activated in the ad-hoc subprocess.
            is_completion_condition_fulfilled (bool | Unset): Indicates whether the completion condition of the ad-hoc
                subprocess is fulfilled. Default: False.
            is_cancel_remaining_instances (bool | Unset): Indicates whether the remaining instances of the ad-hoc subprocess
                should be canceled. Default: False.
            type_ (str | Unset): Used to distinguish between different types of job results. Example: adHocSubProcess.
    """

    activate_elements: list[ResultObject1ActivateelementsItem] | Unset = UNSET
    is_completion_condition_fulfilled: bool | Unset = False
    is_cancel_remaining_instances: bool | Unset = False
    type_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        activate_elements: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.activate_elements, Unset):
            activate_elements = []
            for activate_elements_item_data in self.activate_elements:
                activate_elements_item = activate_elements_item_data.to_dict()
                activate_elements.append(activate_elements_item)

        is_completion_condition_fulfilled = self.is_completion_condition_fulfilled

        is_cancel_remaining_instances = self.is_cancel_remaining_instances

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if activate_elements is not UNSET:
            field_dict["activateElements"] = activate_elements
        if is_completion_condition_fulfilled is not UNSET:
            field_dict["isCompletionConditionFulfilled"] = (
                is_completion_condition_fulfilled
            )
        if is_cancel_remaining_instances is not UNSET:
            field_dict["isCancelRemainingInstances"] = is_cancel_remaining_instances
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.result_object_1_activateelements_item import (
            ResultObject1ActivateelementsItem,
        )

        d = dict(src_dict)
        _activate_elements = d.pop("activateElements", UNSET)
        activate_elements: list[ResultObject1ActivateelementsItem] | Unset = UNSET
        if _activate_elements is not UNSET:
            activate_elements = []
            for activate_elements_item_data in _activate_elements:
                activate_elements_item = ResultObject1ActivateelementsItem.from_dict(
                    activate_elements_item_data
                )

                activate_elements.append(activate_elements_item)

        is_completion_condition_fulfilled = d.pop(
            "isCompletionConditionFulfilled", UNSET
        )

        is_cancel_remaining_instances = d.pop("isCancelRemainingInstances", UNSET)

        type_ = d.pop("type", UNSET)

        result_object_1 = cls(
            activate_elements=activate_elements,
            is_completion_condition_fulfilled=is_completion_condition_fulfilled,
            is_cancel_remaining_instances=is_cancel_remaining_instances,
            type_=type_,
        )

        result_object_1.additional_properties = d
        return result_object_1

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
