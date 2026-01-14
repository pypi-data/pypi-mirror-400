from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.actorid_advancedfilter import ActoridAdvancedfilter


T = TypeVar("T", bound="SearchUserTaskVariablesDataFilter")


@_attrs_define
class SearchUserTaskVariablesDataFilter:
    """The user task variable search filters.

    Attributes:
        name (ActoridAdvancedfilter | str | Unset):
    """

    name: ActoridAdvancedfilter | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter

        name: dict[str, Any] | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        elif isinstance(self.name, ActoridAdvancedfilter):
            name = self.name.to_dict()
        else:
            name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.actorid_advancedfilter import ActoridAdvancedfilter

        d = dict(src_dict)

        def _parse_name(data: object) -> ActoridAdvancedfilter | str | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                name_type_1 = ActoridAdvancedfilter.from_dict(data)

                return name_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ActoridAdvancedfilter | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        search_user_task_variables_data_filter = cls(
            name=name,
        )

        search_user_task_variables_data_filter.additional_properties = d
        return search_user_task_variables_data_filter

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
