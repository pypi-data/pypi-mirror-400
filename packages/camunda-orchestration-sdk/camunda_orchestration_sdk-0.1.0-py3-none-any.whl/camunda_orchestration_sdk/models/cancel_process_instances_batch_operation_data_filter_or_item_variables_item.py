from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter


T = TypeVar(
    "T", bound="CancelProcessInstancesBatchOperationDataFilterOrItemVariablesItem"
)


@_attrs_define
class CancelProcessInstancesBatchOperationDataFilterOrItemVariablesItem:
    """
    Attributes:
        name (str): Name of the variable.
        value (ActoridAdvancedfilter | str):
    """

    name: str
    value: ActoridAdvancedfilter | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter

        name = self.name

        value: dict[str, Any] | str
        if isinstance(self.value, ActoridAdvancedfilter):
            value = self.value.to_dict()
        else:
            value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_value(data: object) -> ActoridAdvancedfilter | str:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                value_type_1 = ActoridAdvancedfilter.from_dict(data)

                return value_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str, data)

        value = _parse_value(d.pop("value"))

        cancel_process_instances_batch_operation_data_filter_or_item_variables_item = (
            cls(
                name=name,
                value=value,
            )
        )

        cancel_process_instances_batch_operation_data_filter_or_item_variables_item.additional_properties = d
        return (
            cancel_process_instances_batch_operation_data_filter_or_item_variables_item
        )

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
