from __future__ import annotations
from camunda_orchestration_sdk.semantic_types import *

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.result_object_1_activateelements_item_variables import (
        ResultObject1ActivateelementsItemVariables,
    )


T = TypeVar("T", bound="ResultObject1ActivateelementsItem")


@_attrs_define
class ResultObject1ActivateelementsItem:
    """Instruction to activate a single BPMN element within an ad‑hoc sub‑process, optionally providing variables scoped to
    that element.

        Attributes:
            element_id (str | Unset): The element ID to activate. Example: Activity_106kosb.
            variables (ResultObject1ActivateelementsItemVariables | Unset): Variables for the element.
    """

    element_id: ElementId | Unset = UNSET
    variables: ResultObject1ActivateelementsItemVariables | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        element_id = self.element_id

        variables: dict[str, Any] | Unset = UNSET
        if not isinstance(self.variables, Unset):
            variables = self.variables.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if element_id is not UNSET:
            field_dict["elementId"] = element_id
        if variables is not UNSET:
            field_dict["variables"] = variables

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.result_object_1_activateelements_item_variables import (
            ResultObject1ActivateelementsItemVariables,
        )

        d = dict(src_dict)
        element_id = lift_element_id(_val) if (_val := d.pop("elementId", UNSET)) is not UNSET else UNSET

        _variables = d.pop("variables", UNSET)
        variables: ResultObject1ActivateelementsItemVariables | Unset
        if isinstance(_variables, Unset):
            variables = UNSET
        else:
            variables = ResultObject1ActivateelementsItemVariables.from_dict(_variables)

        result_object_1_activateelements_item = cls(
            element_id=element_id,
            variables=variables,
        )

        result_object_1_activateelements_item.additional_properties = d
        return result_object_1_activateelements_item

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
